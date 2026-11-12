"""Estacao de comando - ESP32 DevKit V1 (30 pinos).

A mesma placa da estacao de ignicao. Aqui ficam o botao, o OLED e o
buzzer; rele, Q1 e Q2 nao sao montados nesta variante.

Pinos:
  LoRa SCK=18  MISO=19  MOSI=23  CS=4  RESET=16  DIO0=17
  LED status=25  LED vermelho=12  LED do botao=26
  Botao=27 (ativo em baixo, pull-up interno)
  Buzzer=14
  OLED SDA=21  SCL=22
"""

from machine import Pin, SPI, I2C, WDT, PWM
import utime
import sys
import protocolo_lora

try:
    import uselect as select
except ImportError:
    import select


# ─────────────────────────────────────────────────────────────────
#  Driver LoRa (SX127x): prioridade para biblioteca externa,
#  com fallback para driver nativo em SPI se sx127x.py nao existir.
# ─────────────────────────────────────────────────────────────────
USE_SX127X_DRIVER = False

if USE_SX127X_DRIVER:
    try:
        from sx127x import SX127x
        SX127X_DRIVER_AVAILABLE = True
    except Exception as exc:
        SX127X_DRIVER_AVAILABLE = False
        print("[WARN] sx127x indisponivel ({}) - usando driver nativo SX1278.".format(exc))
else:
    SX127X_DRIVER_AVAILABLE = False
    print("[BOOT] Driver nativo SX1278 selecionado (sx127x desativado).")



# ── Pinos SPI / LoRa ─────────────────────────────────────────────
PIN_MOSI  = 23
PIN_MISO  = 19
PIN_SCK   = 18
PIN_CS    = 4
PIN_RESET = 16
PIN_DIO0  = 17

# ── Periféricos ──────────────────────────────────────────────────
PIN_LED_YELLOW = 25  # status / link / armamento
PIN_LED_RED    = 12  # ACK e confirmacao
PIN_LED_LINK   = 26  # LED do botao
PIN_BUZZER     = 14
PIN_BUTTON     = 27  # ativo em baixo, pull-up interno

# ── OLED ─────────────────────────────────────────────────────────
PIN_I2C_SDA = 21
PIN_I2C_SCL = 22
OLED_ADDR   = 0x3C
OLED_W      = 128
OLED_H      = 64

# ── Tempos (ms) ──────────────────────────────────────────────────
SERIAL_ARM_ENABLED = False    # nunca habilitar no firmware de voo

HOLD_REQUIRED_MS   = 10_000  # tempo que o botão deve ficar pressionado
DEBOUNCE_MS        = 50      # janela de debounce
BLINK_INTERVAL_MS  = 250     # cadência do LED amarelo / buzzer
RETRANSMIT_MS      = 200     # intervalo entre re-envios do ARM_CONFIRMED
PING_INTERVAL_MS   = 1_000   # intervalo de PING no IDLE
LINK_TIMEOUT_MS    = 3_000   # sem nenhum quadro valido neste tempo = aborta
LINK_BLINK_MS      = 250     # pisca LED de link enquanto desconectado
FINALIZE_DELAY_MS  = 3_000   # espera apos ignicao concluida

# ── Mensagens LoRa ───────────────────────────────────────────────
MSG_ARM    = "ARM_CONFIRMED"
MSG_ABORT  = "ABORT"
MSG_ACK    = "ACK"
MSG_DONE   = "IGNITION_COMPLETE"
MSG_PING   = "PING"
MSG_PONG   = "PONG"
MSG_STATUS = "STATUS:"

STATUS_VALIDOS = (
    "AGUARDANDO",
    "CONTAGEM",
    "IGNICAO",
    "COMPLETO",
    "ABORT",
    "BLOQUEADO",
)

# ── Parâmetros LoRa (SX1278 @ 433 MHz) ──────────────────────────
LORA_PARAMS = {
    "frequency"         : 433e6,
    "bandwidth"         : 125e3,
    "spreading_factor"  : 7,
    "coding_rate"       : 5,        # 4/5
    "output_power"      : 17,       # dBm (máx 20)
    "rx_crc"            : True,
}

# ── OLED ─────────────────────────────────────────────────────────
oled = None
OLED_OK = False

try:
    from ssd1306 import SSD1306_I2C
    _i2c = I2C(0, scl=Pin(PIN_I2C_SCL), sda=Pin(PIN_I2C_SDA), freq=100000)
    if OLED_ADDR in _i2c.scan():
        oled = SSD1306_I2C(OLED_W, OLED_H, _i2c, OLED_ADDR)
        OLED_OK = True
        print("[BOOT] OLED encontrado em 0x{:02X}.".format(OLED_ADDR))
    else:
        print("[BOOT] OLED ausente no I2C - seguindo sem display.")
except Exception as exc:
    print("[BOOT] I2C/OLED indisponivel ({}) - seguindo sem display.".format(exc))


def oled_show(linhas):
    if not OLED_OK:
        return
    try:
        oled.fill(0)
        y = 0
        for linha in linhas[:8]:
            oled.text(str(linha)[:16], 0, y)
            y += 8
        oled.show()
    except Exception:
        pass


def oled_logo():
    if not OLED_OK:
        return
    try:
        from logo_serra import LOGO_BYTES, LOGO_ALTURA, LOGO_LARGURA, LOGO_X
        oled.fill(0)
        for pagina in range(LOGO_ALTURA // 8):
            ini_logo = pagina * LOGO_LARGURA
            ini_tela = pagina * OLED_W + LOGO_X
            oled.buffer[ini_tela:ini_tela + LOGO_LARGURA] = LOGO_BYTES[ini_logo:ini_logo + LOGO_LARGURA]
        oled.text("SERRA ROCKETRY", 8, 56)
        oled.show()
        utime.sleep_ms(1200)
    except Exception:
        pass


# Zelda's Lullaby: (frequencia em Hz, duracao em ms). 0 = pausa.
NOTA_B4 = 494
NOTA_D5 = 587
NOTA_A4 = 440
NOTA_FS4 = 370
NOTA_G4 = 392

SEQUENCIA_ZELDA = (
    (NOTA_B4, 300), (0, 40),
    (NOTA_D5, 300), (0, 40),
    (NOTA_A4, 600), (0, 60),
    (NOTA_B4, 300), (0, 40),
    (NOTA_D5, 300), (0, 40),
    (NOTA_A4, 600), (0, 60),
    (NOTA_B4, 300), (0, 40),
    (NOTA_D5, 300), (0, 40),
    (NOTA_A4, 300), (0, 40),
    (NOTA_FS4, 300), (0, 40),
    (NOTA_G4, 300), (0, 40),
    (NOTA_A4, 600), (0, 100),
)

# Trecho do tema do Mario para o fim do estagio.
NOTA_E5 = 659
NOTA_C5 = 523
NOTA_G5 = 784
NOTA_G4 = 392

SEQUENCIA_MARIO = (
    (NOTA_E5, 120), (0, 60),
    (NOTA_E5, 120), (0, 60),
    (NOTA_E5, 120), (0, 60),
    (NOTA_C5, 120), (0, 60),
    (NOTA_E5, 120), (0, 60),
    (NOTA_G5, 240), (0, 120),
    (NOTA_G4, 240), (0, 200),
)


class Buzzer:
    def __init__(self, pin):
        self.pin = pin
        self._notas = []
        self._indice = 0
        self._prazo = 0
        self._pwm = None

    def _parar_pwm(self):
        if self._pwm is not None:
            try:
                self._pwm.deinit()
            except Exception:
                pass
            self._pwm = None
        self.pin.value(0)

    def _aplicar(self, indice, agora):
        freq, duracao = self._notas[indice]
        if freq <= 0:
            self._parar_pwm()
        else:
            try:
                if self._pwm is None:
                    self._pwm = PWM(self.pin)
                self._pwm.freq(freq)
                try:
                    self._pwm.duty_u16(32768)
                except AttributeError:
                    self._pwm.duty(512)
            except Exception:
                self._parar_pwm()
        self._prazo = utime.ticks_add(agora, duracao)

    def tocar(self, sequencia, agora=None):
        if agora is None:
            agora = utime.ticks_ms()
        self.parar()
        self._notas = list(sequencia)
        self._indice = 0
        if self._notas:
            self._aplicar(0, agora)

    def atualizar(self, agora):
        if not self._notas:
            return
        if utime.ticks_diff(agora, self._prazo) < 0:
            return
        self._indice += 1
        if self._indice >= len(self._notas):
            self.parar()
            return
        self._aplicar(self._indice, agora)

    def parar(self):
        self._notas = []
        self._parar_pwm()

    @property
    def tocando(self):
        return bool(self._notas)


# ── Registradores e flags do SX1278 (fallback nativo) ──────────
REG_FIFO            = 0x00
REG_OP_MODE         = 0x01
REG_FRF_MSB         = 0x06
REG_FRF_MID         = 0x07
REG_FRF_LSB         = 0x08
REG_PA_CONFIG       = 0x09
REG_LNA             = 0x0C
REG_FIFO_ADDR_PTR   = 0x0D
REG_FIFO_TX_BASE    = 0x0E
REG_FIFO_RX_BASE    = 0x0F
REG_FIFO_RX_CURRENT = 0x10
REG_IRQ_FLAGS       = 0x12
REG_RX_NB_BYTES     = 0x13
REG_MODEM_CONFIG1   = 0x1D
REG_MODEM_CONFIG2   = 0x1E
REG_PREAMBLE_MSB    = 0x20
REG_PREAMBLE_LSB    = 0x21
REG_PAYLOAD_LENGTH  = 0x22
REG_MODEM_CONFIG3   = 0x26
REG_SYNC_WORD       = 0x39
REG_VERSION         = 0x42

MODE_SLEEP   = 0x00
MODE_STDBY   = 0x01
MODE_TX      = 0x03
MODE_RX_CONT = 0x05
MODE_LORA    = 0x80

IRQ_RX_DONE           = 0x40
IRQ_TX_DONE           = 0x08
IRQ_PAYLOAD_CRC_ERROR = 0x20


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


class LoRaRadio:
    """
    Abstracao sobre o radio SX1278.

    Ordem de tentativa:
    1) Driver externo sx127x.py (se instalado);
    2) Driver nativo por registradores SPI;
    3) Modo mock (sem transmissao real).
    """

    def __init__(self):
        self._lora = None
        self._backend = "mock"

        self._cs = Pin(PIN_CS, Pin.OUT, value=1)
        self._reset = Pin(PIN_RESET, Pin.OUT, value=1)
        self._dio0 = Pin(PIN_DIO0, Pin.IN)

        self._spi = self._criar_spi()
        if self._spi is None:
            print("[LoRa] SPI indisponivel - modo mock.")
            return

        if SX127X_DRIVER_AVAILABLE:
            try:
                self._lora = SX127x(
                    self._spi,
                    pins={
                        "cs"    : self._cs,
                        "reset" : self._reset,
                        "dio0"  : self._dio0,
                    },
                    parameters=LORA_PARAMS,
                )
                self._backend = "sx127x"
                print("[LoRa] SX1278 inicializado em 433 MHz (driver sx127x).")
                return
            except Exception as exc:
                if "unexpected keyword argument 'pins'" in str(exc):
                    print("[INFO] API sx127x legada detectada - tentando compatibilidade.")
                else:
                    print(f"[WARN] Falha no sx127x padrao ({exc}) - tentando compatibilidade.")
                try:
                    self._lora = self._init_legacy_sx127x()
                    self._backend = "sx127x"
                    print("[LoRa] SX1278 inicializado em 433 MHz (sx127x legacy compat).")
                    return
                except Exception as legacy_exc:
                    print(f"[WARN] Falha na compatibilidade sx127x ({legacy_exc}) - fallback nativo.")

        if self._init_native():
            self._backend = "native"
            print("[LoRa] SX1278 inicializado em 433 MHz (driver nativo SPI).")
        else:
            print("[LoRa] Modo MOCK ativo (sem resposta do SX1278).")

    def _criar_spi(self):
        for spi_id in (2, 1):
            try:
                return SPI(
                    spi_id,
                    baudrate=1_000_000,
                    polarity=0,
                    phase=0,
                    sck=Pin(PIN_SCK),
                    mosi=Pin(PIN_MOSI),
                    miso=Pin(PIN_MISO),
                )
            except Exception:
                pass
        return None

    def _legacy_transfer(self, pin, address, value=0x00):
        response = bytearray(1)
        pin.value(0)
        self._spi.write(bytes([address]))
        self._spi.write_readinto(bytes([value]), response)
        pin.value(1)
        return response

    def _init_legacy_sx127x(self):
        legacy_params = {
            "frequency"      : int(LORA_PARAMS["frequency"]),
            "tx_power_level" : int(LORA_PARAMS["output_power"]),
            "signal_bandwidth": int(LORA_PARAMS["bandwidth"]),
            "spreading_factor": int(LORA_PARAMS["spreading_factor"]),
            "coding_rate"    : int(LORA_PARAMS["coding_rate"]),
            "preamble_length" : 8,
            "implicitHeader" : False,
            "sync_word"      : 0x12,
            "enable_CRC"     : bool(LORA_PARAMS["rx_crc"]),
        }

        radio = SX127x(parameters=legacy_params)
        radio.pin_ss = self._cs
        radio.pin_RxDone = None
        radio.transfer = self._legacy_transfer
        if hasattr(radio, "init"):
            radio.init()
        return radio

    def _sx_received_packet(self):
        if not self._lora:
            return False

        if hasattr(self._lora, "received_packet"):
            return bool(self._lora.received_packet())

        if hasattr(self._lora, "receivedPacket"):
            return bool(self._lora.receivedPacket())

        return False

    def _sx_read_payload(self):
        if not self._lora or not hasattr(self._lora, "read_payload"):
            return None

        try:
            return self._lora.read_payload(with_header=False)
        except TypeError:
            return self._lora.read_payload()

    def _native_write_reg(self, reg, value):
        self._cs.value(0)
        self._spi.write(bytes([reg | 0x80, value & 0xFF]))
        self._cs.value(1)

    def _native_read_reg(self, reg):
        self._cs.value(0)
        self._spi.write(bytes([reg & 0x7F]))
        result = self._spi.read(1)
        self._cs.value(1)
        return result[0]

    def _native_read_buf(self, reg, length):
        self._cs.value(0)
        self._spi.write(bytes([reg & 0x7F]))
        result = self._spi.read(length)
        self._cs.value(1)
        return result

    def _native_write_fifo(self, payload):
        self._cs.value(0)
        self._spi.write(bytes([REG_FIFO | 0x80]))
        self._spi.write(payload)
        self._cs.value(1)

    def _native_reset(self):
        self._reset.value(0)
        utime.sleep_ms(20)
        self._reset.value(1)
        utime.sleep_ms(100)

    def _init_native(self, verbose=True):
        if self._spi is None:
            return False
        self._native_reset()

        version = self._native_read_reg(REG_VERSION)
        if version != 0x12:
            if verbose:
                print(f"[WARN] SX1278 nao detectado no driver nativo (REG_VERSION=0x{version:02X}).")
            return False

        self._native_write_reg(REG_OP_MODE, MODE_LORA | MODE_SLEEP)
        utime.sleep_ms(10)

        frf = int((int(LORA_PARAMS["frequency"]) * (1 << 19)) / 32_000_000)
        self._native_write_reg(REG_FRF_MSB, (frf >> 16) & 0xFF)
        self._native_write_reg(REG_FRF_MID, (frf >> 8) & 0xFF)
        self._native_write_reg(REG_FRF_LSB, frf & 0xFF)

        self._native_write_reg(REG_PA_CONFIG, 0x8F)
        self._native_write_reg(REG_LNA, 0x23)
        self._native_write_reg(REG_MODEM_CONFIG1, 0x72)
        self._native_write_reg(REG_MODEM_CONFIG2, 0x74)
        self._native_write_reg(REG_MODEM_CONFIG3, 0x04)
        self._native_write_reg(REG_PREAMBLE_MSB, 0x00)
        self._native_write_reg(REG_PREAMBLE_LSB, 0x08)
        self._native_write_reg(REG_SYNC_WORD, 0x12)
        self._native_write_reg(REG_FIFO_TX_BASE, 0x00)
        self._native_write_reg(REG_FIFO_RX_BASE, 0x00)

        self._native_write_reg(REG_OP_MODE, MODE_LORA | MODE_RX_CONT)
        utime.sleep_ms(10)
        return True

    def tentar_nativo(self):
        """Tenta reconhecer o SX1278 novamente sem reiniciar a placa."""
        if self._backend in ("native", "sx127x"):
            return True
        if self._spi is None:
            self._spi = self._criar_spi()
        if self._spi is None:
            return False
        if self._init_native(verbose=False):
            self._backend = "native"
            print("[LoRa] SX1278 reconhecido; backend native.")
            return True
        return False

    def verificar(self):
        """Atualiza o estado do radio para o OLED mostrar OK ou MOCK."""
        if self._backend == "sx127x":
            return True
        if self._backend == "mock":
            return self.tentar_nativo()
        try:
            version = self._native_read_reg(REG_VERSION)
        except Exception:
            version = 0
        if version != 0x12:
            print("[LoRa] SX1278 nao responde mais; voltando para mock.")
            self._backend = "mock"
            return False
        return True

    def _native_send_packet(self, payload):
        if not payload:
            return

        self._native_write_reg(REG_OP_MODE, MODE_LORA | MODE_STDBY)
        self._native_write_reg(REG_FIFO_ADDR_PTR, 0x00)
        self._native_write_reg(REG_PAYLOAD_LENGTH, len(payload))
        self._native_write_fifo(payload)
        self._native_write_reg(REG_IRQ_FLAGS, 0xFF)

        self._native_write_reg(REG_OP_MODE, MODE_LORA | MODE_TX)

        t0 = utime.ticks_ms()
        tx_done = False
        while utime.ticks_diff(utime.ticks_ms(), t0) < 300:
            if self._native_read_reg(REG_IRQ_FLAGS) & IRQ_TX_DONE:
                tx_done = True
                break
            utime.sleep_ms(1)

        self._native_write_reg(REG_IRQ_FLAGS, 0xFF)
        self._native_write_reg(REG_OP_MODE, MODE_LORA | MODE_RX_CONT)

        if not tx_done:
            print("[WARN] Timeout aguardando TX_DONE no SX1278.")

    def _native_receive_packet(self):
        flags = self._native_read_reg(REG_IRQ_FLAGS)
        if not (flags & IRQ_RX_DONE):
            return None

        self._native_write_reg(REG_IRQ_FLAGS, 0xFF)

        if flags & IRQ_PAYLOAD_CRC_ERROR:
            return None

        nb_bytes = self._native_read_reg(REG_RX_NB_BYTES)
        current_addr = self._native_read_reg(REG_FIFO_RX_CURRENT)
        self._native_write_reg(REG_FIFO_ADDR_PTR, current_addr)
        raw = self._native_read_buf(REG_FIFO, nb_bytes)

        try:
            return raw.decode("utf-8", "ignore").strip()
        except Exception:
            return None

    def send(self, message):
        """Transmite uma mensagem pela interface LoRa e mostra log local."""
        try:
            if self._backend == "sx127x":
                self._lora.println(message)
            elif self._backend == "native":
                self._native_send_packet(message.encode("utf-8"))
        except Exception as exc:
            print(f"[WARN] Falha no envio LoRa ({self._backend}): {exc}")
        print(f"[LoRa TX] → {message}")

    @property
    def backend(self):
        return self._backend

    def receive(self):
        """
        Lê um pacote LoRa não bloqueante, se houver.

        Retorna a mensagem decodificada ou None quando não há nenhum pacote.
        """
        try:
            if self._backend == "sx127x" and self._sx_received_packet():
                payload = self._sx_read_payload()
                if payload is None:
                    return None
                msg = bytes(payload).decode("utf-8", "ignore").strip()
                print(f"[LoRa RX] ← {msg}")
                return msg

            if self._backend == "native":
                msg = self._native_receive_packet()
                if msg:
                    print(f"[LoRa RX] ← {msg}")
                    return msg
        except Exception as exc:
            print(f"[WARN] Falha na leitura LoRa ({self._backend}): {exc}")
        return None


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
        self.musica      = Buzzer(self.buzzer)
        self.led_link   = Pin(PIN_LED_LINK,   Pin.OUT, value=0)
        self.button     = Pin(PIN_BUTTON,     Pin.IN,  Pin.PULL_UP)
        self.lora       = LoRaRadio()
        print(f"[CMD] Backend LoRa ativo: {self.lora.backend}")

        # Estado atual da maquina.
        self.state = State.IDLE

        # Tempos de controle usados para armamento, piscar e transmissao.
        self._press_start_ms = 0
        self._last_blink_ms = 0
        self._last_tx_ms = 0
        self._ack_received = False
        self._musica_iniciada = False
        self._musica_fim_ms = 0
        self._last_countdown_s = None

        # Debounce do botao para evitar leituras falsas.
        self._last_btn_change_ms = 0
        self._btn_stable_state = True   # True significa botao solto (pull-up)

        # Estado de toggle para o efeito de piscar.
        self._blink_on = False

        # Controle de comandos via serial (Thonny).
        self._serial_arm = False
        self._serial_abort = False
        self._serial_buf = ""
        self._serial_mode = False

        # Estado de link com a estacao de ignicao.
        self._link_ok = False
        self._last_ping_ms = 0
        self._last_lora_check_ms = 0
        self._last_peer_ms = None
        self._last_no_link_warn_ms = 0
        self._last_link_blink_ms = 0
        self._last_mock_warn_ms = 0
        self._need_release = True
        self._ciclo = 0
        self._ultimo_ciclo_confirmado = 0
        self.codec = protocolo_lora.Codec()
        self.ign_status = "AGUARDANDO"
        self.last_msg = ""
        self._last_display_ms = 0

        try:
            self._wdt = WDT(timeout=8000)
        except Exception:
            self._wdt = None

    # ─────────────────────────────────────────
    #  COMANDOS SERIAIS (Thonny)
    # ─────────────────────────────────────────
    def _check_serial(self):
        """Le comandos do console serial sem bloquear."""
        try:
            ready = select.select([sys.stdin], [], [], 0)[0]
        except Exception:
            return
        if sys.stdin not in ready:
            return

        try:
            ch = sys.stdin.read(1)
        except Exception:
            return
        if not ch:
            return

        if ch in ("\r", "\n"):
            cmd = self._serial_buf.strip().lower()
            self._serial_buf = ""
            if cmd:
                self._process_serial(cmd)
        elif len(self._serial_buf) < 32:
            self._serial_buf += ch

    def _process_serial(self, cmd):
        if cmd == "arm":
            if not SERIAL_ARM_ENABLED:
                print("[SERIAL] arm desabilitado no firmware de voo.")
                return
            if self.state != State.IDLE:
                print("[SERIAL] arm ignorado no estado {}.".format(self.state))
                return
            if self._button_pressed():
                print("[SERIAL] solte o botao antes de armar.")
                return
            print("[SERIAL] ARM")
            self._serial_arm = True
        elif cmd == "abort":
            if self.state not in (State.ARMING, State.TRANSMITTING):
                print("[SERIAL] abort ignorado no estado {}.".format(self.state))
                return
            print("[SERIAL] ABORT")
            self._serial_abort = True
        elif cmd == "status":
            print("[SERIAL] Estado: {}".format(self.state))
            print("[SERIAL] Link: {}".format("OK" if self._link_ok else "PERDIDO"))
            print("[SERIAL] Ignicao: {}".format(self.ign_status))
            print("[SERIAL] Ciclo: {}".format(self._ciclo))
        elif cmd == "ping":
            self._send(MSG_PING)
        else:
            print("[SERIAL] Comando desconhecido: {}".format(cmd))

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
        self.musica.parar()
        self._blink_on = False

    def _send(self, body, ciclo=0):
        self.lora.send(self.codec.encode(body, ciclo))

    def _note_status(self, body):
        if body and body.startswith(MSG_STATUS):
            status = body[len(MSG_STATUS):]
            if status in STATUS_VALIDOS:
                self.ign_status = status

    def _handle_status(self, body, ciclo):
        if not body or not body.startswith(MSG_STATUS):
            return False
        status = body[len(MSG_STATUS):]
        if status == "COMPLETO":
            if ciclo == self._ciclo and ciclo > self._ultimo_ciclo_confirmado:
                self._enter_confirmed(ciclo)
                return True
            return False
        if status in ("ABORT", "BLOQUEADO"):
            if self._ciclo > 0 and ciclo == self._ciclo:
                print("[CMD] Ignicao reportou {}; parando ARM.".format(status))
                self._enter_aborting(enviar=False)
                return True
        return False

    def _receive_event(self, now, tratar_status=True):
        """Le e valida um quadro. Retorna (body, ciclo, mudou_de_estado)."""
        bruto = self.lora.receive()
        if not bruto:
            return None, 0, False

        decodificado = self.codec.decode(bruto)
        if not decodificado:
            print("[CMD] Quadro LoRa ignorado.")
            return None, 0, False

        body, ciclo = decodificado
        self._last_peer_ms = now
        self._note_status(body)
        if tratar_status and self._handle_status(body, ciclo):
            return body, ciclo, True
        return body, ciclo, False

    def _link_ok_now(self, now):
        if self._last_peer_ms is None:
            return False
        return utime.ticks_diff(now, self._last_peer_ms) <= LINK_TIMEOUT_MS

    def _ping_if_due(self, now):
        if utime.ticks_diff(now, self._last_ping_ms) >= PING_INTERVAL_MS:
            self._last_ping_ms = now
            self._send(MSG_PING)

    def _refresh_link(self, now):
        """Mantem PING/PONG ativo apenas no IDLE."""
        self._ping_if_due(now)

        incoming, ciclo, mudou = self._receive_event(now, tratar_status=False)
        if mudou:
            return
        if incoming == MSG_PING:
            self._send(MSG_PONG)
        elif (
            incoming == MSG_DONE
            and ciclo == self._ciclo
            and ciclo > self._ultimo_ciclo_confirmado
        ):
            self.last_msg = "COMPLETE"
            self._enter_confirmed(ciclo)
            return

        link_was_ok = self._link_ok
        self._link_ok = self._link_ok_now(now)
        if self._link_ok != link_was_ok:
            status = "OK" if self._link_ok else "PERDIDO"
            print("[CMD] Link com ignicao: {}".format(status))
        if self._link_ok:
            self.led_link.value(1)
            self.led_yellow.value(1)
        else:
            self.led_yellow.value(0)
            if utime.ticks_diff(now, self._last_link_blink_ms) >= LINK_BLINK_MS:
                self._last_link_blink_ms = now
                self.led_link.value(0 if self.led_link.value() else 1)

    def _blink_tick(self):
        """Alterna apenas o LED amarelo em BLINK_INTERVAL_MS."""
        now = utime.ticks_ms()
        if utime.ticks_diff(now, self._last_blink_ms) >= BLINK_INTERVAL_MS:
            self._last_blink_ms = now
            self._blink_on = not self._blink_on
            self.led_yellow.value(self._blink_on)

    # ─────────────────────────────────────────
    #  TRANSIÇÕES DE ESTADO
    # ─────────────────────────────────────────
    def _enter_idle(self):
        self._all_off()
        self._serial_mode = False
        self._serial_arm = False
        self._serial_abort = False
        self.state = State.IDLE
        print("[CMD] Estado: IDLE - aguardando botao.")

    def _enter_arming(self):
        self.musica.parar()
        self._ciclo = (self._ciclo + 1) & 0x7FFFFFFF
        if self._ciclo == 0:
            self._ciclo = 1
        self._press_start_ms = utime.ticks_ms()
        self._last_blink_ms = self._press_start_ms
        self._last_tx_ms = utime.ticks_add(self._press_start_ms, -RETRANSMIT_MS)
        self._ack_received = False
        self._last_countdown_s = None
        self._serial_arm = False
        self._serial_abort = False
        self.state = State.ARMING
        print(
            "[CMD] Estado: ARMING - mantenha o botao ate CONFIRMADO (ciclo {}).".format(
                self._ciclo
            )
        )

    def _enter_transmitting(self):
        self._last_tx_ms = 0
        self.led_red.value(1 if self._ack_received else 0)
        self.led_yellow.value(1)
        self.musica.parar()
        self.state = State.TRANSMITTING
        print("[CMD] Estado: TRANSMITTING - mantenha o botao ate CONFIRMADO.")

    def _enter_confirmed(self, ciclo=None):
        if self.state == State.CONFIRMED:
            if ciclo is not None and ciclo > self._ultimo_ciclo_confirmado:
                self._ultimo_ciclo_confirmado = ciclo
            return
        if ciclo is not None:
            self._ultimo_ciclo_confirmado = ciclo
        self._all_off()
        self.led_red.value(1)
        self.ign_status = "COMPLETO"
        self.last_msg = "COMPLETE"
        self._musica_iniciada = False
        self._musica_fim_ms = 0
        self._need_release = True
        self.state = State.CONFIRMED
        print("[CMD] Estado: CONFIRMED - IGNITION_COMPLETE recebido.")

    def _enter_aborting(self, enviar=True):
        if enviar:
            # Duas copias: se a primeira colidir com um ACK/STATUS, a segunda
            # ainda chega. O timeout de 500 ms da ignicao e o fallback.
            for _ in range(2):
                self._send(MSG_ABORT, self._ciclo)
                utime.sleep_ms(20)
        self._all_off()
        self._need_release = True
        self.state = State.ABORTING
        if enviar:
            print("[CMD] Estado: ABORTING - ABORT enviado.")
        else:
            print("[CMD] Estado: ABORTING - ignicao ja abortou.")
        self._enter_idle()

    # ─────────────────────────────────────────
    #  HANDLERS DE CADA ESTADO
    # ─────────────────────────────────────────
    def _handle_idle(self):
        now = utime.ticks_ms()
        self._check_serial()

        # Reavalia o radio a cada 2 s para o OLED refletir LORA OK/MOCK.
        if utime.ticks_diff(now, self._last_lora_check_ms) >= 2000:
            self._last_lora_check_ms = now
            self.lora.verificar()

        self._refresh_link(now)

        if self.lora.backend == "mock" and utime.ticks_diff(now, self._last_mock_warn_ms) >= 3000:
            self._last_mock_warn_ms = now
            print("[CMD] RADIO EM MOCK: verifique cabos SPI/energia do SX1278 no comando.")

        if self._need_release:
            if self._button_pressed():
                return
            self._need_release = False
            return

        if self._serial_arm:
            self._serial_arm = False
            if not self._link_ok:
                print("[CMD] Sem link LoRa. Armamento bloqueado.")
                return
            self._serial_mode = True
            self._enter_arming()
            return

        if self._button_pressed():
            if not self._link_ok:
                if utime.ticks_diff(now, self._last_no_link_warn_ms) >= 1_000:
                    self._last_no_link_warn_ms = now
                    print("[CMD] Sem link LoRa ativo. Armamento bloqueado.")
                return
            self._enter_arming()

    def _handle_arming(self):
        self._check_serial()

        if self._serial_abort:
            self._serial_abort = False
            print("[CMD] ABORT via serial.")
            self._enter_aborting()
            return

        now = utime.ticks_ms()

        incoming, ciclo_in, mudou = self._receive_event(now)
        if mudou:
            return
        if incoming == MSG_ACK:
            if ciclo_in == self._ciclo and not self._ack_received:
                self._ack_received = True
                self.led_red.value(1)
                self.last_msg = "ACK"
                print("[CMD] ACK recebido da base de ignicao.")
        elif incoming == MSG_DONE:
            if ciclo_in == self._ciclo:
                self.last_msg = "COMPLETE"
                self._enter_confirmed(ciclo_in)
                return
        elif incoming == MSG_PING:
            self._send(MSG_PONG)

        if not (SERIAL_ARM_ENABLED and self._serial_mode) and not self._button_pressed():
            print("[CMD] Botao solto - ABORT imediato.")
            self._enter_aborting()
            return

        if utime.ticks_diff(now, self._last_tx_ms) >= RETRANSMIT_MS:
            self._last_tx_ms = now
            self._send(MSG_ARM, self._ciclo)

        self._link_ok = self._link_ok_now(now)
        if not self._link_ok:
            print("[CMD] Link instavel - ABORT imediato.")
            self._enter_aborting()
            return

        self._blink_tick()

        elapsed = utime.ticks_diff(now, self._press_start_ms)
        remaining = max(0, (HOLD_REQUIRED_MS - elapsed) // 1000)
        if remaining != self._last_countdown_s:
            self._last_countdown_s = remaining
            self.musica.tocar([(2000, 60), (0, 940)], now)
            print("[CMD] Armando... {} s restantes.".format(remaining))

        if elapsed >= HOLD_REQUIRED_MS:
            self._enter_transmitting()

    def _handle_transmitting(self):
        self._check_serial()

        if self._serial_abort:
            self._serial_abort = False
            print("[CMD] ABORT via serial.")
            self._enter_aborting()
            return

        now = utime.ticks_ms()

        # Primeiro o radio: um IGNITION_COMPLETE atrasado vence a soltura.
        incoming, ciclo_in, mudou = self._receive_event(now)
        if mudou:
            return
        if incoming == MSG_ACK:
            if ciclo_in == self._ciclo and not self._ack_received:
                self._ack_received = True
                self.led_red.value(1)
                self.last_msg = "ACK"
                print("[CMD] ACK recebido da base de ignicao.")
        elif incoming == MSG_DONE:
            if ciclo_in == self._ciclo:
                self.last_msg = "COMPLETE"
                self._enter_confirmed(ciclo_in)
                return
        elif incoming == MSG_PING:
            self._send(MSG_PONG)

        if not (SERIAL_ARM_ENABLED and self._serial_mode) and not self._button_pressed():
            print("[CMD] Botao solto - ABORT imediato.")
            self._enter_aborting()
            return

        if utime.ticks_diff(now, self._last_tx_ms) >= RETRANSMIT_MS:
            self._last_tx_ms = now
            self._send(MSG_ARM, self._ciclo)

        self._link_ok = self._link_ok_now(now)
        if not self._link_ok:
            print("[CMD] Link instavel - ABORT imediato.")
            self._enter_aborting()
            return

    def _handle_confirmed(self):
        agora = utime.ticks_ms()

        if not self._musica_iniciada:
            print("[CMD] Ignicao concluida. Tocando o tema.")
            self.musica.tocar(SEQUENCIA_MARIO, agora)
            self._musica_iniciada = True
            return

        if self.musica.tocando:
            return

        if self._musica_fim_ms == 0:
            self._musica_fim_ms = agora

        if utime.ticks_diff(agora, self._musica_fim_ms) >= FINALIZE_DELAY_MS:
            self._enter_idle()

    def _update_display(self):
        now = utime.ticks_ms()
        if utime.ticks_diff(now, self._last_display_ms) < 500:
            return
        self._last_display_ms = now

        segurar = False
        if self.state == State.ARMING:
            restante = max(
                0,
                (HOLD_REQUIRED_MS - utime.ticks_diff(now, self._press_start_ms) + 999) // 1000,
            )
            cmd = "ARMANDO {}s".format(restante)
            segurar = True
        elif self.state == State.TRANSMITTING:
            cmd = "SEGURE"
            segurar = True
        elif self.state == State.CONFIRMED:
            cmd = "CONFIRMADO"
        else:
            cmd = "IDLE"

        lora = "OK" if self.lora.backend in ("native", "sx127x") else "MOCK"

        linhas = [
            "SERRA ROCKETRY",
            "CMD  " + cmd,
        ]
        if segurar:
            linhas.append("ATE CONFIRMAR")
        linhas.extend([
            "LINK " + ("OK" if self._link_ok else "--"),
            "LORA " + lora,
            "IGN  " + self.ign_status,
            "MSG  " + (self.last_msg or "-"),
            "CIC  " + str(self._ciclo),
        ])
        oled_show(linhas)

    # ─────────────────────────────────────────
    #  LOOP PRINCIPAL
    # ─────────────────────────────────────────
    def run(self):
        print("=" * 60)
        print("  ESTACAO DE COMANDO - LoRa 433 MHz")
        print("=" * 60)
        oled_logo()
        self._enter_idle()
        self.musica.tocar(SEQUENCIA_ZELDA)

        while True:
            if self.state == State.IDLE:
                self._handle_idle()
            elif self.state == State.ARMING:
                self._handle_arming()
            elif self.state == State.TRANSMITTING:
                self._handle_transmitting()
            elif self.state == State.CONFIRMED:
                self._handle_confirmed()

            self.musica.atualizar(utime.ticks_ms())
            self._update_display()
            if self._wdt:
                self._wdt.feed()
            utime.sleep_ms(10)


if __name__ == "__main__":
    station = CommandStation()
    station.run()
