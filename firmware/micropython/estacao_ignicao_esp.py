"""Estacao de ignicao - ESP32 DevKit V1 (30 pinos).

Mesma placa da estacao de comando. Esta variante leva rele, Q1/Q2,
LEDs e buzzer; nao tem botao, OLED, EXP nem ADC.

Pinos:
  LoRa SCK=18  MISO=19  MOSI=23  CS=4  RESET=16  DIO0=17
  RELE=32 (ativo em baixo)  GATE_1=13  GATE_2=33
  LED status=25  LED contagem=12  Buzzer=14
"""

import utime
from machine import Pin, SPI, WDT

USE_SX127X_DRIVER = False

if USE_SX127X_DRIVER:
    try:
        from sx127x import SX127x
        SX127X_DRIVER_AVAILABLE = True
    except Exception as exc:
        SX127X_DRIVER_AVAILABLE = False
        print("[WARN] sx127x indisponivel ({}); usando driver nativo.".format(exc))
else:
    SX127X_DRIVER_AVAILABLE = False
    print("[BOOT] Driver nativo SX1278.")

LORA_PARAMS = {
    "frequency"       : 433e6,
    "bandwidth"       : 125e3,
    "spreading_factor": 7,
    "coding_rate"     : 5,
    "output_power"    : 17,
    "rx_crc"          : True,
}

# --- pinos ---
SPI_ID_CANDIDATES = (2, 1)
SPI_SCK = 18
SPI_MOSI = 23
SPI_MISO = 19
SPI_DIO0 = 17

PIN_LORA_CS_NUM    = 4
PIN_LORA_RESET_NUM = 16
PIN_LORA_DIO0_NUM  = 17
PIN_RELE_NUM       = 32
PIN_GATE_1_NUM     = 13
PIN_GATE_2_NUM     = 33
PIN_BUZZER_NUM     = 14
PIN_STATUS_NUM     = 25
PIN_LED_COUNT_NUM  = 12

LORA_CS    = Pin(PIN_LORA_CS_NUM, Pin.OUT, value=1)
LORA_RESET = Pin(PIN_LORA_RESET_NUM, Pin.OUT, value=1)
LORA_DIO0  = Pin(PIN_LORA_DIO0_NUM, Pin.IN)

PIN_RELE       = Pin(PIN_RELE_NUM, Pin.OUT, value=1)
PIN_GATE_1     = Pin(PIN_GATE_1_NUM, Pin.OUT, value=0)
PIN_GATE_2     = Pin(PIN_GATE_2_NUM, Pin.OUT, value=0)
PIN_BUZZER     = Pin(PIN_BUZZER_NUM, Pin.OUT, value=0)
PIN_STATUS     = Pin(PIN_STATUS_NUM, Pin.OUT, value=0)
PIN_LED_COUNT  = Pin(PIN_LED_COUNT_NUM, Pin.OUT, value=0)

RELE_ACTIVE_LEVEL   = 0
RELE_INACTIVE_LEVEL = 1

def _set_rele(ligado):
    PIN_RELE.value(RELE_ACTIVE_LEVEL if ligado else RELE_INACTIVE_LEVEL)

def _set_gate1(ligado):
    PIN_GATE_1.value(1 if ligado else 0)

def _set_gate2(ligado):
    PIN_GATE_2.value(1 if ligado else 0)

def _set_status(valor):
    PIN_STATUS.value(1 if valor else 0)

def _toggle_status():
    PIN_STATUS.value(0 if PIN_STATUS.value() else 1)

def buzzer_bip(duracao_ms=100):
    PIN_BUZZER.value(1)
    utime.sleep_ms(duracao_ms)
    PIN_BUZZER.value(0)

def sinalizar_erro(n=3):
    for _ in range(n):
        buzzer_bip(80)
        utime.sleep_ms(120)

def desligar_tudo():
    _set_gate2(False)   # Q1 primeiro: corta a corrente
    _set_rele(False)    # depois o rele, sem arco
    _set_gate1(False)   # por ultimo o GND da bobina
    PIN_BUZZER.value(0)
    _set_status(False)
    PIN_LED_COUNT.value(0)

# =============================================================================
#  ENDERECOS DE REGISTRADORES DO SX1278
# =============================================================================

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
REG_DIO_MAPPING1    = 0x40
REG_VERSION         = 0x42

# Modos de operacao do SX1278
MODE_SLEEP   = 0x00
MODE_STDBY   = 0x01
MODE_TX      = 0x03
MODE_RX_CONT = 0x05
MODE_LORA    = 0x80  # Bit 7 = 1 habilita modo LoRa

# Mascaras de flag de interrupcao (registrador IRQ_FLAGS)
IRQ_RX_DONE = 0x40  # Pacote recebido com sucesso
IRQ_TX_DONE = 0x08  # Transmissao concluida

# =============================================================================
#  INICIALIZACAO DO BARRAMENTO SPI
# =============================================================================

def _init_spi():
    last_exc = None
    for spi_id in SPI_ID_CANDIDATES:
        try:
            return SPI(spi_id,
                       baudrate=1_000_000,
                       polarity=0,
                       phase=0,
                       sck=Pin(SPI_SCK),
                       mosi=Pin(SPI_MOSI),
                       miso=Pin(SPI_MISO))
        except Exception as exc:
            last_exc = exc

    raise RuntimeError("Falha ao iniciar SPI (ids {}): {}".format(SPI_ID_CANDIDATES, last_exc))


try:
    spi = _init_spi()
except Exception as exc:
    print("[ERRO] SPI indisponivel: {}".format(exc))
    spi = None

lora_driver = None
lora_backend = "native"

# =============================================================================
#  FUNCOES SPI DE BAIXO NIVEL
# =============================================================================

def _spi_write(reg, value):
    # Bit 7 = 1 indica operacao de escrita no SX1278
    LORA_CS.value(0)
    spi.write(bytes([reg | 0x80, value]))
    LORA_CS.value(1)

def _spi_read(reg):
    # Bit 7 = 0 indica operacao de leitura
    LORA_CS.value(0)
    spi.write(bytes([reg & 0x7F]))
    result = spi.read(1)
    LORA_CS.value(1)
    return result[0]

def _spi_read_buf(reg, length):
    # Leitura de multiplos bytes consecutivos do FIFO
    LORA_CS.value(0)
    spi.write(bytes([reg & 0x7F]))
    result = spi.read(length)
    LORA_CS.value(1)
    return result


def _toggle_pin(pin):
    """Alterna pinos de forma compativel com firmwares sem Pin.toggle()."""
    pin.value(0 if pin.value() else 1)

def _sx127x_legacy_transfer(pin, address, value=0x00):
    response = bytearray(1)
    pin.value(0)
    spi.write(bytes([address]))
    spi.write_readinto(bytes([value]), response)
    pin.value(1)
    return response

def _init_legacy_sx127x(frequency):
    params = {
        "frequency"      : int(frequency),
        "tx_power_level" : int(LORA_PARAMS["output_power"]),
        "signal_bandwidth": int(LORA_PARAMS["bandwidth"]),
        "spreading_factor": int(LORA_PARAMS["spreading_factor"]),
        "coding_rate"    : int(LORA_PARAMS["coding_rate"]),
        "preamble_length" : 8,
        "implicitHeader" : False,
        "sync_word"      : 0x12,
        "enable_CRC"     : bool(LORA_PARAMS["rx_crc"]),
    }

    radio = SX127x(parameters=params)
    radio.pin_ss = LORA_CS
    radio.pin_RxDone = None
    radio.transfer = _sx127x_legacy_transfer
    if hasattr(radio, "init"):
        radio.init()
    return radio

def _sx127x_packet_available():
    if not lora_driver:
        return False

    if hasattr(lora_driver, "received_packet"):
        return bool(lora_driver.received_packet())

    if hasattr(lora_driver, "receivedPacket"):
        return bool(lora_driver.receivedPacket())

    return False

def _sx127x_read_payload():
    if not lora_driver or not hasattr(lora_driver, "read_payload"):
        return None

    try:
        return lora_driver.read_payload(with_header=False)
    except TypeError:
        return lora_driver.read_payload()

# =============================================================================
#  DRIVER DO MODULO LORA SX1278
# =============================================================================

def lora_reset():
    # Pulso de reset por hardware conforme datasheet do SX1278 (minimo 100us)
    LORA_RESET.value(0)
    utime.sleep_ms(10)
    LORA_RESET.value(1)
    utime.sleep_ms(10)

def lora_init(frequency=433_000_000):
    global lora_driver, lora_backend

    if spi is None:
        return False

    if SX127X_DRIVER_AVAILABLE:
        try:
            params = dict(LORA_PARAMS)
            params["frequency"] = float(frequency)
            lora_driver = SX127x(
                spi,
                pins={
                    "cs": LORA_CS,
                    "reset": LORA_RESET,
                    "dio0": LORA_DIO0,
                },
                parameters=params,
            )
            lora_backend = "sx127x"
            return True
        except Exception as exc:
            if "unexpected keyword argument 'pins'" in str(exc):
                print("[INFO] API sx127x legada detectada na Ignicao - tentando compatibilidade.")
            else:
                print("[WARN] Falha no sx127x padrao da Ignicao ({}). Tentando compatibilidade.".format(exc))
            try:
                lora_driver = _init_legacy_sx127x(frequency)
                lora_backend = "sx127x"
                print("[BOOT] SX1278 inicializado em modo sx127x legacy compat.")
                return True
            except Exception as legacy_exc:
                print("[WARN] Falha na compatibilidade sx127x da Ignicao ({}). Fallback nativo.".format(legacy_exc))
                lora_driver = None
                lora_backend = "native"

    # Inicializa o SX1278 em modo LoRa
    lora_reset()

    # Verifica identidade do chip: SX1276/77/78/79 retornam 0x12
    version = _spi_read(REG_VERSION)
    print("[BOOT] SX1278 REG_VERSION=0x{:02X} (esperado 0x12)".format(version))
    if version != 0x12:
        return False  # SPI com defeito ou modulo nao conectado

    # Entra em Sleep com LoRa ativado
    _spi_write(REG_OP_MODE, MODE_LORA | MODE_SLEEP)
    utime.sleep_ms(10)

    # Calcula e grava os registradores de frequencia
    frf = int((frequency * (1 << 19)) / 32_000_000)
    _spi_write(REG_FRF_MSB, (frf >> 16) & 0xFF)
    _spi_write(REG_FRF_MID, (frf >> 8)  & 0xFF)
    _spi_write(REG_FRF_LSB,  frf        & 0xFF)

    # Potencia de saida via PA_BOOST: 17 dBm
    _spi_write(REG_PA_CONFIG, 0x8F)

    # LNA: ganho maximo automatico com boost para banda HF (433 MHz)
    _spi_write(REG_LNA, 0x23)

    # Modem Config 1: BW=125kHz, CodingRate=4/5, Header explicito
    _spi_write(REG_MODEM_CONFIG1, 0x72)

    # Modem Config 2: SF=7, CRC habilitado
    _spi_write(REG_MODEM_CONFIG2, 0x74)

    # Modem Config 3: AGC automatico habilitado
    _spi_write(REG_MODEM_CONFIG3, 0x04)

    # Preambulo de 8 simbolos (minimo recomendado)
    _spi_write(REG_PREAMBLE_MSB, 0x00)
    _spi_write(REG_PREAMBLE_LSB, 0x08)

    # Sync Word privado: 0x12
    _spi_write(REG_SYNC_WORD, 0x12)

    # Enderecos base do FIFO para TX e RX (sem sobreposicao)
    _spi_write(REG_FIFO_TX_BASE, 0x00)
    _spi_write(REG_FIFO_RX_BASE, 0x00)

    # Volta ao Standby antes de iniciar recepcao
    _spi_write(REG_OP_MODE, MODE_LORA | MODE_STDBY)
    utime.sleep_ms(10)

    lora_backend = "native"
    return True

def lora_receive_mode():
    if lora_backend == "sx127x":
        return
    _spi_write(REG_OP_MODE, MODE_LORA | MODE_RX_CONT)

def lora_packet_available():
    if lora_backend == "sx127x":
        try:
            return _sx127x_packet_available()
        except Exception:
            return False

    flags = _spi_read(REG_IRQ_FLAGS)
    return bool(flags & IRQ_RX_DONE)

def lora_read_packet():
    if lora_backend == "sx127x":
        try:
            payload = _sx127x_read_payload()
            if payload is None:
                return None
            return bytes(payload).decode("utf-8", "ignore").strip()
        except Exception:
            return None

    flags = _spi_read(REG_IRQ_FLAGS)
    _spi_write(REG_IRQ_FLAGS, 0xFF)

    if flags & 0x20:
        return None  # Descarta pacote com CRC invalido

    nb_bytes     = _spi_read(REG_RX_NB_BYTES)
    current_addr = _spi_read(REG_FIFO_RX_CURRENT)

    _spi_write(REG_FIFO_ADDR_PTR, current_addr)
    raw = _spi_read_buf(REG_FIFO, nb_bytes)

    try:
        return raw.decode("utf-8").strip()
    except Exception:
        return None

def lora_send(message):
    if lora_backend == "sx127x":
        if not lora_driver:
            return
        try:
            lora_driver.println(message)
        except Exception:
            pass
        return

    _spi_write(REG_OP_MODE, MODE_LORA | MODE_STDBY)
    utime.sleep_ms(5)

    _spi_write(REG_FIFO_ADDR_PTR, 0x00)
    encoded = message.encode("utf-8")
    for byte in encoded:
        _spi_write(REG_FIFO, byte)
    _spi_write(REG_PAYLOAD_LENGTH, len(encoded))

    _spi_write(REG_OP_MODE, MODE_LORA | MODE_TX)

    timeout = utime.ticks_add(utime.ticks_ms(), 300)
    while not (_spi_read(REG_IRQ_FLAGS) & IRQ_TX_DONE):
        if utime.ticks_diff(timeout, utime.ticks_ms()) <= 0:
            break
        utime.sleep_ms(1)

    _spi_write(REG_IRQ_FLAGS, 0xFF)
    lora_receive_mode()

# --- maquina de estados ---
ESTADO_AGUARDANDO = "AGUARDANDO"
ESTADO_CONTAGEM   = "CONTAGEM"
ESTADO_IGNICAO    = "IGNICAO"
ESTADO_COMPLETO   = "COMPLETO"

TEMPO_CONTAGEM_MS = 10000
TEMPO_IGNICAO_MS  = 2000
TIMEOUT_SINAL_MS  = 500
TIMEOUT_LINK_MS   = 3000
INTERVALO_PISCA_MS = 250
INTERVALO_BUZZER_MS = 500
INTERVALO_PING_BOOT_MS = 700
INTERVALO_PISCA_STATUS_MS = 500
TEMPO_POS_COMPLETO_MS = 3000

MSG_ARM   = "ARM_CONFIRMED"
MSG_ABORT = "ABORT"
MSG_ACK   = "ACK"
MSG_DONE  = "IGNITION_COMPLETE"
MSG_STATUS = "STATUS:"

def _status(estado):
    lora_send(MSG_STATUS + estado)

def executar():
    print("[BOOT] Estacao de ignicao")
    desligar_tudo()
    buzzer_bip(300)

    if not lora_init(433_000_000):
        print("[ERRO] SX1278 nao detectado.")
        while True:
            sinalizar_erro(5)
            utime.sleep_ms(1000)

    lora_receive_mode()
    print("[BOOT] LoRa OK")

    # handshake de boot
    t_inicio = utime.ticks_ms()
    t_ping = utime.ticks_add(t_inicio, -INTERVALO_PING_BOOT_MS)
    t_pisca = t_inicio
    led = False
    conexao = False

    while utime.ticks_diff(utime.ticks_ms(), t_inicio) < 5000:
        agora = utime.ticks_ms()
        if utime.ticks_diff(agora, t_pisca) >= INTERVALO_PISCA_STATUS_MS:
            t_pisca = agora
            led = not led
            _set_status(led)
        if utime.ticks_diff(agora, t_ping) >= INTERVALO_PING_BOOT_MS:
            t_ping = agora
            lora_send("PING")
        if lora_packet_available():
            msg = lora_read_packet()
            if msg == "PING":
                lora_send("PONG")
                conexao = True
                break
            if msg == "PONG":
                conexao = True
                break
        utime.sleep_ms(10)

    if conexao:
        _set_status(True)
        buzzer_bip(200)
        print("[OK] Link com o comando")
    else:
        sinalizar_erro(4)
        print("[AVISO] Sem link no boot")

    estado = ESTADO_AGUARDANDO
    t_inicio_contagem = 0
    t_ultimo_arm = 0
    t_ultimo_link = utime.ticks_ms() if conexao else None
    t_inicio_ignicao = 0
    t_ultimo_pisca = 0
    t_ultimo_buz = 0
    led_vermelho = False
    link_reportado = None

    try:
        wdt = WDT(timeout=8000)
    except Exception:
        wdt = None

    _status(ESTADO_AGUARDANDO)

    while True:
        agora = utime.ticks_ms()
        msg = None

        if lora_packet_available():
            msg = lora_read_packet()
            if msg:
                t_ultimo_link = agora
                print("[RX] {} | {}".format(msg, estado))

        if msg == "PING":
            lora_send("PONG")
            t_ultimo_link = agora
            msg = None

        link_ok = (
            t_ultimo_link is not None
            and utime.ticks_diff(agora, t_ultimo_link) <= TIMEOUT_LINK_MS
        )
        if link_ok != link_reportado:
            link_reportado = link_ok
            print("[LINK] {}".format("OK" if link_ok else "PERDIDO"))

        if link_ok:
            _set_status(True)
        elif utime.ticks_diff(agora, t_ultimo_pisca) >= INTERVALO_PISCA_STATUS_MS:
            t_ultimo_pisca = agora
            _toggle_status()

        if estado == ESTADO_AGUARDANDO:
            _set_status(True)
            PIN_LED_COUNT.value(0)
            PIN_BUZZER.value(0)

            if msg == MSG_ARM:
                lora_send(MSG_ACK)
                _status(ESTADO_CONTAGEM)
                print("[ARM] Contagem de 10 s")
                _set_gate1(True)
                t_inicio_contagem = agora
                t_ultimo_arm = agora
                t_ultimo_pisca = agora
                t_ultimo_buz = agora
                estado = ESTADO_CONTAGEM

        elif estado == ESTADO_CONTAGEM:
            _set_status(True)

            if msg == MSG_ARM:
                t_ultimo_arm = agora

            sinal_perdido = utime.ticks_diff(agora, t_ultimo_arm) > TIMEOUT_SINAL_MS
            abort = (msg == MSG_ABORT)

            if abort or sinal_perdido:
                print("[SEGURANCA] {}".format("ABORT" if abort else "sinal perdido"))
                desligar_tudo()
                _status(MSG_ABORT)
                sinalizar_erro(6)
                estado = ESTADO_AGUARDANDO
                continue

            if utime.ticks_diff(agora, t_ultimo_pisca) >= INTERVALO_PISCA_MS:
                led_vermelho = not led_vermelho
                PIN_LED_COUNT.value(1 if led_vermelho else 0)
                t_ultimo_pisca = agora

            if utime.ticks_diff(agora, t_ultimo_buz) >= INTERVALO_BUZZER_MS:
                PIN_BUZZER.value(0 if PIN_BUZZER.value() else 1)
                t_ultimo_buz = agora

            decorrido = utime.ticks_diff(agora, t_inicio_contagem)
            if decorrido >= TEMPO_CONTAGEM_MS:
                if lora_packet_available():
                    final = lora_read_packet()
                    if final == MSG_ABORT:
                        desligar_tudo()
                        _status(MSG_ABORT)
                        sinalizar_erro(6)
                        estado = ESTADO_AGUARDANDO
                        continue
                if utime.ticks_diff(agora, t_ultimo_arm) > TIMEOUT_SINAL_MS:
                    desligar_tudo()
                    _status(MSG_ABORT)
                    sinalizar_erro(6)
                    estado = ESTADO_AGUARDANDO
                    continue

                PIN_BUZZER.value(0)
                _set_status(True)
                PIN_LED_COUNT.value(1)
                _set_rele(True)
                _set_gate2(True)
                _status(ESTADO_IGNICAO)
                print("[IGNICAO] Rele e Q1 acionados")
                t_inicio_ignicao = agora
                estado = ESTADO_IGNICAO

        elif estado == ESTADO_IGNICAO:
            if msg == MSG_ABORT or utime.ticks_diff(agora, t_ultimo_arm) > TIMEOUT_SINAL_MS:
                print("[SEGURANCA] ABORT durante a ignicao")
                desligar_tudo()
                _status(MSG_ABORT)
                sinalizar_erro(4)
                estado = ESTADO_AGUARDANDO
                continue

            if utime.ticks_diff(agora, t_inicio_ignicao) >= TEMPO_IGNICAO_MS:
                _set_gate2(False)
                _set_rele(False)
                lora_send(MSG_DONE)
                _status(ESTADO_COMPLETO)
                print("[OK] Ignicao concluida")
                for _ in range(3):
                    buzzer_bip(120)
                    utime.sleep_ms(120)
                estado = ESTADO_COMPLETO
                t_fim = agora

        elif estado == ESTADO_COMPLETO:
            _set_rele(False)
            if utime.ticks_diff(agora, t_fim) >= TEMPO_POS_COMPLETO_MS:
                desligar_tudo()
                _status(ESTADO_AGUARDANDO)
                estado = ESTADO_AGUARDANDO

        if wdt:
            wdt.feed()
        utime.sleep_ms(5)

if __name__ == "__main__":
    executar()
