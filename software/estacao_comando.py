"""
ESTACAO DE COMANDO - SISTEMA DE IGNICAO LoRa

Pinagem SX1278 -> Raspberry Pi Pico
- MOSI: GP3 (pino fisico 5)
- MISO: GP0 (pino fisico 1)
- SCK: GP2 (pino fisico 4)
- CS: GP1 (pino fisico 2)
- RESET: GP4 (pino fisico 6)
- DIO0: GP15 (pino fisico 20)

Perifericos
- LED amarelo: GP11
- LED vermelho: GP12
- Buzzer: GP19
- Botao de ignicao: GP13 (pull-up interno)
"""

from machine import Pin, SPI
import utime

# ─────────────────────────────────────────────────────────────────
#  DEPENDÊNCIA: driver SX127x para MicroPython
#  Instale copiando sx127x.py para o Pico via Thonny ou mpremote.
#  Repositório: https://github.com/Serra-Rocketry/ignitor
#  ou instale via: mpremote mip install github:Wei1234c/SX127x_driver
# ─────────────────────────────────────────────────────────────────
try:
    from sx127x import SX127x
    LORA_AVAILABLE = True
except ImportError:
    # Modo de desenvolvimento sem hardware LoRa
    LORA_AVAILABLE = False
    print("[WARN] sx127x não encontrado — rodando sem LoRa real.")


# ╔══════════════════════════════════════════════════════════════╗
# ║                     CONFIGURAÇÕES                           ║
# ╚══════════════════════════════════════════════════════════════╝

# ── Pinos SPI / LoRa ─────────────────────────────────────────────
PIN_MOSI  = 3
PIN_MISO  = 0
PIN_SCK   = 2
PIN_CS    = 1
PIN_RESET = 4
PIN_DIO0  = 15

# ── Periféricos ──────────────────────────────────────────────────
PIN_LED_YELLOW = 11  # status de conexao e armamento
PIN_LED_RED    = 12  # acende fixo ao receber ACK
PIN_BUZZER     = 19  # bipes de alerta
PIN_BUTTON     = 13  # botao momentaneo (active-low, pull-up)

# ── Tempos (ms) ──────────────────────────────────────────────────
HOLD_REQUIRED_MS   = 5_000   # tempo que o botão deve ficar pressionado
DEBOUNCE_MS        = 50      # janela de debounce
BLINK_INTERVAL_MS  = 250     # cadência do LED amarelo / buzzer
ACK_TIMEOUT_MS     = 2_000   # aguarda ACK por este tempo após ARM_CONFIRMED
RETRANSMIT_MS      = 200     # intervalo entre re-envios do ARM_CONFIRMED
PING_INTERVAL_MS   = 1_000   # intervalo de PING para teste de conexao
LINK_TIMEOUT_MS    = 3_000   # sem PONG neste tempo = sem conexao
FINALIZE_DELAY_MS  = 3_000   # espera apos ignicao concluida

# ── Mensagens LoRa ───────────────────────────────────────────────
MSG_ARM    = "ARM_CONFIRMED"
MSG_ABORT  = "ABORT"
MSG_ACK    = "ACK"
MSG_DONE   = "IGNITION_COMPLETE"
MSG_PING   = "PING"
MSG_PONG   = "PONG"

# ── Parâmetros LoRa (SX1278 @ 433 MHz) ──────────────────────────
LORA_PARAMS = {
    "frequency"         : 433e6,
    "bandwidth"         : 125e3,
    "spreading_factor"  : 7,
    "coding_rate"       : 5,        # 4/5
    "output_power"      : 17,       # dBm (máx 20)
    "rx_crc"            : True,
}


# ╔══════════════════════════════════════════════════════════════╗
# ║                    ESTADOS DA MÁQUINA                       ║
# ╚══════════════════════════════════════════════════════════════╝
class State:
    # Estado inicial: aguardando a pressão do botão de ignição.
    IDLE        = "IDLE"
    # Estado de armamento: o botão está pressionado e o sistema conta 5 segundos.
    ARMING      = "ARMING"
    # Estado de transmissão: envia repetidamente o comando de armamento.
    TRANSMITTING = "TRANSMITTING"
    # Estado de confirmação: ignicao concluida no receptor.
    CONFIRMED   = "CONFIRMED"
    # Estado de aborto: envia ABORT para o receptor e retorna a IDLE.
    ABORTING    = "ABORTING"


# ╔══════════════════════════════════════════════════════════════╗
# ║                  DRIVER LoRa (wrapper)                      ║
# ╚══════════════════════════════════════════════════════════════╝
class LoRaRadio:
    """
    Abstração sobre o driver SX127x.

    Permite operar com o rádio real quando o driver está instalado e
    um modo mock silencioso quando o hardware não está disponível.
    """

    def __init__(self):
        if LORA_AVAILABLE:
            spi = SPI( 
                0,
                baudrate=1_000_000,
                polarity=0,
                phase=0,
                sck=Pin(PIN_SCK),
                mosi=Pin(PIN_MOSI),
                miso=Pin(PIN_MISO),
            )
            self._lora = SX127x(
                spi,
                pins={
                    "cs"    : Pin(PIN_CS,    Pin.OUT),
                    "reset" : Pin(PIN_RESET, Pin.OUT),
                    "dio0"  : Pin(PIN_DIO0,  Pin.IN),
                },
                parameters=LORA_PARAMS,
            )
            print("[LoRa] SX1278 inicializado em 433 MHz.")
        else:
            self._lora = None
            print("[LoRa] Modo MOCK ativo.")

    def send(self, message):
        """Transmite uma mensagem pela interface LoRa e mostra log local."""
        if self._lora:
            self._lora.println(message)
        print(f"[LoRa TX] → {message}")

    def receive(self):
        """
        Lê um pacote LoRa não bloqueante, se houver.

        Retorna a mensagem decodificada ou None quando não há nenhum pacote.
        """
        if self._lora and self._lora.received_packet():
            payload = self._lora.read_payload(with_header=False)
            msg = bytes(payload).decode("utf-8", "ignore").strip()
            print(f"[LoRa RX] ← {msg}")
            return msg
        return None


# ╔══════════════════════════════════════════════════════════════╗
# ║                 ESTAÇÃO DE COMANDO                          ║
# ╚══════════════════════════════════════════════════════════════╝
class CommandStation:
    """
    Máquina de estados para a estação de comando.

    Esta classe controla o ciclo de armamento e transmissão de mensagens
    de ignição via LoRa, usando um botão físico e indicadores visuais.

    Fluxo de estados:
    IDLE -> ARMING -> TRANSMITTING -> CONFIRMED -> IDLE
    """

    def __init__(self):
        # Inicializa os componentes físicos e o rádio LoRa.
        self.led_yellow = Pin(PIN_LED_YELLOW, Pin.OUT, value=0)
        self.led_red    = Pin(PIN_LED_RED,    Pin.OUT, value=0)
        self.buzzer     = Pin(PIN_BUZZER,     Pin.OUT, value=0)
        self.button     = Pin(PIN_BUTTON,     Pin.IN,  Pin.PULL_UP)
        self.lora       = LoRaRadio()

        # Estado atual da máquina e estado anterior reservado para futura expansão.
        self.state       = State.IDLE
        self._prev_state = None

        # Tempos de controle usados para armamento, piscar e transmissão.
        self._press_start_ms  = 0    # instante em que o botão foi pressionado
        self._last_blink_ms   = 0    # instante do último piscar do LED/buzzer
        self._last_tx_ms      = 0    # instante do último envio de ARM_CONFIRMED
        self._tx_start_ms     = 0    # instante do início da fase de transmissão
        self._finalize_start_ms = 0  # inicio da janela de finalizacao
        self._ack_received = False

        # Debounce do botão para evitar leituras falsas.
        self._last_btn_change_ms = 0
        self._btn_stable_state   = True   # True significa botão solto (pull-up ativo)

        # Estado de toggle para o efeito de piscar.
        self._blink_on = False

        # Estado de link com a estacao de ignicao.
        self._link_ok = False
        self._last_ping_ms = 0
        self._last_pong_ms = None
        self._last_no_link_warn_ms = 0

    # ─────────────────────────────────────────
    #  LEITURA COM DEBOUNCE
    # ─────────────────────────────────────────
    def _button_pressed(self) -> bool:
        """
        Retorna True se o botão está estável e pressionado.
        Implementa debounce por tempo: só atualiza o estado estável
        após DEBOUNCE_MS ms de sinal constante.
        """
        raw = self.button.value() == 0   # active-low
        now = utime.ticks_ms()

        if raw != self._btn_stable_state:
            if utime.ticks_diff(now, self._last_btn_change_ms) >= DEBOUNCE_MS:
                self._btn_stable_state   = raw
                self._last_btn_change_ms = now

        return self._btn_stable_state

    # ─────────────────────────────────────────
    #  CONTROLE DE SAÍDAS
    # ─────────────────────────────────────────
    def _all_off(self):
        """Desliga todos os indicadores visuais e sonoros."""
        self.led_yellow.value(0)
        self.led_red.value(0)
        self.buzzer.value(0)
        self._blink_on = False

    def _refresh_link(self, now):
        """Mantem o teste de conexao ativo com PING/PONG."""
        if utime.ticks_diff(now, self._last_ping_ms) >= PING_INTERVAL_MS:
            self._last_ping_ms = now
            self.lora.send(MSG_PING)

        incoming = self.lora.receive()
        if incoming == MSG_PING:
            self.lora.send(MSG_PONG)
            self._last_pong_ms = now
        elif incoming == MSG_PONG:
            self._last_pong_ms = now

        link_was_ok = self._link_ok
        if self._last_pong_ms is None:
            self._link_ok = False
        else:
            self._link_ok = utime.ticks_diff(now, self._last_pong_ms) <= LINK_TIMEOUT_MS
        if self._link_ok != link_was_ok:
            status = "OK" if self._link_ok else "PERDIDO"
            print(f"[CMD] Link com ignicao: {status}")

    def _blink_tick(self):
        """Alterna LED amarelo e buzzer em BLINK_INTERVAL_MS."""
        now = utime.ticks_ms()
        if utime.ticks_diff(now, self._last_blink_ms) >= BLINK_INTERVAL_MS:
            self._last_blink_ms = now
            self._blink_on = not self._blink_on
            self.led_yellow.value(self._blink_on)
            self.buzzer.value(self._blink_on)

    # ─────────────────────────────────────────
    #  TRANSIÇÕES DE ESTADO
    # ─────────────────────────────────────────
    def _enter_idle(self):
        self._all_off()
        if self._link_ok:
            self.led_yellow.value(1)
        self.state = State.IDLE
        print("[CMD] Estado: IDLE — aguardando botão.")

    def _enter_arming(self): 
        self._press_start_ms = utime.ticks_ms()
        self._last_blink_ms  = self._press_start_ms
        self.state = State.ARMING
        print("[CMD] Estado: ARMING — mantenha o botão por 5 s...")

    def _enter_transmitting(self):
        self._tx_start_ms = utime.ticks_ms()
        self._last_tx_ms  = 0
        self._ack_received = False
        self.led_red.value(0)
        self.state = State.TRANSMITTING
        print("[CMD] Estado: TRANSMITTING — mantendo ARM_CONFIRMED ativo.")

    def _enter_confirmed(self):
        self._all_off()
        self.led_red.value(1)
        self._finalize_start_ms = utime.ticks_ms()
        self.state = State.CONFIRMED
        print("[CMD] Estado: CONFIRMED — IGNITION_COMPLETE recebido.")

    def _enter_aborting(self):
        self.lora.send(MSG_ABORT)
        self._all_off()
        self.state = State.ABORTING
        print("[CMD] Estado: ABORTING — ABORT enviado.")
        # Retorna imediatamente ao IDLE (sem lógica adicional necessária)
        self._enter_idle()

    # ─────────────────────────────────────────
    #  HANDLERS DE CADA ESTADO
    # ─────────────────────────────────────────
    def _handle_idle(self):
        # Apenas aguarda o início do armamento quando o botão é pressionado.
        now = utime.ticks_ms()
        self._refresh_link(now)
        if self._link_ok:
            self.led_yellow.value(1)

        if self._button_pressed():
            if not self._link_ok:
                if utime.ticks_diff(now, self._last_no_link_warn_ms) >= 1_000:
                    self._last_no_link_warn_ms = now
                    print("[CMD] Sem link LoRa ativo. Armamento bloqueado.")
                return
            self._enter_arming()

    def _handle_arming(self):
        # Se o botão for solto antes de 5 segundos, o processo é cancelado.
        if not self._button_pressed():
            print("[CMD] Botão solto antes dos 5 s — cancelando.")
            self._enter_idle()
            return

        # Enquanto o botão estiver pressionado, pisca LED amarelo e buzzer.
        self._blink_tick()

        elapsed = utime.ticks_diff(utime.ticks_ms(), self._press_start_ms)
        remaining = max(0, (HOLD_REQUIRED_MS - elapsed) // 1000)

        # Exibe uma atualização de tempo a cada segundo.
        if elapsed // 1000 != (elapsed - 50) // 1000:
            print(f"[CMD] Armando... {remaining} s restantes.")

        # Se o tempo mínimo for atingido, inicia a transmissão.
        if elapsed >= HOLD_REQUIRED_MS:
            self._enter_transmitting()

    def _handle_transmitting(self):
        # Se o botão soltar durante a transmissão, aborta imediatamente.
        if not self._button_pressed():
            print("[CMD] Botão solto durante transmissão — ABORT.")
            self._enter_aborting()
            return

        now = utime.ticks_ms()

        # Reenvia o comando de armamento periodicamente.
        if utime.ticks_diff(now, self._last_tx_ms) >= RETRANSMIT_MS:
            self._last_tx_ms = now
            self.lora.send(MSG_ARM)

        # Verifica se o receptor devolveu o ACK.
        incoming = self.lora.receive()
        if incoming == MSG_ACK:
            if not self._ack_received:
                self._ack_received = True
                self.led_red.value(1)
                print("[CMD] ACK recebido da base de ignicao.")
        elif incoming == MSG_DONE:
            self._enter_confirmed()
            return
        elif incoming == MSG_PING:
            self.lora.send(MSG_PONG)
        elif incoming == MSG_PONG:
            self._last_pong_ms = now
            self._link_ok = True

        # Se não receber ACK dentro do tempo, reinicia a janela de espera.
        if utime.ticks_diff(now, self._tx_start_ms) >= ACK_TIMEOUT_MS:
            print("[CMD] Timeout aguardando ACK — continuando a transmitir.")
            self._tx_start_ms = now

    def _handle_confirmed(self):
        # Aguarda a janela de seguranca final e emite dois bipes curtos.
        if utime.ticks_diff(utime.ticks_ms(), self._finalize_start_ms) >= FINALIZE_DELAY_MS:
            print("[CMD] Ciclo concluido. Emitindo bipes de finalizacao.")
            for _ in range(2):
                self.buzzer.value(1)
                utime.sleep_ms(120)
                self.buzzer.value(0)
                utime.sleep_ms(120)
            self._enter_idle()

    # ─────────────────────────────────────────
    #  LOOP PRINCIPAL
    # ─────────────────────────────────────────
    def run(self):
        # Exibe cabeçalho de inicialização do sistema.
        print("=" * 60)
        print("  ESTAÇÃO DE COMANDO — Sistema de Ignição LoRa 433 MHz")
        print("=" * 60)
        self._enter_idle()

        while True:
            if self.state == State.IDLE:
                self._handle_idle()
            elif self.state == State.ARMING:
                self._handle_arming()
            elif self.state == State.TRANSMITTING:
                self._handle_transmitting()
            elif self.state == State.CONFIRMED:
                self._handle_confirmed()

            # Pequena pausa para manter a execução responsiva sem bloquear demais.
            utime.sleep_ms(10)


# ╔══════════════════════════════════════════════════════════════╗
# ║                    PONTO DE ENTRADA                         ║
# ╚══════════════════════════════════════════════════════════════╝
if __name__ == "__main__":
    station = CommandStation()
    station.run()