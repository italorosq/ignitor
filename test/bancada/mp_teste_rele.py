# ==============================================================================
#   TESTE DE BANCADA - MODULO RELE SRD-05VDC (ESP32)
#   Alvos: entrada IN ativo em BAIXO (GPIO32), click do contato e o interlock
#   com Q2/GATE_1 (sem GATE_1 o modulo nem energiza). Carga dummy apenas.
# ==============================================================================
#
#   LIGACAO (ESP32 DevKit V1, mapa oficial do projeto):
#   - Modulo rele: VCC->5V, GND->GND, IN->GPIO32.
#   - Q2/GATE_1 (GPIO13) ja chaveia o GND do modulo na placa (nada a ligar).
#   - IGNITOR -> LED + resistor de 1k em serie (carga dummy) no lugar do
#     ignitor, no caminho que passa pelo contato do rele.
#   - Buzzer ativo 3,3 V: + em GPIO14, - em GND.
#   - Botao: GPIO27 e o outro terminal em GND (pull-up interno, active-low).
#   - GATE_2 (Q1, saida do ignitor) NAO e acionado aqui: e fixado em OFF no
#     boot. O teste do Q1 e o mp_teste_transistor.py.
#
#   TESTES:
#     1. Interlock (automatico no boot): com GATE_1 OFF, pulso de 1,5 s no IN.
#        O modulo NAO pode clicar. Click = interlock quebrado, PARE.
#     2. Toggles manuais: clique curto alterna o rele (bipe sincronizado).
#     3. Ciclos automaticos: clique longo roda 10 ciclos de 500 ms; clique
#        curto/longo durante os ciclos cancela e desliga o rele.
#
#   SEGURANCA: nenhum ignitor real; carga dummy SEMPRE. O teste BLOQUEIA se o
#   IN do rele nascer ativo (fail-safe).
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
    beep_bloqueante,
)

# Rele ativo em baixo: nasce INATIVO (IN em ALTO). Q2/GATE_1 nasce OFF; o
# modulo rele so recebe energia no teste 2, quando o gate e ligado. Q1/GATE_2
# tambem e fixado em OFF (o pull-down externo ja garante, mas explicito e
# melhor): o ignitor dummy nunca tem caminho de corrente neste teste.
PIN_RELE = Pin(PIN_ESP32_RELE_NUM, Pin.OUT, value=RELE_INACTIVE_LEVEL)
PIN_GATE_1 = Pin(PIN_ESP32_GATE_1_NUM, Pin.OUT, value=0)
PIN_GATE_2 = Pin(PIN_ESP32_GATE_2_NUM, Pin.OUT, value=0)
PIN_BUZZER = Pin(PIN_ESP32_BUZZER_NUM, Pin.OUT, value=0)
BUTTON = Pin(PIN_ESP32_BUTTON_NUM, Pin.IN, Pin.PULL_UP)

CICLOS_AUTO = 10
INTERVALO_CICLO_MS = 500
TEMPO_INTERLOCK_MS = 1500

ESTADO_CICLOS = "CICLOS"
ESTADO_AUTO = "AUTO"


def _set_rele(ligado):
    PIN_RELE.value(RELE_ACTIVE_LEVEL if ligado else RELE_INACTIVE_LEVEL)


def _set_gate1(ligado):
    PIN_GATE_1.value(1 if ligado else 0)


def _resumo_pinos():
    return "Q2(GATE_1)={} RELE_IN={}".format(PIN_GATE_1.value(), PIN_RELE.value())


def _problemas_fail_safe():
    problemas = []
    if PIN_GATE_1.value() != 0:
        problemas.append("Q2/GATE_1 ligado no boot")
    if PIN_RELE.value() != RELE_INACTIVE_LEVEL:
        problemas.append("IN do rele ativo no boot")
    return problemas


# =============================================================================
#  TESTES
# =============================================================================

def _teste_interlock():
    print("[TESTE 1] Interlock: GATE_1 OFF + IN ativo por {} ms.".format(TEMPO_INTERLOCK_MS))
    print("[TESTE 1] Com o modulo SEM energia NAO pode haver click - escute.")
    _set_rele(True)
    utime.sleep_ms(TEMPO_INTERLOCK_MS)
    _set_rele(False)
    print("[TESTE 1] Fim do pulso. Se ouviu click, PARE: o interlock falhou")
    print("[TESTE 1] (revise Q2/GATE_1 e a alimentacao do modulo).")


def _alternar_manual(estado, buzzer, agora):
    estado["rele_ligado"] = not estado["rele_ligado"]
    _set_rele(estado["rele_ligado"])
    buzzer.bip(60, agora)
    if estado["rele_ligado"]:
        estado["toggles"] += 1
    print("[RELE] {} (toggle #{})".format(
        "LIGADO" if estado["rele_ligado"] else "DESLIGADO", estado["toggles"]))


def _iniciar_auto(estado, buzzer, agora):
    estado["estado"] = ESTADO_AUTO
    estado["auto_feitos"] = 0
    estado["auto_ligado"] = True
    estado["t_fase"] = agora
    _set_rele(True)
    buzzer.bip(80, agora)
    print("[AUTO] {} ciclos de {} ms. Botao longo cancela.".format(
        CICLOS_AUTO, INTERVALO_CICLO_MS))
    print("[AUTO] ciclo 1/{}: rele LIGADO".format(CICLOS_AUTO))


def _cancelar_auto(estado, buzzer, agora):
    _set_rele(False)
    estado["rele_ligado"] = False
    estado["estado"] = ESTADO_CICLOS
    buzzer.tocar(((150, 0),), agora)
    print("[AUTO] Cancelado pelo botao. Rele DESLIGADO.")


def _passo_auto(estado, buzzer, agora):
    if utime.ticks_diff(agora, estado["t_fase"]) < INTERVALO_CICLO_MS:
        return
    estado["t_fase"] = agora
    buzzer.bip(30, agora)
    if estado["auto_ligado"]:
        _set_rele(False)
        estado["auto_ligado"] = False
        estado["auto_feitos"] += 1
        print("[AUTO] ciclo {}/{}: rele DESLIGADO".format(estado["auto_feitos"], CICLOS_AUTO))
        if estado["auto_feitos"] >= CICLOS_AUTO:
            estado["estado"] = ESTADO_CICLOS
            buzzer.tocar(((200, 0),), agora)
            print("[OK] {} ciclos concluidos. Rele DESLIGADO.".format(CICLOS_AUTO))
    else:
        _set_rele(True)
        estado["auto_ligado"] = True
        print("[AUTO] ciclo {}/{}: rele LIGADO".format(estado["auto_feitos"] + 1, CICLOS_AUTO))


# =============================================================================
#  LOOP PRINCIPAL
# =============================================================================

def executar():
    print("[BOOT] Teste de bancada: modulo rele SRD-05VDC (ESP32)")
    print("[SEGURANCA] Confirme: NENHUM ignitor real; carga dummy (LED+1k).")

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

    print("[BOOT] Fail-safe OK: Q2 OFF e IN do rele inativo ({}).".format(_resumo_pinos()))

    _teste_interlock()

    # Energiza o modulo (Q2) para os testes 2 e 3.
    _set_gate1(True)
    print("[TESTE 2] Q2/GATE_1 ligado: modulo energizado.")
    print("[TESTE 2] Clique curto alterna o rele | clique longo roda os ciclos.")
    print("[INFO] Status no serial a cada {} s.".format(INTERVALO_STATUS_MS // 1000))

    botao = Botao(BUTTON)
    buzzer = Buzzer(PIN_BUZZER)
    estado = {
        "estado": ESTADO_CICLOS,
        "rele_ligado": False,
        "toggles": 0,
        "auto_feitos": 0,
        "auto_ligado": False,
        "t_fase": 0,
        "t_boot": utime.ticks_ms(),
    }
    t_ultimo_status = estado["t_boot"]

    while True:
        agora = utime.ticks_ms()
        buzzer.atualizar(agora)

        for evento in botao.atualizar(agora):
            atual = estado["estado"]
            if atual == ESTADO_AUTO:
                if evento in (Botao.EVENTO_APERTO, Botao.EVENTO_LONGO):
                    _cancelar_auto(estado, buzzer, agora)
            elif evento == Botao.EVENTO_CURTO:
                _alternar_manual(estado, buzzer, agora)
            elif evento == Botao.EVENTO_LONGO:
                _iniciar_auto(estado, buzzer, agora)

        atual = estado["estado"]
        if atual == ESTADO_AUTO:
            _passo_auto(estado, buzzer, agora)

        if utime.ticks_diff(agora, t_ultimo_status) >= INTERVALO_STATUS_MS:
            t_ultimo_status = agora
            print("[STATUS] estado={} {} toggles={} auto={}/{} uptime={}s".format(
                estado["estado"],
                _resumo_pinos(),
                estado["toggles"],
                estado["auto_feitos"],
                CICLOS_AUTO,
                utime.ticks_diff(agora, estado["t_boot"]) // 1000,
            ))

        utime.sleep_ms(PAUSA_LOOP_MS)


# =============================================================================
#  PONTO DE ENTRADA
# =============================================================================
if __name__ == "__main__":
    executar()
