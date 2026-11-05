#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera e valida a biblioteca compartilhada do projeto Ignitor.

A pasta hardware/kicad/shared/lib passa a conter TODOS os componentes das
placas (simbolos, footprints e modelos 3D), recortados apenas com o que os
tres projetos usam. As tabelas sym-lib-table/fp-lib-table dos projetos sao
regeradas apontando para ca, de modo que nada depende das bibliotecas
globais do KiCad nem de pastas pessoais fora do repositorio.

O script e idempotente: rodar de novo nao altera o resultado.

Uso:
    python extrair_biblioteca.py          # gera biblioteca + tabelas + caminhos 3D
    python extrair_biblioteca.py --check  # so verifica (nao escreve nada)

Roda com qualquer Python 3 (nao precisa do pcbnew). O caminho convencional
do repositorio usa o Python embutido do KiCad:

    & "C:\\Program Files\\KiCad\\10.0\\bin\\python.exe" -u ^
        hardware/tools/kicad/biblioteca/extrair_biblioteca.py
"""

import argparse
import re
import shutil
import sys
from pathlib import Path

# --------------------------------------------------------------------------
# Origens (maquina que gerou a biblioteca)
# --------------------------------------------------------------------------

KICAD = Path(r"C:\Program Files\KiCad\10.0")
KICAD_SYM_SRC = KICAD / "share" / "kicad" / "symbols"
KICAD_FP_SRC = KICAD / "share" / "kicad" / "footprints"
KICAD_3D_SRC = KICAD / "share" / "kicad" / "3dmodels"

EASYEDA = Path(r"C:\Users\italo\Documents\KiCad\easyeda2kicad")

THIRD = Path(r"C:\Users\italo\Documents\KiCad\10.0") / "3rdparty"
THIRD_SYM = THIRD / "symbols"
THIRD_FP = THIRD / "footprints"
THIRD_3D = THIRD / "3dmodels"

KICADBIBIS_RA02 = (Path(r"C:\Users\italo\Documents\kicadbibis") /
                   "lora-ai-thinker-sx1278-1.snapshot.2" /
                   "lora-ra-02-ai-thinker.STEP")

SL_SYM = THIRD_SYM / "com_github_Sajitha-Aldeniya_KiCad-Simple-Libraries"
SL_FP = THIRD_FP / "com_github_Sajitha-Aldeniya_KiCad-Simple-Libraries"
AKL_SYM = THIRD_SYM / "com_github_dawidcislo_alternate-kicad-library"
AKL_FP = THIRD_FP / "com_github_dawidcislo_alternate-kicad-library"
SPARKFUN_SYM = THIRD_SYM / "com_github_sparkfun_SparkFun-KiCad-Libraries"

# --------------------------------------------------------------------------
# Destino
# --------------------------------------------------------------------------

REPO = Path(__file__).resolve().parents[4]
LIB = REPO / "hardware" / "kicad" / "shared" / "lib"
MODELS_DIR = LIB / "3dmodels"

PROJECTS = [
    REPO / "hardware" / "kicad" / "placas" / "ignicao_pth",
    REPO / "hardware" / "kicad" / "placas" / "ignicao_smd",
    REPO / "hardware" / "kicad" / "placas" / "ignicao_cnc",
]


def pcb_do_projeto(projeto):
    """PCB de topo do projeto (ignora copias dentro de .history)."""
    pcbs = [p for p in sorted(projeto.glob("*.kicad_pcb"))
            if ".history" not in p.parts]
    if len(pcbs) != 1:
        raise SystemExit(f"esperava 1 .kicad_pcb em {projeto}, achei {len(pcbs)}")
    return pcbs[0]

REL_LIB = "${KIPRJMOD}/../../shared/lib"
REL_MODELS = REL_LIB + "/3dmodels"

# --------------------------------------------------------------------------
# Manifesto de simbolos: nome da lib -> (arquivo de origem, simbolos usados)
# --------------------------------------------------------------------------

SYMBOL_LIBS = {
    "Connector": (KICAD_SYM_SRC / "Connector.kicad_sym",
                  ["Screw_Terminal_01x02"]),
    "Device": (KICAD_SYM_SRC / "Device.kicad_sym",
               ["C", "D_Schottky", "D_TVS", "Fuse"]),
    "Diode": (KICAD_SYM_SRC / "Diode.kicad_sym",
              ["1N5400"]),
    "power": (KICAD_SYM_SRC / "power.kicad_sym",
              ["+3V3", "GND", "PWR_FLAG", "VCC"]),
    "Switch": (KICAD_SYM_SRC / "Switch.kicad_sym",
               ["SW_SP3T"]),
    "easyeda2kicad": (EASYEDA / "easyeda2kicad.kicad_sym",
                      ["0805W8F2200T5E", "1206W4F1002T5E", "CL31A106KBHNNNE",
                       "CL31A107MQHNNNE", "CL31B104KBCNNNC", "SS34_C8678"]),
    "PCM_SL_Capacitors": (SL_SYM / "SL_Capacitors.kicad_sym",
                          ["1000uF_16V", "100uF_16V", "10uF_16V"]),
    "PCM_SL_Connectors": (SL_SYM / "SL_Connectors.kicad_sym",
                          ["JST_02", "JST_03", "JST_04"]),
    "PCM_SL_Development_Board": (SL_SYM / "SL_Development_Board.kicad_sym",
                                 ["ESP32_DevKit_V1_DOIT_30GPIOs"]),
    "PCM_SL_Devices": (SL_SYM / "SL_Devices.kicad_sym",
                       ["LED"]),
    "PCM_SL_Pin_Headers": (SL_SYM / "SL_Pin_Headers.kicad_sym",
                           ["PINHD_1x1_Male", "PINHD_1x2_Female",
                            "PINHD_1x2_Male", "PINHD_1x3_Male"]),
    "PCM_SL_Resistors": (SL_SYM / "SL_Resistors.kicad_sym",
                         ["10k", "220ohm"]),
    "PCM_SL_Screw_Terminal": (SL_SYM / "SL_Screw_Terminal.kicad_sym",
                              ["Screw_Terminal_2_P3.50mm"]),
    "PCM_SparkFun-PowerSymbol": (SPARKFUN_SYM / "SparkFun-PowerSymbol.kicad_sym",
                                 ["VIN"]),
    "PCM_Transistor_MOSFET_AKL": (AKL_SYM / "Transistor_MOSFET_AKL.kicad_sym",
                                  ["IRLZ44N"]),
}

# Libs proprias do repositorio: nao sao regeradas, so entram nas tabelas.
SYMBOL_LIBS_KEEP = ["ignitor"]

SYMBOL_ORDER = ["ignitor"] + sorted(SYMBOL_LIBS)

# --------------------------------------------------------------------------
# Manifesto de footprints: nome da lib -> (dir de origem, arquivos usados)
# --------------------------------------------------------------------------

FOOTPRINT_LIBS = {
    "Capacitor_THT": (KICAD_FP_SRC / "Capacitor_THT.pretty",
                      ["CP_Radial_D5.0mm_P2.00mm",
                       "CP_Radial_D10.0mm_P5.00mm"]),
    "Connector_JST": (KICAD_FP_SRC / "Connector_JST.pretty",
                      ["JST_EH_B2B-EH-A_1x02_P2.50mm_Vertical",
                       "JST_EH_B3B-EH-A_1x03_P2.50mm_Vertical",
                       "JST_EH_B4B-EH-A_1x04_P2.50mm_Vertical"]),
    "Connector_PinHeader_2.54mm": (KICAD_FP_SRC / "Connector_PinHeader_2.54mm.pretty",
                                   ["PinHeader_1x01_P2.54mm_Vertical",
                                    "PinHeader_1x02_P2.54mm_Vertical",
                                    "PinHeader_1x03_P2.54mm_Vertical"]),
    "Connector_PinSocket_2.54mm": (KICAD_FP_SRC / "Connector_PinSocket_2.54mm.pretty",
                                   ["PinSocket_1x02_P2.54mm_Vertical"]),
    "Diode_THT": (KICAD_FP_SRC / "Diode_THT.pretty",
                  ["D_DO-201AD_P15.24mm_Horizontal"]),
    "LED_THT": (KICAD_FP_SRC / "LED_THT.pretty",
                ["LED_D5.0mm"]),
    "Resistor_THT": (KICAD_FP_SRC / "Resistor_THT.pretty",
                     ["R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal"]),
    "TerminalBlock_Phoenix": (KICAD_FP_SRC / "TerminalBlock_Phoenix.pretty",
                              ["TerminalBlock_Phoenix_PT-1,5-2-3.5-H_1x02_P3.50mm_Horizontal"]),
    "easyeda2kicad": (EASYEDA / "easyeda2kicad.pretty",
                      ["C1206", "R0805", "R1206", "SMA_L4.3-W2.6-LS5.2-RD"]),
    "PCM_Package_TO_SOT_THT_AKL": (AKL_FP / "Package_TO_SOT_THT_AKL.pretty",
                                   ["TO-220-3_Vertical_GDS"]),
    "PCM_SL_Development_Boards": (SL_FP / "SL_Development_Boards.pretty",
                                  ["DOIT_ESP32_DEVKIT_30Pins"]),
}

FOOTPRINT_LIBS_KEEP = ["ignitor"]

FOOTPRINT_ORDER = ["ignitor"] + sorted(FOOTPRINT_LIBS)

# --------------------------------------------------------------------------
# Manifesto de modelos 3D: (arquivo de origem, nome copiado)
# --------------------------------------------------------------------------

MODELS = []

for _nome in ["CP_Radial_D5.0mm_P2.00mm", "CP_Radial_D10.0mm_P5.00mm"]:
    MODELS.append((KICAD_3D_SRC / "Capacitor_THT.3dshapes" / (_nome + ".step"),
                   _nome + ".step"))
for _nome in ["JST_EH_B2B-EH-A_1x02_P2.50mm_Vertical",
              "JST_EH_B3B-EH-A_1x03_P2.50mm_Vertical",
              "JST_EH_B4B-EH-A_1x04_P2.50mm_Vertical"]:
    MODELS.append((KICAD_3D_SRC / "Connector_JST.3dshapes" / (_nome + ".step"),
                   _nome + ".step"))
for _nome in ["PinHeader_1x01_P2.54mm_Vertical",
              "PinHeader_1x02_P2.54mm_Vertical",
              "PinHeader_1x03_P2.54mm_Vertical"]:
    MODELS.append((KICAD_3D_SRC / "Connector_PinHeader_2.54mm.3dshapes" / (_nome + ".step"),
                   _nome + ".step"))
MODELS += [
    (KICAD_3D_SRC / "Connector_PinSocket_2.54mm.3dshapes" /
     "PinSocket_1x02_P2.54mm_Vertical.step",
     "PinSocket_1x02_P2.54mm_Vertical.step"),
    (KICAD_3D_SRC / "Diode_THT.3dshapes" /
     "D_DO-201AD_P15.24mm_Horizontal.step",
     "D_DO-201AD_P15.24mm_Horizontal.step"),
    (KICAD_3D_SRC / "LED_THT.3dshapes" / "LED_D5.0mm.step",
     "LED_D5.0mm.step"),
    (KICAD_3D_SRC / "Resistor_THT.3dshapes" /
     "R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal.step",
     "R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal.step"),
    (KICAD_3D_SRC / "TerminalBlock_Phoenix.3dshapes" /
     "TerminalBlock_Phoenix_PT-1,5-2-3.5-H_1x02_P3.50mm_Horizontal.step",
     "TerminalBlock_Phoenix_PT-1,5-2-3.5-H_1x02_P3.50mm_Horizontal.step"),
    (KICAD_3D_SRC / "Package_TO_SOT_THT.3dshapes" / "TO-220-3_Vertical.step",
     "TO-220-3_Vertical.step"),
    (KICAD_3D_SRC / "Package_TO_SOT_THT.3dshapes" / "TO-92_Inline.step",
     "TO-92_Inline.step"),
    (EASYEDA / "easyeda2kicad.3dshapes" / "C1206_L3.2-W1.6-H1.3.step",
     "C1206_L3.2-W1.6-H1.3.step"),
    (EASYEDA / "easyeda2kicad.3dshapes" / "R0805_L2.0-W1.3-H0.6.step",
     "R0805_L2.0-W1.3-H0.6.step"),
    (EASYEDA / "easyeda2kicad.3dshapes" / "R0805_L2.0-W1.3-H0.6.wrl",
     "R0805_L2.0-W1.3-H0.6.wrl"),
    (EASYEDA / "easyeda2kicad.3dshapes" / "R1206_L3.2-W1.6-H0.6.step",
     "R1206_L3.2-W1.6-H0.6.step"),
    (EASYEDA / "easyeda2kicad.3dshapes" / "SMA_L4.3-W2.6-LS5.2-RD.step",
     "SMA_L4.3-W2.6-LS5.2-RD.step"),
    (EASYEDA / "easyeda2kicad.3dshapes" / "TO-92-3_L4.9-W3.7-P1.27-L.step",
     "TO-92-3_L4.9-W3.7-P1.27-L.step"),
    (THIRD_3D / "com_github_Sajitha-Aldeniya_KiCad-Simple-Libraries" /
     "SL_Development_Boards.3dshapes" / "DOIT_ESP32_devkit_V1.wrl",
     "DOIT_ESP32_devkit_V1.wrl"),
    (KICADBIBIS_RA02, "lora-ra-02-ai-thinker.STEP"),
]

MODEL_NAMES = {nome for _src, nome in MODELS}

RA02_MODEL_NAME = "lora-ra-02-ai-thinker.STEP"


# --------------------------------------------------------------------------
# Leitura/escrita preservando o tipo de quebra de linha (LF ou CRLF)
# --------------------------------------------------------------------------

def ler_texto(caminho):
    with open(caminho, "r", encoding="utf-8", newline="") as f:
        return f.read()


def escrever_texto(caminho, texto):
    with open(caminho, "w", encoding="utf-8", newline="") as f:
        f.write(texto)


# --------------------------------------------------------------------------
# S-expression: leitura de blocos de simbolo
# --------------------------------------------------------------------------

def skip_string(text, i):
    """i aponta para a aspa de abertura; devolve o indice apos a de fechamento."""
    j = i + 1
    n = len(text)
    while j < n:
        c = text[j]
        if c == "\\":
            j += 2
            continue
        if c == '"':
            return j + 1
        j += 1
    raise ValueError("string sem terminador")


def match_paren(text, i):
    """i aponta para '('; devolve o indice do ')' correspondente."""
    depth = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c == '"':
            i = skip_string(text, i)
            continue
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return i
        i += 1
    raise ValueError("parenteses desbalanceados")


SYMBOL_RE = re.compile(r'\(\s*symbol\s+"((?:[^"\\]|\\.)*)"')
EXTENDS_RE = re.compile(r'\(extends\s+"((?:[^"\\]|\\.)*)"')


def scan_lib(text):
    """Mapa nome -> (inicio, fim) dos simbolos de nivel 1 de um .kicad_sym."""
    spans = {}
    i = 0
    depth = 0
    n = len(text)
    while i < n:
        c = text[i]
        if c == '"':
            i = skip_string(text, i)
            continue
        if c == "(":
            depth += 1
            if depth == 2:
                m = SYMBOL_RE.match(text, i)
                if m:
                    end = match_paren(text, i)
                    spans[m.group(1)] = (i, end + 1)
                    i = end + 1
                    depth -= 1
                    continue
            i += 1
            continue
        if c == ")":
            depth -= 1
        i += 1
    return spans


def newline_of(text):
    return "\r\n" if "\r\n" in text else "\n"


def extract_lib_text(src_path, wanted):
    """Monta o .kicad_sym recortado com os simbolos pedidos (+ bases extends)."""
    text = ler_texto(src_path)
    spans = scan_lib(text)
    if not spans:
        raise ValueError(f"nenhum simbolo encontrado em {src_path}")

    todo = set(wanted)
    while True:
        faltando = todo - set(spans)
        if not faltando:
            break
        raise ValueError(
            f"simbolo(s) nao encontrado(s) em {src_path}: "
            + ", ".join(sorted(faltando)))

    # simbolos derivados precisam da base junto
    extra = set()
    for nome in list(todo):
        bloco = text[spans[nome][0]:spans[nome][1]]
        m = EXTENDS_RE.search(bloco)
        if m:
            base = m.group(1)
            if base not in spans:
                raise ValueError(f"base '{base}' de '{nome}' nao existe em {src_path}")
            if base not in todo:
                extra.add(base)
    if extra:
        todo |= extra
        print(f"    + bases extends: {', '.join(sorted(extra))}")

    primeiro = min(inicio for inicio, _fim in spans.values())
    header = text[:primeiro]
    nl = newline_of(text)
    ordenados = sorted(((text[a:b], a) for nome, (a, b) in spans.items()
                        if nome in todo))
    corpo = (nl + "\t").join(bloco for bloco, _a in ordenados)
    return header + corpo + nl + ")" + nl


def resolver_modelo(nome, preferir_step):
    """Nome local do modelo; normaliza .wrl -> .step quando pedido."""
    if preferir_step and nome.endswith(".wrl"):
        alternativa = nome[:-4] + ".step"
        if alternativa in MODEL_NAMES:
            return alternativa
    if nome in MODEL_NAMES:
        return nome
    if nome.endswith(".wrl") and nome[:-4] + ".step" in MODEL_NAMES:
        return nome[:-4] + ".step"
    return None


MODEL_DECL_RE = re.compile(r'\(model\s+"((?:[^"\\]|\\.)*)"')


def corrigir_modelos_texto(text, preferir_step):
    """Troca os caminhos das declaracoes (model ...) por caminhos locais."""
    def repl(m):
        caminho = m.group(1)
        if caminho.startswith("${KIPRJMOD}/"):
            return m.group(0)
        nome = Path(caminho.replace("\\", "/")).name
        local = resolver_modelo(nome, preferir_step)
        if local is None:
            raise ValueError(f"modelo sem copia local: {caminho}")
        return '(model "%s/%s"' % (REL_MODELS, local)
    return MODEL_DECL_RE.sub(repl, text)


# --------------------------------------------------------------------------
# Geracao
# --------------------------------------------------------------------------

def gerar_simbolos():
    print("== simbolos")
    for nome in sorted(SYMBOL_LIBS):
        origem, usados = SYMBOL_LIBS[nome]
        if not origem.exists():
            raise FileNotFoundError(origem)
        texto = extract_lib_text(origem, usados)
        destino = LIB / f"{nome}.kicad_sym"
        LIB.mkdir(parents=True, exist_ok=True)
        escrever_texto(destino, texto)
        print(f"    {nome}.kicad_sym <- {origem.name} "
              f"({len(usados)} simbolos)")


def gerar_footprints():
    print("== footprints")
    for nome in sorted(FOOTPRINT_LIBS):
        origem_dir, arquivos = FOOTPRINT_LIBS[nome]
        destino_dir = LIB / f"{nome}.pretty"
        destino_dir.mkdir(parents=True, exist_ok=True)
        for arquivo in list(destino_dir.glob("*.kicad_mod")):
            arquivo.unlink()
        for arquivo in arquivos:
            src = origem_dir / f"{arquivo}.kicad_mod"
            if not src.exists():
                raise FileNotFoundError(src)
            texto = ler_texto(src)
            texto = corrigir_modelos_texto(texto, preferir_step=True)
            escrever_texto(destino_dir / f"{arquivo}.kicad_mod", texto)
        print(f"    {nome}.pretty ({len(arquivos)} footprints)")


def gerar_modelos():
    print("== modelos 3D")
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    for origem, nome in MODELS:
        if not origem.exists():
            raise FileNotFoundError(origem)
        shutil.copyfile(origem, MODELS_DIR / nome)
        print(f"    {nome}")


def gerar_tabelas():
    print("== tabelas")
    linhas_sym = ["(sym_lib_table", "  (version 7)", ""]
    for nome in SYMBOL_ORDER:
        linhas_sym.append(
            f'  (lib (name "{nome}") (type "KiCad") '
            f'(uri "{REL_LIB}/{nome}.kicad_sym") (options "") '
            f'(descr "Biblioteca local do projeto Ignitor"))')
    linhas_sym.append(")")
    conteudo_sym = "\n".join(linhas_sym) + "\n"

    linhas_fp = ["(fp_lib_table", "  (version 7)", ""]
    for nome in FOOTPRINT_ORDER:
        linhas_fp.append(
            f'  (lib (name "{nome}") (type "KiCad") '
            f'(uri "{REL_LIB}/{nome}.pretty") (options "") '
            f'(descr "Biblioteca local do projeto Ignitor"))')
    linhas_fp.append(")")
    conteudo_fp = "\n".join(linhas_fp) + "\n"

    for projeto in PROJECTS:
        escrever_texto(projeto / "sym-lib-table", conteudo_sym)
        escrever_texto(projeto / "fp-lib-table", conteudo_fp)
        print(f"    {projeto.parent.name}/{projeto.name}/sym-lib-table")
        print(f"    {projeto.parent.name}/{projeto.name}/fp-lib-table")


def bloco_modelo_ra02(nivel, nl):
    """Bloco (model ...) do RA-02 com nivel tabs na linha do (model."""
    linhas = [
        (0, f'(model "{REL_MODELS}/{RA02_MODEL_NAME}"'),
        (1, "(offset"),
        (2, "(xyz 0 0 0)"),
        (1, ")"),
        (1, "(scale"),
        (2, "(xyz 1 1 1)"),
        (1, ")"),
        (1, "(rotate"),
        (2, "(xyz -90 -0 -0)"),
        (1, ")"),
        (0, ")"),
    ]
    return nl.join("\t" * (nivel + d) + txt for d, txt in linhas)


def inserir_modelo_antes_do_fechamento(texto, idx_fecha, nivel, nl):
    """Insere o bloco de modelo na linha anterior ao ')' em idx_fecha."""
    inicio_linha = texto.rfind(nl, 0, idx_fecha)
    if inicio_linha == -1:
        raise ValueError("nao achei a linha de fechamento")
    inicio_linha += len(nl)
    bloco = bloco_modelo_ra02(nivel, nl) + nl
    return texto[:inicio_linha] + bloco + texto[inicio_linha:]


def corrigir_pcbs():
    print("== pcbs (caminhos 3D)")
    for projeto in PROJECTS:
        pcb = pcb_do_projeto(projeto)
        texto = ler_texto(pcb)
        antes = texto
        texto = corrigir_modelos_texto(texto, preferir_step=False)

        if 'footprint "ignitor:RA-02_THT"' in texto and \
                RA02_MODEL_NAME not in texto:
            marcador = '(footprint "ignitor:RA-02_THT"'
            inicio = texto.index(marcador)
            fim = match_paren(texto, inicio)
            nl = newline_of(texto)
            texto = inserir_modelo_antes_do_fechamento(texto, fim, 2, nl)
            print(f"    {pcb.parent.name}: modelo do RA-02 adicionado")

        if texto != antes:
            escrever_texto(pcb, texto)
            print(f"    {pcb.parent.name}/{pcb.name}: caminhos corrigidos")
        else:
            print(f"    {pcb.parent.name}/{pcb.name}: ja estava local")

    print("== ignitor.pretty (modelo do RA-02)")
    for nome in ["RA-02.kicad_mod", "RA-02_THT.kicad_mod"]:
        caminho = LIB / "ignitor.pretty" / nome
        texto = ler_texto(caminho)
        if RA02_MODEL_NAME in texto:
            print(f"    {nome}: ja tem modelo")
            continue
        nl = newline_of(texto)
        fecha = texto.rfind(nl + ")")
        if fecha == -1:
            raise ValueError(f"final inesperado em {nome}")
        bloco = bloco_modelo_ra02(1, nl) + nl
        texto = texto[:fecha + len(nl)] + bloco + texto[fecha + len(nl):]
        escrever_texto(caminho, texto)
        print(f"    {nome}: modelo adicionado")


# --------------------------------------------------------------------------
# Verificacao
# --------------------------------------------------------------------------

LIB_RE = re.compile(r'\(lib \(name "([^"]+)"\) \(type "KiCad"\) '
                    r'\(uri "([^"]+)"\)')
LIB_ID_RE = re.compile(r'\(lib_id "([^"]+)"')
FP_PROP_RE = re.compile(r'\(property "Footprint" "([^"]+)"')
PCB_FP_RE = re.compile(r'^\t\(footprint "([^"]+)"', re.MULTILINE)


class Falhas:
    def __init__(self):
        self.lista = []

    def add(self, msg):
        self.lista.append(msg)
        print(f"    FALHA: {msg}")


def ler_tabela(caminho, projeto, falhas):
    tabela = {}
    if not caminho.exists():
        falhas.add(f"{caminho.name} nao existe em {projeto.name}")
        return tabela
    texto = ler_texto(caminho)
    for nome, uri in LIB_RE.findall(texto):
        resolvido = Path(uri.replace("${KIPRJMOD}", str(projeto)))
        tabela[nome] = resolvido
    return tabela


def checar():
    print("== --check")
    falhas = Falhas()

    print("-- arquivos da biblioteca")
    for nome in SYMBOL_LIBS:
        if not (LIB / f"{nome}.kicad_sym").exists():
            falhas.add(f"{nome}.kicad_sym ausente")
    for nome in SYMBOL_LIBS_KEEP:
        if not (LIB / f"{nome}.kicad_sym").exists():
            falhas.add(f"{nome}.kicad_sym ausente")
    for nome in FOOTPRINT_LIBS:
        if not (LIB / f"{nome}.pretty").is_dir():
            falhas.add(f"{nome}.pretty ausente")
    for nome in FOOTPRINT_LIBS_KEEP:
        if not (LIB / f"{nome}.pretty").is_dir():
            falhas.add(f"{nome}.pretty ausente")
    for nome in MODEL_NAMES:
        if not (MODELS_DIR / nome).exists():
            falhas.add(f"3dmodels/{nome} ausente")

    simbolos_por_lib = {}
    for nome in SYMBOL_ORDER:
        caminho = LIB / f"{nome}.kicad_sym"
        if caminho.exists():
            simbolos_por_lib[nome] = set(scan_lib(ler_texto(caminho)))

    for projeto in PROJECTS:
        print(f"-- {projeto.parent.name}/{projeto.name}")
        sym_tab = ler_tabela(projeto / "sym-lib-table", projeto, falhas)
        fp_tab = ler_tabela(projeto / "fp-lib-table", projeto, falhas)

        for nome in SYMBOL_ORDER:
            if nome not in sym_tab:
                falhas.add(f"sym-lib-table sem '{nome}'")
        for nome in FOOTPRINT_ORDER:
            if nome not in fp_tab:
                falhas.add(f"fp-lib-table sem '{nome}'")

        for arquivo in sorted(projeto.rglob("*.kicad_sch")):
            if ".history" in arquivo.parts:
                continue
            texto = ler_texto(arquivo)
            for lib_id in LIB_ID_RE.findall(texto):
                lib, _, simbolo = lib_id.partition(":")
                if lib not in sym_tab:
                    faltas = f"'{lib}' fora do sym-lib-table"
                    falhas.add(f"{arquivo.name}: {lib_id} ({faltas})")
                    continue
                if not sym_tab[lib].exists():
                    falhas.add(f"{arquivo.name}: {lib_id} "
                               f"(arquivo {sym_tab[lib].name} inexistente)")
                    continue
                if simbolo not in simbolos_por_lib.get(lib, set()):
                    falhas.add(f"{arquivo.name}: {lib_id} ausente no recorte")
            for fp in FP_PROP_RE.findall(texto):
                if not fp:
                    continue
                lib, _, nome_fp = fp.partition(":")
                if lib not in fp_tab:
                    falhas.add(f"{arquivo.name}: {fp} (lib fora da tabela)")
                    continue
                if not (fp_tab[lib] / f"{nome_fp}.kicad_mod").exists():
                    falhas.add(f"{arquivo.name}: {fp} sem .kicad_mod local")

        for pcb in sorted(projeto.rglob("*.kicad_pcb")):
            if ".history" in pcb.parts:
                continue
            texto = ler_texto(pcb)
            for fp in PCB_FP_RE.findall(texto):
                lib, _, nome_fp = fp.partition(":")
                if lib not in fp_tab:
                    falhas.add(f"{pcb.name}: {fp} (lib fora da tabela)")
                    continue
                if not (fp_tab[lib] / f"{nome_fp}.kicad_mod").exists():
                    falhas.add(f"{pcb.name}: {fp} sem .kicad_mod local")
            for caminho in MODEL_DECL_RE.findall(texto):
                if not caminho.startswith("${KIPRJMOD}/"):
                    falhas.add(f"{pcb.name}: modelo nao-local {caminho}")
                    continue
                nome = Path(caminho.replace("\\", "/")).name
                if nome not in MODEL_NAMES:
                    falhas.add(f"{pcb.name}: modelo sem copia {nome}")
                relativo = caminho.replace("${KIPRJMOD}/", "")
                if not (projeto / relativo).resolve().exists():
                    falhas.add(f"{pcb.name}: caminho 3D quebrado {caminho}")

        if projeto.name in ("ignicao_pth", "ignicao_cnc"):
            texto = ler_texto(pcb_do_projeto(projeto))
            if "ignitor:RA-02_THT" in texto and RA02_MODEL_NAME not in texto:
                falhas.add(f"RA-02_THT da PCB {projeto.name} sem modelo 3D")

    print("-- footprints das bibliotecas locais (modelos)")
    for lib_dir in [LIB / f"{nome}.pretty" for nome in FOOTPRINT_ORDER]:
        for arquivo in lib_dir.glob("*.kicad_mod"):
            texto = ler_texto(arquivo)
            for caminho in MODEL_DECL_RE.findall(texto):
                if not caminho.startswith("${KIPRJMOD}/"):
                    falhas.add(f"{arquivo.name}: modelo nao-local {caminho}")
                    continue
                nome = Path(caminho.replace("\\", "/")).name
                if nome not in MODEL_NAMES:
                    falhas.add(f"{arquivo.name}: modelo sem copia {nome}")

    if falhas.lista:
        print(f"\n{len(falhas.lista)} falha(s)")
        return 1
    print("\nOK: simbolos, footprints e modelos 3D resolvem localmente.")
    return 0


# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="somente verifica, sem escrever nada")
    args = ap.parse_args()

    if args.check:
        return checar()

    LIB.mkdir(parents=True, exist_ok=True)
    gerar_simbolos()
    gerar_footprints()
    gerar_modelos()
    corrigir_pcbs()
    gerar_tabelas()
    print("\nBiblioteca gerada em", LIB)
    return 0


if __name__ == "__main__":
    sys.exit(main())
