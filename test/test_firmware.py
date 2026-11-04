"""Conferencias estaticas dos firmwares e dos scripts de bancada.

Roda no PC, sem placa:

    python -m pytest test/ -q
    python test/test_firmware.py
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FW = RAIZ / "firmware" / "micropython"
BANCADA = RAIZ / "test" / "bancada"

IGNICAO = FW / "estacao_ignicao_esp.py"
COMANDO = FW / "estacao_comando_esp.py"
FIRMWARES = (IGNICAO, COMANDO)

MAPA_IGNICAO = {
    "SPI_SCK": 18,
    "SPI_MOSI": 23,
    "SPI_MISO": 19,
    "PIN_LORA_CS_NUM": 4,
    "PIN_LORA_RESET_NUM": 16,
    "PIN_LORA_DIO0_NUM": 17,
    "PIN_RELE_NUM": 32,
    "PIN_GATE_1_NUM": 13,
    "PIN_GATE_2_NUM": 33,
    "PIN_BUZZER_NUM": 14,
    "PIN_STATUS_NUM": 25,
    "PIN_LED_COUNT_NUM": 12,
}

MAPA_COMANDO = {
    "PIN_SCK": 18,
    "PIN_MOSI": 23,
    "PIN_MISO": 19,
    "PIN_CS": 4,
    "PIN_RESET": 16,
    "PIN_DIO0": 17,
    "PIN_LED_YELLOW": 25,
    "PIN_LED_RED": 12,
    "PIN_LED_LINK": 26,
    "PIN_BUZZER": 14,
    "PIN_BUTTON": 27,
    "PIN_I2C_SDA": 21,
    "PIN_I2C_SCL": 22,
}

PROIBIDOS_IGNICAO = (
    "PIN_BUTTON", "PIN_LED_BTN", "PIN_I2C_SDA", "PIN_I2C_SCL",
    "PIN_EXP_A", "PIN_EXP_B", "PIN_EXP_C",
    "PIN_ADC1_IN1", "PIN_ADC1_IN2", "OLED_ADDR",
)

PROIBIDOS_COMANDO = (
    "PIN_RELE", "PIN_GATE_1", "PIN_GATE_2",
    "PIN_EXP_A", "PIN_EXP_B", "PIN_EXP_C",
    "PIN_ADC1_IN1", "PIN_ADC1_IN2",
)

ESPELHO_BANCADA = {
    "PIN_ESP32_RELE_NUM": "PIN_RELE_NUM",
    "PIN_ESP32_GATE_1_NUM": "PIN_GATE_1_NUM",
    "PIN_ESP32_GATE_2_NUM": "PIN_GATE_2_NUM",
    "PIN_ESP32_BUZZER_NUM": "PIN_BUZZER_NUM",
    "PIN_ESP32_LED_COUNT_NUM": "PIN_LED_COUNT_NUM",
}


def _constantes(caminho: Path) -> dict[str, int]:
    arvore = ast.parse(caminho.read_text(encoding="utf-8"), filename=str(caminho))
    valores = {}
    for no in arvore.body:
        if not isinstance(no, ast.Assign):
            continue
        if not isinstance(no.value, ast.Constant) or type(no.value.value) is not int:
            continue
        for alvo in no.targets:
            if isinstance(alvo, ast.Name):
                valores[alvo.id] = no.value.value
    return valores


def _textos(caminho: Path) -> dict[str, str]:
    arvore = ast.parse(caminho.read_text(encoding="utf-8"), filename=str(caminho))
    valores = {}
    for no in arvore.body:
        if not isinstance(no, ast.Assign):
            continue
        if not isinstance(no.value, ast.Constant) or not isinstance(no.value.value, str):
            continue
        for alvo in no.targets:
            if isinstance(alvo, ast.Name):
                valores[alvo.id] = no.value.value
    return valores


def _pinos_com_valor(caminho: Path) -> dict[str, object]:
    arvore = ast.parse(caminho.read_text(encoding="utf-8"), filename=str(caminho))
    valores = {}
    for no in arvore.body:
        if not isinstance(no, ast.Assign) or not isinstance(no.value, ast.Call):
            continue
        func = no.value.func
        if not (isinstance(func, ast.Name) and func.id == "Pin"):
            continue
        if not no.targets or not isinstance(no.targets[0], ast.Name):
            continue
        valor = None
        for kw in no.value.keywords:
            if kw.arg == "value":
                if isinstance(kw.value, ast.Constant):
                    valor = kw.value.value
                elif isinstance(kw.value, ast.Name):
                    valor = ("nome", kw.value.id)
        valores[no.targets[0].id] = valor
    return valores


def _ordem_chamadas(caminho: Path, funcao: str) -> list[str]:
    arvore = ast.parse(caminho.read_text(encoding="utf-8"), filename=str(caminho))
    for no in arvore.body:
        if isinstance(no, ast.FunctionDef) and no.name == funcao:
            ordem = []
            for stmt in no.body:
                if (
                    isinstance(stmt, ast.Expr)
                    and isinstance(stmt.value, ast.Call)
                    and isinstance(stmt.value.func, ast.Name)
                ):
                    ordem.append(stmt.value.func.id)
            return ordem
    return []


def _checa_mapa(caminho: Path, mapa: dict[str, int], proibidos: tuple[str, ...]) -> None:
    consts = _constantes(caminho)
    divergencias = [
        f"{nome}: firmware={consts.get(nome, 'ausente')} esperado={esperado}"
        for nome, esperado in mapa.items()
        if consts.get(nome) != esperado
    ]
    assert not divergencias, "pinagem divergente:\n" + "\n".join(divergencias)

    presentes = [n for n in proibidos if n in consts]
    assert not presentes, f"constantes que nao deveriam existir: {presentes}"


def test_firmwares_compilam():
    for caminho in FIRMWARES:
        compile(caminho.read_text(encoding="utf-8"), str(caminho), "exec")


def test_pinagem_ignicao():
    _checa_mapa(IGNICAO, MAPA_IGNICAO, PROIBIDOS_IGNICAO)


def test_pinagem_comando():
    _checa_mapa(COMANDO, MAPA_COMANDO, PROIBIDOS_COMANDO)


def test_tempos_de_seguranca():
    ign = _constantes(IGNICAO)
    assert ign["TEMPO_CONTAGEM_MS"] == 10000
    assert ign["TEMPO_IGNICAO_MS"] == 2000
    assert ign["TIMEOUT_SINAL_MS"] == 500

    cmd = _constantes(COMANDO)
    assert cmd["HOLD_REQUIRED_MS"] == 10000
    assert cmd["RETRANSMIT_MS"] == 200
    assert cmd["LINK_TIMEOUT_MS"] == 1000


def test_protocolo_lora():
    esperado = {
        "MSG_ARM": "ARM_CONFIRMED",
        "MSG_ABORT": "ABORT",
        "MSG_ACK": "ACK",
        "MSG_DONE": "IGNITION_COMPLETE",
    }
    for caminho in FIRMWARES:
        consts = _textos(caminho)
        for nome, valor in esperado.items():
            assert consts.get(nome) == valor, f"{caminho.name}: {nome}"


def test_comando_tem_oled_e_mario():
    fonte = COMANDO.read_text(encoding="utf-8")
    assert "SSD1306_I2C" in fonte
    assert "SEQUENCIA_MARIO" in fonte
    assert "PIN_I2C_SDA" in fonte
    assert fonte.count("Link instavel - ABORT imediato") == 2


def test_ignicao_nao_tem_oled():
    fonte = IGNICAO.read_text(encoding="utf-8")
    assert "SSD1306" not in fonte.upper()
    assert "PIN_I2C_SDA" not in fonte
    assert "oled." not in fonte


def test_rele_e_gates_nascem_desligados():
    consts = _constantes(IGNICAO)
    assert consts["RELE_ACTIVE_LEVEL"] == 0

    valores = _pinos_com_valor(IGNICAO)
    assert valores["PIN_GATE_1"] == 0
    assert valores["PIN_GATE_2"] == 0


def test_desarme_abre_q1_antes_do_rele():
    ordem = _ordem_chamadas(IGNICAO, "desligar_tudo")
    assert ordem[:3] == ["_set_gate2", "_set_rele", "_set_gate1"]


def test_scripts_de_bancada():
    for caminho in sorted(BANCADA.glob("mp_*.py")):
        compile(caminho.read_text(encoding="utf-8"), str(caminho), "exec")

    comum = _constantes(BANCADA / "mp_teste_comum.py")
    ign = _constantes(IGNICAO)
    for banco, firmware in ESPELHO_BANCADA.items():
        assert comum.get(banco) == ign.get(firmware), f"{banco} != {firmware}"

    for caminho in (BANCADA / "mp_teste_rele.py", BANCADA / "mp_teste_transistor.py"):
        valores = _pinos_com_valor(caminho)
        assert valores.get("PIN_GATE_1") == 0, f"{caminho.name}: GATE_1"
        assert valores.get("PIN_GATE_2") == 0, f"{caminho.name}: GATE_2"
        assert valores.get("PIN_RELE") == ("nome", "RELE_INACTIVE_LEVEL"), f"{caminho.name}: RELE"

    ordem = _ordem_chamadas(BANCADA / "mp_teste_transistor.py", "desligar_tudo")
    assert ordem == ["_set_gate2", "_set_rele", "_set_gate1"]


def test_readme_cita_os_tempos():
    texto = (RAIZ / "README.md").read_text(encoding="utf-8")
    for valor in ("10 s", "2 s", "500 ms"):
        assert valor in texto, f"README nao cita {valor}"


if __name__ == "__main__":
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
    sys.exit(1 if falhas else 0)
