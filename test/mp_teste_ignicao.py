# ==============================================================================
#   TESTE DE BANCADA - SEQUENCIA DE IGNICAO ISOLADA (ESP8266)
#   Alvos: logica de contagem/abort/disparo + buzzer + botao + LED do botao.
#   Nao usa LoRa, nao usa rele e nao aciona nada real (saida SIMULADA).
#   A infraestrutura (buzzer/botao/OLED/telas) vem de mp_teste_comum.py.
# ==============================================================================
#
#   LIGACAO (rotulos serigrafados na placa):
#   - Buzzer ativo: terminal + em D5 (GPIO14), outro terminal em GND.
#   - Botao: D6 (GPIO12) e o outro terminal em GND. Pull-up interno,
#     active-low, igual ao BUTTON_IN=GPIO27 da estacao de ignicao.
#   - LED do botao: anodo em D7 (GPIO13) com resistor serie de ~220R,
#     catodo em GND.
#   - OLED (opcional): VCC->3V3, GND->GND, SDA->D2 (GPIO4), SCL->D1 (GPIO5).
#   - Nao usar D3 (GPIO0), D4 (GPIO2) e D8 (GPIO15): pinos de boot da placa.
#
#   USO: aperte o botao -> contagem de 5 s com bipes (ARM_CONFIRMED simulado).
#   Aperte de novo durante a contagem para ABORTAR. No fim: "FOGO!" com saida
#   simulada de 2 s, telemetria no serial, logo da Serra Rocketry na tela e o
#   tema do Mario no buzzer.
#
#   Diferenca para mp_teste_hardware_esp8266.py: aquele valida os perifericos
#   (tela de boot, I2C, LED); este valida so os tempos e transicoes da
#   sequencia de seguranca (contagem, abort, janela de 2 s).
# ==============================================================================

import utime
from machine import Pin

from mp_teste_comum import (
    Botao,
    Buzzer,
    DURACAO_PISCA_LED_MS,
    ESTADO_ABORTADO,
    ESTADO_CONTAGEM,
    ESTADO_IDLE,
    INTERVALO_OLED_MS,
    INTERVALO_PISCA_LED_MS,
    INTERVALO_STATUS_MS,
    PAUSA_LOOP_MS,
    PIN_BUTTON_NUM,
    PIN_BUZZER_NUM,
    PIN_LED_BTN_NUM,
    abortar_sequencia,
    beep_bloqueante,
    criar_oled,
    iniciar_sequencia,
    mostrar,
    passo_sequencia,
    pisca_acesa,
)

BUZZER = Pin(PIN_BUZZER_NUM, Pin.OUT, value=0)
BUTTON = Pin(PIN_BUTTON_NUM, Pin.IN, Pin.PULL_UP)
LED_BTN = Pin(PIN_LED_BTN_NUM, Pin.OUT, value=0)

tela, _ = criar_oled()


# =============================================================================
#  LOOP PRINCIPAL
# =============================================================================

def executar():
    print("[BOOT] Teste de bancada: sequencia de ignicao isolada (ESP8266)")
    print("[INFO] Clique curto no botao: inicia a sequencia de ignicao (teste).")
    print("[INFO] Aperte de novo durante a contagem para ABORTAR (seguranca).")
    print("[INFO] No fim: FOGO! + saida simulada de 2 s + som do Mario.")
    print("[INFO] Resumo de status no serial a cada {} s.".format(INTERVALO_STATUS_MS // 1000))

    beep_bloqueante(BUZZER, 200)

    botao = Botao(BUTTON)
    buzzer = Buzzer(BUZZER)
    estado = {
        "estado": ESTADO_IDLE,
        "sequencias": 0,
        "refresh": 0,
        "segundos": 0,
        "t_boot": utime.ticks_ms(),
        "t_contagem": 0,
        "t_abortado": 0,
        "t_saida": 0,
        "t_sucesso": 0,
    }
    t_ultimo_oled = 0
    t_ultimo_status = estado["t_boot"]

    while True:
        agora = utime.ticks_ms()
        buzzer.atualizar(agora)

        for evento in botao.atualizar(agora):
            atual = estado["estado"]
            if evento == Botao.EVENTO_APERTO and atual == ESTADO_CONTAGEM:
                abortar_sequencia(estado, buzzer, agora)
            elif evento == Botao.EVENTO_CURTO and atual == ESTADO_CONTAGEM:
                abortar_sequencia(estado, buzzer, agora)
            elif atual == ESTADO_IDLE and evento in (Botao.EVENTO_CURTO, Botao.EVENTO_LONGO):
                iniciar_sequencia(estado, buzzer, agora)

        atual = estado["estado"]
        passo_sequencia(estado, buzzer, agora)

        # ------------------------------------------------------------------
        #  LED DO BOTAO (heartbeat em repouso; pisca na contagem/aborto;
        #  fixo na saida e no sucesso)
        # ------------------------------------------------------------------
        if atual == ESTADO_IDLE:
            pisca = utime.ticks_diff(agora, estado["t_boot"]) % INTERVALO_PISCA_LED_MS
            LED_BTN.value(1 if pisca < DURACAO_PISCA_LED_MS else 0)
        elif atual in (ESTADO_CONTAGEM, ESTADO_ABORTADO):
            LED_BTN.value(1 if pisca_acesa(agora) else 0)
        else:
            LED_BTN.value(1)

        # ------------------------------------------------------------------
        #  TELA E STATUS PERIODICOS
        # ------------------------------------------------------------------
        if tela.ok and utime.ticks_diff(agora, t_ultimo_oled) >= INTERVALO_OLED_MS:
            t_ultimo_oled = agora
            estado["refresh"] += 1
            mostrar(tela, estado, agora)

        if utime.ticks_diff(agora, t_ultimo_status) >= INTERVALO_STATUS_MS:
            t_ultimo_status = agora
            print("[STATUS] estado={} seqs={} uptime={}s oled={} buzzer={} led={}".format(
                estado["estado"],
                estado["sequencias"],
                utime.ticks_diff(agora, estado["t_boot"]) // 1000,
                "OK" if tela.ok else "--",
                "ON" if buzzer.tocando else "OFF",
                LED_BTN.value(),
            ))

        utime.sleep_ms(PAUSA_LOOP_MS)


# =============================================================================
#  PONTO DE ENTRADA
# =============================================================================
if __name__ == "__main__":
    executar()
