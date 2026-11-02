"""Regressao estatica dos scripts de bancada MicroPython (``test/mp_*.py``).

Os scripts rodam na placa e nao podem ser importados no CPython (dependem de
``machine``/``utime``). Estes testes fazem analise estatica: compilam cada
arquivo (pega erro de sintaxe antes de subir para a placa) e conferem a
cadeia de seguranca da bancada -- pinos do ESP32 iguais aos do firmware,
gates nascendo OFF, rele nascendo inativo e a ordem de desarme Q1 -> rele ->
Q2 no teste dos transistores.

Rodar::

    python -m pytest test/test_scripts_bancada.py -v
    python test/test_scripts_bancada.py          # sem pytest instalado
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
TESTES = RAIZ / "test"
COMUM = TESTES / "mp_teste_comum.py"
FIRMWARE_ESP32 = RAIZ / "firmware" / "micropython" / "estacao_ignicao_esp.py"
ESP32_BANCADA = (TESTES / "mp_teste_transistor.py", TESTES / "mp_teste_rele.py")

# Constante do modulo comum -> constante correspondente no firmware.
ESPELHO_ESP32 = {
    "PIN_ESP32_RELE_NUM": "PIN_RELE_NUM",
    "PIN_ESP32_GATE_1_NUM": "PIN_GATE_1_NUM",
    "PIN_ESP32_GATE_2_NUM": "PIN_GATE_2_NUM",
    "PIN_ESP32_BUZZER_NUM": "PIN_BUZZER_NUM",
    "PIN_ESP32_BUTTON_NUM": "PIN_BUTTON_NUM",
    "PIN_ESP32_LED_COUNT_NUM": "PIN_LED_COUNT_NUM",
    "PIN_ESP32_SDA_NUM": "PIN_I2C_SDA_NUM",
    "PIN_ESP32_SCL_NUM": "PIN_I2C_SCL_NUM",
}


# =============================================================================
#  LEITURA ESTATICA DOS FONTES
# =============================================================================

def _constantes(caminho: Path) -> dict[str, int]:
    """Atribuicoes ``NOME = <int>`` no nivel do modulo (via AST)."""
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


def _pinos_com_valor(caminho: Path) -> dict[str, object]:
    """Atribuicoes ``NOME = Pin(..., value=<valor>)`` -> NOME: valor.

    O valor volta como int (constante) ou ``("nome", ID)`` quando e uma
    constante simbolica (ex.: ``value=RELE_INACTIVE_LEVEL``).
    """
    arvore = ast.parse(caminho.read_text(encoding="utf-8"), filename=str(caminho))
    valores: dict[str, object] = {}
    for no in arvore.body:
        if not isinstance(no, ast.Assign) or not isinstance(no.value, ast.Call):
            continue
        func = no.value.func
        if not (isinstance(func, ast.Name) and func.id == "Pin"):
            continue
        if not no.targets or not isinstance(no.targets[0], ast.Name):
            continue
        valor: object = None
        for kw in no.value.keywords:
            if kw.arg != "value":
                continue
            if isinstance(kw.value, ast.Constant):
                valor = kw.value.value
            elif isinstance(kw.value, ast.Name):
                valor = ("nome", kw.value.id)
        valores[no.targets[0].id] = valor
    return valores


def _ordem_chamadas(caminho: Path, funcao: str) -> list[str]:
    """Nomes das funcoes chamadas como instrucao direta no corpo de ``funcao``."""
    arvore = ast.parse(caminho.read_text(encoding="utf-8"), filename=str(caminho))
    for no in arvore.body:
        if isinstance(no, ast.FunctionDef) and no.name == funcao:
            ordem: list[str] = []
            for stmt in no.body:
                if (
                    isinstance(stmt, ast.Expr)
                    and isinstance(stmt.value, ast.Call)
                    and isinstance(stmt.value.func, ast.Name)
                ):
                    ordem.append(stmt.value.func.id)
            return ordem
    return []


def _scripts_bancada() -> list[Path]:
    return sorted(TESTES.glob("mp_*.py"))


# =============================================================================
#  TESTES
# =============================================================================

def test_scripts_bancada_compilam():
    """Nenhum erro de sintaxe nos scripts que vao para a placa."""
    arquivos = _scripts_bancada() + [TESTES / "esp8266_main.py"]
    problemas = []
    for caminho in arquivos:
        fonte = caminho.read_text(encoding="utf-8")
        try:
            compile(fonte, str(caminho), "exec")
        except SyntaxError as exc:
            problemas.append(f"{caminho.name}:{exc.lineno}: {exc.msg}")
    assert not problemas, "erro de sintaxe nos scripts de bancada:\n" + "\n".join(problemas)


def test_mapas_esp32_espelham_o_firmware():
    """Pinos da bancada (mp_teste_comum) batem com o firmware da estacao."""
    bench = _constantes(COMUM)
    firmware = _constantes(FIRMWARE_ESP32)

    divergencias = []
    for nome_bench, nome_fw in ESPELHO_ESP32.items():
        if nome_bench not in bench:
            divergencias.append(f"{nome_bench}: ausente em {COMUM.name}")
        elif nome_fw not in firmware:
            divergencias.append(f"{nome_fw}: ausente em {FIRMWARE_ESP32.name}")
        elif bench[nome_bench] != firmware[nome_fw]:
            divergencias.append(
                f"{nome_bench}={bench[nome_bench]} != {nome_fw}={firmware[nome_fw]}"
            )
    assert not divergencias, "mapa ESP32 da bancada divergente do firmware:\n" + "\n".join(divergencias)


def test_rele_ativo_em_baixo_na_bancada():
    """O modulo SRD-05VDC e ativo em baixo tambem nos testes de bancada."""
    bench = _constantes(COMUM)
    firmware = _constantes(FIRMWARE_ESP32)
    assert firmware.get("RELE_ACTIVE_LEVEL") == 0, "firmware mudou o nivel logico do rele"
    assert bench.get("RELE_ACTIVE_LEVEL") == 0, (
        f"bancada: RELE_ACTIVE_LEVEL={bench.get('RELE_ACTIVE_LEVEL')} (esperado 0)"
    )


def test_gates_nascem_desligados_nos_testes_esp32():
    """Fail-safe: Q1/Q2 tem de inicializar em 0 (OFF) nos dois testes ESP32."""
    problemas = []
    for caminho in ESP32_BANCADA:
        valores = _pinos_com_valor(caminho)
        for gate in ("PIN_GATE_1", "PIN_GATE_2"):
            if gate not in valores:
                problemas.append(f"{caminho.name}: {gate} nao inicializado")
            elif type(valores[gate]) is not int or valores[gate] != 0:
                problemas.append(
                    f"{caminho.name}: {gate} inicializa em {valores[gate]!r} (esperado 0 = OFF)"
                )
    assert not problemas, "gate de potencia ligado por padrao:\n" + "\n".join(problemas)


def test_rele_nasce_inativo_nos_testes_esp32():
    """Fail-safe: o IN do rele tem de nascer inativo nos dois testes ESP32."""
    problemas = []
    for caminho in ESP32_BANCADA:
        valor = _pinos_com_valor(caminho).get("PIN_RELE")
        inativo = valor == ("nome", "RELE_INACTIVE_LEVEL") or (
            type(valor) is int and valor == 1
        )
        if not inativo:
            problemas.append(
                f"{caminho.name}: PIN_RELE inicializa em {valor!r} "
                "(esperado RELE_INACTIVE_LEVEL = 1)"
            )
    assert not problemas, "rele ligado por padrao:\n" + "\n".join(problemas)


def test_ordem_de_desarme_no_teste_de_transistor():
    """desligar_tudo() desarma na ordem segura: Q1 -> rele -> Q2."""
    ordem = _ordem_chamadas(TESTES / "mp_teste_transistor.py", "desligar_tudo")
    assert ordem == ["_set_gate2", "_set_rele", "_set_gate1"], (
        f"ordem de desarme inesperada: {ordem} (esperado Q1 -> rele -> Q2)"
    )


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
