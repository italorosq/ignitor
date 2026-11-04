# ==============================================================================
#   TESTE DE BANCADA - CADEIA DE SEGURANCA COM OS TRANSISTORES (ESP32)
#   Alvos: Q1 (net GATE_2, chave de saida do ignitor) e Q2 (net GATE_1, que
#   liga o GND do modulo rele). Valida o fail-safe e a ORDEM de armar/desarmar
#   a cadeia em serie, com carga dummy. NAO usar ignitor real.
# ==============================================================================
#
#   LIGACAO (ESP32 DevKit V1, mapa oficial do projeto):
#   - Modulo rele na bancada: VCC->5V, GND->GND, IN->GPIO32.
#   - Q2/GATE_1 (GPIO13) ja chaveia o GND do modulo rele na placa: nada a
#     ligar; o proprio modulo serve de carga do Q2.
#   - IGNITOR -> LED + resistor de 1k em serie (carga dummy) no lugar do
#     ignitor, no caminho que passa pelo contato do rele e pelo Q1.
#   - Buzzer ativo 3,3 V: + em GPIO14, - em GND.
#   - Botao: GPIO27 e o outro terminal em GND (pull-up interno, active-low).
#   - Botao curto = proximo passo | botao longo (1 s) = ABORTAR.
#
#   PASSOS (o LED dummy do ignitor so acende no passo 3):
#     1. GATE_1 (Q2) ON  -> modulo rele ENERGIZA (Ainda sem click).
#     2. RELE ON (IN baixo) -> modulo CLICA; LED dummy APAGADO (Q1 aberto =
#        interlock: contato fechado, mas sem caminho de corrente).
#     3. GATE_2 (Q1) ON  -> LED dummy ACENDE por 2 s (janela do firmware).
#     4. Desarme automatico na ordem segura: Q1 -> rele -> Q2.
#
#   SEGURANCA: nenhum ignitor real; carga dummy SEMPRE. O teste BLOQUEIA se
#   Q1/Q2 nao nascerem OFF ou se o IN do rele nascer ativo (fail-safe).
# ==============================================================================

import utime
from machine import Pin

from mp_teste_comum import (
    Botao,
    Buzzer,
    INTERVALO_STATUS_MS,
    PAUSA_LOOP_MS,
    PIN_ESP32_BUTTON_NUM,
    PIN_ESP32_BUZZER_NUM,
    PIN_ESP32_GATE_1_NUM,
    PIN_ESP32_GATE_2_NUM,
    PIN_ESP32_RELE_NUM,
    RELE_ACTIVE_LEVEL,
    RELE_INACTIVE_LEVEL,
    TEMPO_ABORTADO_MS,
    TEMPO_SAIDA_MS,
    beep_bloqueante,
)

# Rele SRD-05VDC (ativo em baixo): nasce INATIVO. Gates dos MOSFETs (ativos
# em ALTO): nascem em 0 = OFF, como no firmware da estacao.
PIN_RELE = Pin(PIN_ESP32_RELE_NUM, Pin.OUT, value=RELE_INACTIVE_LEVEL)
PIN_GATE_1 = Pin(PIN_ESP32_GATE_1_NUM, Pin.OUT, value=0)
PIN_GATE_2 = Pin(PIN_ESP32_GATE_2_NUM, Pin.OUT, value=0)
PIN_BUZZER = Pin(PIN_ESP32_BUZZER_NUM, Pin.OUT, value=0)
BUTTON = Pin(PIN_ESP32_BUTTON_NUM, Pin.IN, Pin.PULL_UP)

ESTADO_IDLE = "IDLE"
ESTADO_GATE_1 = "GATE_1"
ESTADO_RELE = "RELE"
ESTADO_IGNITOR = "IGNITOR"
ESTADO_ABORTADO = "ABORTADO"


def _set_rele(ligado):
    PIN_RELE.value(RELE_ACTIVE_LEVEL if ligado else RELE_INACTIVE_LEVEL)


def _set_gate1(ligado):
    PIN_GATE_1.value(1 if ligado else 0)


def _set_gate2(ligado):
    PIN_GATE_2.value(1 if ligado else 0)


def desligar_tudo():
    # Ordem segura: Q1 corta a corrente primeiro, depois o contato do rele,
    # por ultimo a alimentacao do modulo (Q2). Mesmo espirito do firmware.
    _set_gate2(False)
    _set_rele(False)
    _set_gate1(False)


def _resumo_pinos():
    return "Q2(GATE_1)={} Q1(GATE_2)={} RELE_IN={}".format(
        PIN_GATE_1.value(), PIN_GATE_2.value(), PIN_RELE.value())


def _problemas_fail_safe():
    problemas = []
    if PIN_GATE_1.value() != 0:
        problemas.append("Q2/GATE_1 ligado no boot")
    if PIN_GATE_2.value() != 0:
        problemas.append("Q1/GATE_2 ligado no boot")
    if PIN_RELE.value() != RELE_INACTIVE_LEVEL:
        problemas.append("IN do rele ativo no boot")
    return problemas


# =============================================================================
#  PASSOS DA CADEIA
# =============================================================================

def _passo1(estado, buzzer, agora):
    _set_gate1(True)
    estado["estado"] = ESTADO_GATE_1
    buzzer.bip(100, agora)
    print("[PASSO 1/4] GATE_1 (Q2) LIGADO: o modulo rele deve ENERGIZAR.")
    print("            Espere energia/LED no modulo, mas SEM click ainda.")
    print("[INFO] Botao curto = passo 2 | botao longo = ABORTAR.")


def _passo2(estado, buzzer, agora):
    _set_rele(True)
    estado["estado"] = ESTADO_RELE
    buzzer.bip(100, agora)
    print("[PASSO 2/4] RELE LIGADO (IN ativo em baixo): deve CLICAR agora.")
    print("            O LED dummy do ignitor segue APAGADO (Q1 aberto = interlock).")
    print("[INFO] Botao curto = passo 3 (ACENDE o dummy) | longo = ABORTAR.")


def _passo3(estado, buzzer, agora):
    _set_gate2(True)
    estado["estado"] = ESTADO_IGNITOR
    estado["t_janela"] = agora
    buzzer.tocar(((400, 0),), agora)
    print("[PASSO 3/4] GATE_2 (Q1) LIGADO: LED dummy do ignitor ACENDE por {} s.".format(
        TEMPO_SAIDA_MS // 1000))
    print("[SEGURANCA] Aperto curto/longo agora ABORTA na hora.")


def _fim_da_janela(estado, buzzer, agora):
    print("[PASSO 3/4] Janela de {} s encerrada: Q1 abre primeiro (LED apaga).".format(
        TEMPO_SAIDA_MS // 1000))
    desligar_tudo()
    estado["estado"] = ESTADO_IDLE
    buzzer.tocar(((200, 0),), agora)
    print("[PASSO 4/4] Desarme na ordem segura: Q1 -> rele -> Q2.")
    print("[OK] Cadeia desarmada ({}).".format(_resumo_pinos()))
    print("[OK] Pronto para novo ciclo.")


def _abortar(estado, buzzer, agora):
    desligar_tudo()
    estado["estado"] = ESTADO_ABORTADO
    estado["t_abortado"] = agora
    buzzer.tocar(((600, 0),), agora)
    print("[SEGURANCA] ABORTADO! Cadeia desarmada na ordem Q1 -> rele -> Q2.")
    print("[SEGURANCA] Pinos agora: {}.".format(_resumo_pinos()))


# =============================================================================
#  LOOP PRINCIPAL
# =============================================================================

def executar():
    print("[BOOT] Teste de bancada: cadeia de seguranca Q1/Q2 (ESP32)")
    print("[SEGURANCA] Confirme: NENHUM ignitor real; carga dummy (LED+1k).")
    print("[INFO] Botao curto avanca os 4 passos; botao longo aborta.")
    print("[INFO] Status no serial a cada {} s.".format(INTERVALO_STATUS_MS // 1000))

    beep_bloqueante(PIN_BUZZER, 200)

    problemas = _problemas_fail_safe()
    if problemas:
        print("[SEGURANCA] FALHA NO FAIL-SAFE:")
        for problema in problemas:
            print("[SEGURANCA]   - {}".format(problema))
        print("[SEGURANCA] Teste BLOQUEADO. Desligue a chave geral e revise a cadeia.")
        while True:
            beep_bloqueante(PIN_BUZZER, 120)
            utime.sleep_ms(880)

    print("[BOOT] Fail-safe OK: Q2/Q1 OFF e IN do rele inativo ({}).".format(
        _resumo_pinos()))
    print("[INFO] Aperte o botao para o passo 1.")

    botao = Botao(BUTTON)
    buzzer = Buzzer(PIN_BUZZER)
    estado = {
        "estado": ESTADO_IDLE,
        "t_boot": utime.ticks_ms(),
        "t_janela": 0,
        "t_abortado": 0,
    }
    t_ultimo_status = estado["t_boot"]

    while True:
        agora = utime.ticks_ms()
        buzzer.atualizar(agora)

        for evento in botao.atualizar(agora):
            atual = estado["estado"]
            if evento == Botao.EVENTO_LONGO and atual != ESTADO_IDLE:
                _abortar(estado, buzzer, agora)
            elif evento == Botao.EVENTO_APERTO and atual == ESTADO_IGNITOR:
                _abortar(estado, buzzer, agora)
            elif atual == ESTADO_IDLE and evento in (Botao.EVENTO_CURTO, Botao.EVENTO_LONGO):
                _passo1(estado, buzzer, agora)
            elif atual == ESTADO_GATE_1 and evento == Botao.EVENTO_CURTO:
                _passo2(estado, buzzer, agora)
            elif atual == ESTADO_RELE and evento == Botao.EVENTO_CURTO:
                _passo3(estado, buzzer, agora)

        atual = estado["estado"]

        if atual == ESTADO_IGNITOR:
            if utime.ticks_diff(agora, estado["t_janela"]) >= TEMPO_SAIDA_MS:
                _fim_da_janela(estado, buzzer, agora)
        elif atual == ESTADO_ABORTADO:
            if utime.ticks_diff(agora, estado["t_abortado"]) >= TEMPO_ABORTADO_MS:
                estado["estado"] = ESTADO_IDLE
                print("[OK] Aborto concluido. Pronto para novo ciclo.")

        if utime.ticks_diff(agora, t_ultimo_status) >= INTERVALO_STATUS_MS:
            t_ultimo_status = agora
            print("[STATUS] estado={} {} uptime={}s".format(
                estado["estado"],
                _resumo_pinos(),
                utime.ticks_diff(agora, estado["t_boot"]) // 1000,
            ))

        utime.sleep_ms(PAUSA_LOOP_MS)


# =============================================================================
#  PONTO DE ENTRADA
# =============================================================================
if __name__ == "__main__":
    executar()
