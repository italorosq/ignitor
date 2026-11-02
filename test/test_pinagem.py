"""Regressao de pinagem e parametros de seguranca do firmware.

Os scripts em ``firmware/micropython/`` rodam em MicroPython e nao podem ser
importados no CPython (dependem de ``machine``/``utime``). Estes testes fazem
analise estatica do fonte: compilam o arquivo (pega erro de sintaxe) e
comparam as constantes de pino com o mapa oficial do projeto.

Motivacao: o historico tem dois commits "alinha pinagem ao hardware revisado",
ou seja, codigo e documentacao divergindo do netlist. Um teste que compara
constante de pino x mapa esperado x docstring pega essa deriva antes do
hardware ser energizado.

Rodar::

    python -m pytest test/test_pinagem.py -v
    python test/test_pinagem.py          # sem pytest instalado
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FW = RAIZ / "firmware" / "micropython"

ESP32 = FW / "estacao_ignicao_esp.py"
PICO_IGNICAO = FW / "estacao_ignicao.py"
PICO_COMANDO = FW / "estacao_comando.py"

FIRMWARES = (ESP32, PICO_IGNICAO, PICO_COMANDO)


# =============================================================================
#  LEITURA ESTATICA DOS FONTES
# =============================================================================

def _constantes(caminho: Path) -> dict[str, int]:
    """Atribuicoes ``NOME = <int>`` no nivel do modulo (via AST).

    Ignora ``bool`` (que em Python e subclasse de ``int``) e expressoes
    derivadas, como ``X = 0 if Y else 1``.
    """
    arvore = ast.parse(caminho.read_text(encoding="utf-8"), filename=str(caminho))
    valores: dict[str, int] = {}
    for no in arvore.body:
        if not isinstance(no, ast.Assign):
            continue
        if not isinstance(no.value, ast.Constant) or type(no.value.value) is not int:
            continue
        for alvo in no.targets:
            if isinstance(alvo, ast.Name):
                valores[alvo.id] = no.value.value
    return valores


def _constantes_texto(caminho: Path) -> dict[str, str]:
    """Atribuicoes ``NOME = "texto"`` no nivel do modulo (via AST)."""
    arvore = ast.parse(caminho.read_text(encoding="utf-8"), filename=str(caminho))
    valores: dict[str, str] = {}
    for no in arvore.body:
        if not isinstance(no, ast.Assign):
            continue
        if not isinstance(no.value, ast.Constant) or not isinstance(no.value.value, str):
            continue
        for alvo in no.targets:
            if isinstance(alvo, ast.Name):
                valores[alvo.id] = no.value.value
    return valores


def _pinos_diretos(caminho: Path) -> dict[str, int]:
    """Atribuicoes ``NOME = Pin(<int>, ...)`` -> NOME: numero do pino."""
    arvore = ast.parse(caminho.read_text(encoding="utf-8"), filename=str(caminho))
    valores: dict[str, int] = {}
    for no in arvore.body:
        if not isinstance(no, ast.Assign) or not isinstance(no.value, ast.Call):
            continue
        func = no.value.func
        if not (isinstance(func, ast.Name) and func.id == "Pin"):
            continue
        if not no.value.args:
            continue
        primeiro = no.value.args[0]
        if isinstance(primeiro, ast.Constant) and type(primeiro.value) is int:
            for alvo in no.targets:
                if isinstance(alvo, ast.Name):
                    valores[alvo.id] = primeiro.value
    return valores


def _mapa_docstring(caminho: Path) -> dict[str, int]:
    """Pares ``ROTULO=GPIO<n>`` do bloco de comentario no topo do arquivo."""
    linhas: list[str] = []
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        if linha.startswith("#"):
            linhas.append(linha)
        elif linhas:
            break
    bloco = "\n".join(linhas)
    return {
        m.group(1): int(m.group(2))
        for m in re.finditer(r"([A-Za-z_][A-Za-z0-9_()]*)=GPIO(\d+)", bloco)
    }


# =============================================================================
#  MAPA OFICIAL DO PROJETO
# =============================================================================
#  ESP32 DevKit V1, 30 pinos (ESP32-WROOM-32) -- MCU atual da estacao de ignicao.
#  Fonte: cabecalho de estacao_ignicao_esp.py e hardware/README.md.
MAPA_ESP32 = {
    # LoRa (SPI/VSPI de hardware)
    "SPI_SCK": 18,
    "SPI_MOSI": 23,
    "SPI_MISO": 19,
    "PIN_LORA_CS_NUM": 4,
    "PIN_LORA_RESET_NUM": 16,
    "PIN_LORA_DIO0_NUM": 17,
    # Atuador e chaves de potencia (MOSFET IRLZ44N, gate ativo em ALTO)
    "PIN_RELE_NUM": 32,
    "PIN_GATE_1_NUM": 13,
    "PIN_GATE_2_NUM": 33,
    "PIN_BUZZER_NUM": 14,
    "PIN_STATUS_NUM": 25,
    "PIN_BUTTON_NUM": 27,
    # Entradas (expansao e ADC1 -- somente entrada, sem pull interno)
    "PIN_EXP_A_NUM": 2,
    "PIN_EXP_B_NUM": 5,
    "PIN_EXP_C_NUM": 15,
    "PIN_ADC1_IN1_NUM": 34,
    "PIN_ADC1_IN2_NUM": 35,
    # I2C do OLED de status
    "PIN_I2C_SDA_NUM": 21,
    "PIN_I2C_SCL_NUM": 22,
}

# Constantes opcionais: so sao conferidas quando presentes no firmware.
MAPA_ESP32_OPCIONAL = {"PIN_LED_BTN_NUM": 26}

# Rotulo usado no cabecalho do arquivo -> constante correspondente.
ROTULOS_ESP32 = {
    "SCK": "SPI_SCK",
    "MOSI": "SPI_MOSI",
    "MISO": "SPI_MISO",
    "CS(NSS)": "PIN_LORA_CS_NUM",
    "RESET": "PIN_LORA_RESET_NUM",
    "DIO0": "PIN_LORA_DIO0_NUM",
    "RELE": "PIN_RELE_NUM",
    "GATE_1": "PIN_GATE_1_NUM",
    "GATE_2": "PIN_GATE_2_NUM",
    "BUZZER": "PIN_BUZZER_NUM",
    "STATUS_LED": "PIN_STATUS_NUM",
    "LED_BTN": "PIN_LED_BTN_NUM",
    "BUTTON_IN": "PIN_BUTTON_NUM",
    "EXP_A": "PIN_EXP_A_NUM",
    "EXP_B": "PIN_EXP_B_NUM",
    "EXP_C": "PIN_EXP_C_NUM",
    "ADC1_IN1": "PIN_ADC1_IN1_NUM",
    "ADC1_IN2": "PIN_ADC1_IN2_NUM",
    "SDA": "PIN_I2C_SDA_NUM",
    "SCL": "PIN_I2C_SCL_NUM",
}

# Raspberry Pi Pico (RP2040) -- variante THT rev 1.3.
# Fonte: hardware/README.md ("Estacao de Ignicao - Raspberry Pi Pico").
MAPA_PICO_IGNICAO = {
    "SPI_MISO": 0,
    "SPI_SCK": 2,
    "SPI_MOSI": 3,
    "SPI_DIO0": 21,
    "LORA_CS": 1,
    "LORA_RESET": 4,
    "PIN_RELE": 26,
    "PIN_BUZZER": 19,
    "PIN_LED_VERMELHO": 12,
    "PIN_LED_AMARELO": 11,
    "PIN_LED_LINK": 25,
    "PIN_LED_BTN_NUM": 16,
}

# Raspberry Pi Pico -- estacao de comando.
MAPA_PICO_COMANDO = {
    "PIN_MISO": 0,
    "PIN_SCK": 2,
    "PIN_MOSI": 3,
    "PIN_CS": 1,
    "PIN_RESET": 4,
    "PIN_DIO0": 15,
    "PIN_LED_YELLOW": 11,
    "PIN_LED_RED": 12,
    "PIN_BUZZER": 19,
    "PIN_BUTTON": 13,
    "PIN_LED_LINK": 25,
}

# Regras de seguranca: valor canonico em ms, compartilhado pelas duas estacoes
# de ignicao e citado em prosa no README.
SEGURANCA_MS = {
    "TEMPO_CONTAGEM_MS": 5000,
    "TEMPO_IGNICAO_MS": 2000,
    "TIMEOUT_SINAL_MS": 500,
}

# Protocolo LoRa: as tres estacoes precisam falar a mesma lingua.
PROTOCOLO = {
    "MSG_ARM": "ARM_CONFIRMED",
    "MSG_ABORT": "ABORT",
    "MSG_ACK": "ACK",
    "MSG_DONE": "IGNITION_COMPLETE",
}


# =============================================================================
#  TESTES
# =============================================================================

def test_firmwares_compilam():
    """Nenhum erro de sintaxe nos scripts que vao para a placa."""
    problemas = []
    for caminho in FIRMWARES:
        fonte = caminho.read_text(encoding="utf-8")
        try:
            compile(fonte, str(caminho), "exec")
        except SyntaxError as exc:
            problemas.append(f"{caminho.name}:{exc.lineno}: {exc.msg}")
    assert not problemas, "erro de sintaxe no firmware:\n" + "\n".join(problemas)


def test_pinagem_esp32():
    """Constantes de pino do ESP32 DevKit V1 batem com o mapa oficial."""
    consts = _constantes(ESP32)
    divergencias = [
        f"{nome}: firmware={consts.get(nome, 'ausente')} esperado={esperado}"
        for nome, esperado in {**MAPA_ESP32, **MAPA_ESP32_OPCIONAL}.items()
        if nome in consts and consts[nome] != esperado
    ]
    assert not divergencias, "pinagem ESP32 divergente:\n" + "\n".join(divergencias)

    faltando = [n for n in MAPA_ESP32 if n not in consts]
    assert not faltando, f"constantes de pino obrigatorias ausentes: {faltando}"


def test_docstring_esp32_bate_com_codigo():
    """O mapa comentado no topo do arquivo reflete as constantes reais."""
    consts = _constantes(ESP32)
    documentado = _mapa_docstring(ESP32)

    divergencias = []
    for rotulo, nome in ROTULOS_ESP32.items():
        if nome not in consts:
            continue  # constante ainda nao existe nesta versao do firmware
        if rotulo not in documentado:
            divergencias.append(f"{rotulo}: ausente no cabecalho (codigo={consts[nome]})")
        elif documentado[rotulo] != consts[nome]:
            divergencias.append(
                f"{rotulo}: cabecalho=GPIO{documentado[rotulo]} codigo=GPIO{consts[nome]}"
            )
    assert not divergencias, "cabecalho do ESP32 divergente do codigo:\n" + "\n".join(divergencias)


def test_pinagem_pico_ignicao():
    """Pinagem da ignicao THT (Pico, rev 1.3) bate com o mapa oficial."""
    consts = {**_constantes(PICO_IGNICAO), **_pinos_diretos(PICO_IGNICAO)}
    divergencias = [
        f"{nome}: firmware={consts.get(nome, 'ausente')} esperado={esperado}"
        for nome, esperado in MAPA_PICO_IGNICAO.items()
        if nome in consts and consts[nome] != esperado
    ]
    assert not divergencias, "pinagem do Pico (ignicao) divergente:\n" + "\n".join(divergencias)

    faltando = [n for n in MAPA_PICO_IGNICAO if n not in consts]
    assert not faltando, f"constantes de pino obrigatorias ausentes: {faltando}"


def test_pinagem_pico_comando():
    """Pinagem da estacao de comando (Pico) bate com o mapa oficial."""
    consts = _constantes(PICO_COMANDO)
    divergencias = [
        f"{nome}: firmware={consts.get(nome, 'ausente')} esperado={esperado}"
        for nome, esperado in MAPA_PICO_COMANDO.items()
        if nome in consts and consts[nome] != esperado
    ]
    assert not divergencias, "pinagem do Pico (comando) divergente:\n" + "\n".join(divergencias)

    faltando = [n for n in MAPA_PICO_COMANDO if n not in consts]
    assert not faltando, f"constantes de pino obrigatorias ausentes: {faltando}"


def test_tempos_de_seguranca():
    """Contagem, tempo de rele e timeout de sinal iguais nas duas ignicoes."""
    problemas = []
    for caminho in (ESP32, PICO_IGNICAO):
        consts = _constantes(caminho)
        for nome, esperado in SEGURANCA_MS.items():
            if nome not in consts:
                problemas.append(f"{caminho.name}: {nome} ausente")
            elif consts[nome] != esperado:
                problemas.append(
                    f"{caminho.name}: {nome}={consts[nome]} esperado={esperado}"
                )
    assert not problemas, "tempos de seguranca divergentes:\n" + "\n".join(problemas)


def test_readme_documenta_os_tempos_de_seguranca():
    """O README cita os mesmos tempos que o firmware aplica."""
    texto = (RAIZ / "README.md").read_text(encoding="utf-8")
    esperado = {
        "TEMPO_CONTAGEM_MS": "5 s",
        "TEMPO_IGNICAO_MS": "2 s",
        "TIMEOUT_SINAL_MS": "500 ms",
    }
    ausentes = [f"{nome} ({valor})" for nome, valor in esperado.items() if valor not in texto]
    assert not ausentes, f"README nao cita: {ausentes}"


def test_protocolo_lora_consistente():
    """ARM/ABORT/ACK/DONE identicos em comando, ignicao Pico e ignicao ESP32."""
    problemas = []
    for caminho in FIRMWARES:
        consts = _constantes_texto(caminho)
        for nome, valor in PROTOCOLO.items():
            if nome not in consts:
                problemas.append(f"{caminho.name}: {nome} ausente")
            elif consts[nome] != valor:
                problemas.append(f"{caminho.name}: {nome}={consts[nome]!r} esperado={valor!r}")
    assert not problemas, "protocolo LoRa divergente entre estacoes:\n" + "\n".join(problemas)


def test_acionamento_do_rele_e_ativo_em_baixo():
    """Rele SRD-05VDC e ativo em baixo nas duas estacoes de ignicao."""
    problemas = []
    for caminho in (ESP32, PICO_IGNICAO):
        consts = _constantes(caminho)
        if consts.get("RELE_ACTIVE_LEVEL") != 0:
            problemas.append(f"{caminho.name}: RELE_ACTIVE_LEVEL={consts.get('RELE_ACTIVE_LEVEL')}")
    assert not problemas, "nivel logico do rele mudou:\n" + "\n".join(problemas)


def test_gates_de_potencia_nascem_desligados():
    """Fail-safe: os gates dos MOSFETs precisam inicializar em 0 (OFF).

    O gate do IRLZ44N e ativo em ALTO. Se o firmware nascer com o gate em 1,
    o ignitor fecha junto com a energizacao. Os pull-downs de 10k (R2/R3) no
    esquema cobrem o intervalo antes do firmware rodar; esta checagem cobre o
    instante seguinte, quando o GPIO ja e saida.
    """
    arvore = ast.parse(ESP32.read_text(encoding="utf-8"), filename=str(ESP32))
    valores: dict[str, object] = {}
    for no in arvore.body:
        if not isinstance(no, ast.Assign) or not isinstance(no.value, ast.Call):
            continue
        func = no.value.func
        if not (isinstance(func, ast.Name) and func.id == "Pin"):
            continue
        if not no.targets or not isinstance(no.targets[0], ast.Name):
            continue
        for kw in no.value.keywords:
            if kw.arg == "value" and isinstance(kw.value, ast.Constant):
                valores[no.targets[0].id] = kw.value.value

    problemas = [
        f"{gate} inicializa em {valores.get(gate)!r} (esperado 0 = OFF)"
        for gate in ("PIN_GATE_1", "PIN_GATE_2")
        if valores.get(gate) != 0
    ]
    assert not problemas, "gate de potencia ligado por padrao:\n" + "\n".join(problemas)


# =============================================================================
#  RUNNER SEM PYTEST
# =============================================================================

def _main() -> int:
    testes = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    falhas = 0
    for teste in testes:
        try:
            teste()
        except AssertionError as exc:
            falhas += 1
            print(f"FALHOU  {teste.__name__}\n{exc}\n")
        else:
            print(f"ok      {teste.__name__}")
    print(f"\n{len(testes) - falhas}/{len(testes)} testes passaram")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(_main())
