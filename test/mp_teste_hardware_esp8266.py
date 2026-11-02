# ==============================================================================
#   TESTE DE BANCADA - PERIFERICOS NO ESP8266 (NodeMCU v3 / Wemos D1 mini)
#   Alvos: OLED SSD1306 (I2C), buzzer ativo 3,3 V, botao e LED do botao.
#   Teste isolado: nao usa LoRa nem se conecta a nenhuma estacao.
#   A infraestrutura (buzzer/botao/I2C/OLED/telas/sequencia) vem de
#   mp_teste_comum.py - envie o modulo junto com este script.
# ==============================================================================
#
#   LIGACAO (rotulos serigrafados na placa):
#   - OLED VCC->3V3, GND->GND, SDA->D2 (GPIO4), SCL->D1 (GPIO5)
#   - Buzzer ativo: terminal + em D5 (GPIO14), outro terminal em GND.
#     GPIO14 e o mesmo numero do buzzer na estacao de ignicao ESP32.
#   - Botao: D6 (GPIO12) e o outro terminal em GND. Pull-up interno,
#     active-low, igual ao BUTTON_IN=GPIO27 da estacao de ignicao.
#   - LED do botao: anodo em D7 (GPIO13) com resistor serie de ~220R,
#     catodo em GND.
#   - Nao usar D3 (GPIO0), D4 (GPIO2) e D8 (GPIO15): pinos de boot da placa.
#
#   USO: aperte o botao -> comando de ignicao na tela (contagem de 5 s com
#   bipes, igual a sequencia do projeto). Aperte de novo durante a contagem
#   para ABORTAR (demo de seguranca). No fim: "FOGO!" com saida simulada de
#   2 s, telemetria no serial, logo da Serra Rocketry na tela e o tema do
#   Mario no buzzer.
#
#   OBS: o I2C do ESP8266 e por software (bit-bang): o init tenta 400 kHz e
#   cai para 100 kHz se o scan falhar. O serial (115200) repete o que a
#   tela mostra, para o caso de OLED ausente.
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

# =============================================================================
#  PINAGEM (ESP8266) E DISPLAY
# =============================================================================

BUZZER = Pin(PIN_BUZZER_NUM, Pin.OUT, value=0)
BUTTON = Pin(PIN_BUTTON_NUM, Pin.IN, Pin.PULL_UP)
LED_BTN = Pin(PIN_LED_BTN_NUM, Pin.OUT, value=0)

tela, I2C_ENCONTRADOS = criar_oled()


def _tela_boot(tela, encontrados):
    if not tela.ok:
        return
    try:
        resumo = "I2C:" + "".join(" {:02X}".format(a) for a in encontrados)
        tela.oled.fill(0)
        tela.oled.text("TESTE HW ESP8266", 0, 0)
        tela.oled.text("NodeMCU / D1mini", 0, 12)
        tela.oled.text(resumo[:16], 0, 24)
        tela.oled.text("SDA:D2 SCL:D1", 0, 36)
        tela.oled.text("BUZ:D5 BTN:D6", 0, 48)
        tela.oled.text("LED_BTN: D7", 0, 56)
        tela.oled.show()
    except Exception as exc:
        tela.desabilitar(exc)


# =============================================================================
#  LOOP PRINCIPAL
# =============================================================================

def executar():
    print("[BOOT] Teste de bancada ESP8266: OLED + buzzer + botao + LED do botao")
    print("[INFO] Clique curto no botao: inicia a sequencia de ignicao (teste).")
    print("[INFO] Aperte de novo durante a contagem para ABORTAR (seguranca).")
    print("[INFO] No fim: FOGO! + saida simulada de 2 s + som do Mario.")
    print("[INFO] Resumo de status no serial a cada {} s.".format(INTERVALO_STATUS_MS // 1000))

    beep_bloqueante(BUZZER, 200)
    _tela_boot(tela, I2C_ENCONTRADOS)

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
