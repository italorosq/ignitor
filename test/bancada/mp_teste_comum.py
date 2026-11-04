# ==============================================================================
#   INFRAESTRUTURA COMUM DOS TESTES DE BANCADA (MicroPython)
#   Compartilhado por:
#     - mp_teste_transistor.py : cadeia de seguranca Q1/Q2 no ESP32
#     - mp_teste_rele.py       : modulo rele SRD-05VDC no ESP32
#
#   Este arquivo vai para a placa junto com o script escolhido (mesma pasta).
#   ESP8266 exige modulo pre-compilado (mpy-cross -march=xtensa); no ESP32 o
#   .py roda direto.
# ==============================================================================

import utime
from machine import I2C, Pin

# =============================================================================
#  PINAGEM PADRAO DO ESP8266 (NodeMCU v3 / Wemos D1 mini)
# =============================================================================

PIN_SDA_NUM = 4      # D2
PIN_SCL_NUM = 5      # D1
PIN_BUZZER_NUM = 14  # D5
PIN_BUTTON_NUM = 12  # D6
PIN_LED_BTN_NUM = 13  # D7

OLED_ADDR = 0x3C
OLED_W = 128
OLED_H = 64
I2C_FREQ_ALTO = 400_000
I2C_FREQ_BAIXO = 100_000

# =============================================================================
#  MAPA OFICIAL DA ESTACAO DE IGNICAO (ESP32 DevKit V1)
#  Espelha as constantes de firmware/micropython/estacao_ignicao_esp.py.
#  test/test_firmware.py confere que os dois continuam iguais.
# =============================================================================

PIN_ESP32_RELE_NUM = 32     # entrada IN do modulo rele (ativo em baixo)
PIN_ESP32_GATE_1_NUM = 13   # Q2: liga o GND do modulo rele (ativo em ALTO)
PIN_ESP32_GATE_2_NUM = 33   # Q1: chave de saida do ignitor (ativo em ALTO)
PIN_ESP32_BUZZER_NUM = 14
PIN_ESP32_BUTTON_NUM = 27   # BUTTON_IN, active-low (pull-up interno)
PIN_ESP32_LED_COUNT_NUM = 12
PIN_ESP32_SDA_NUM = 21
PIN_ESP32_SCL_NUM = 22

# Modulo SRD-05VDC-SL-C: IN em BAIXO liga o rele, IN em ALTO desliga.
RELE_ACTIVE_LEVEL = 0
RELE_INACTIVE_LEVEL = 0 if RELE_ACTIVE_LEVEL else 1

# =============================================================================
#  TEMPOS COMPARTILHADOS (mesmos valores do firmware da estacao)
# =============================================================================

INTERVALO_OLED_MS = 200
INTERVALO_STATUS_MS = 2000
INTERVALO_PISCA_MS = 250
INTERVALO_PISCA_LED_MS = 1000
DURACAO_PISCA_LED_MS = 100
TEMPO_CONTAGEM_MS = 5000
TEMPO_SAIDA_MS = 2000
TEMPO_ABORTADO_MS = 1500
TEMPO_POS_MARIO_MS = 3000
TEMPO_LONGO_MS = 1000
DEBOUNCE_BTN_MS = 50
PAUSA_LOOP_MS = 10

ESTADO_IDLE = "IDLE"
ESTADO_CONTAGEM = "CONTAGEM"
ESTADO_ABORTADO = "ABORTADO"
ESTADO_SAIDA = "SAIDA"
ESTADO_SUCESSO = "SUCESSO"

# =============================================================================
#  SEQUENCIA DO MARIO (ritmo em unidades de 90 ms; buzzer ativo so tem
#  liga/desliga, entao o que se ouve e o ritmo do tema)
# =============================================================================

UNIDADE_MARIO_MS = 90
UNIDADES_MARIO = (
    (1, 1), (1, 1), (1, 2),            # E  E  _  E
    (1, 2), (1, 1), (1, 2),            # _  C  E  _
    (2, 2), (2, 4),                    # G  _  G4 _  _  _
    (2, 3), (2, 2), (2, 3),            # C  _  _  G4 _  E  _  _
    (2, 1), (2, 1), (2, 1), (2, 0),    # A  B  A# A
)
SEQUENCIA_MARIO = tuple(
    (ligado * UNIDADE_MARIO_MS, desligado * UNIDADE_MARIO_MS)
    for ligado, desligado in UNIDADES_MARIO
)

# =============================================================================
#  LOGO (SUCESSO) - modulo separado mp_logo_serra.py (bitmap 1-bit no formato
#  do framebuffer do display). Se o modulo faltar na placa, a tela de sucesso
#  cai para o texto simples.
# =============================================================================

try:
    from mp_logo_serra import LOGO_BYTES, LOGO_ALTURA, LOGO_LARGURA, LOGO_X
    LOGO_OK = True
except Exception as exc:
    LOGO_OK = False
    print("[BOOT] mp_logo_serra.py ausente ({}) - sucesso sem logo.".format(exc))


# =============================================================================
#  BUZZER (toca sequencias de (ligado_ms, desligado_ms) sem bloquear)
# =============================================================================

def fases(sequencia):
    lista = []
    for ligado_ms, desligado_ms in sequencia:
        lista.append((1, ligado_ms))
        if desligado_ms > 0:
            lista.append((0, desligado_ms))
    return lista


class Buzzer:
    def __init__(self, pin):
        self.pin = pin
        self._fases = []
        self._indice = 0
        self._prazo = 0

    def tocar(self, sequencia, agora=None):
        if agora is None:
            agora = utime.ticks_ms()
        self._fases = fases(sequencia)
        self._indice = 0
        self.pin.value(self._fases[0][0])
        self._prazo = utime.ticks_add(agora, self._fases[0][1])

    def bip(self, ms=80, agora=None):
        self.tocar(((ms, 0),), agora)

    def atualizar(self, agora):
        if not self._fases:
            return
        if utime.ticks_diff(agora, self._prazo) < 0:
            return
        self._indice += 1
        if self._indice >= len(self._fases):
            self._fases = []
            self.pin.value(0)
            return
        ligado, duracao = self._fases[self._indice]
        self.pin.value(ligado)
        self._prazo = utime.ticks_add(agora, duracao)

    @property
    def tocando(self):
        return bool(self._fases)


def beep_bloqueante(pin, ms):
    pin.value(1)
    utime.sleep_ms(ms)
    pin.value(0)


# =============================================================================
#  BOTAO (active-low, debounce; eventos de aperto, clique e toque longo)
# =============================================================================

class Botao:
    EVENTO_APERTO = "APERTO"
    EVENTO_CURTO = "CURTO"
    EVENTO_LONGO = "LONGO"

    def __init__(self, pin, debounce_ms=DEBOUNCE_BTN_MS, tempo_longo_ms=TEMPO_LONGO_MS):
        self.pin = pin
        self.debounce_ms = debounce_ms
        self.tempo_longo_ms = tempo_longo_ms
        self.estavel = 1
        self.t_mudanca = 0
        self.t_aperto = 0
        self.aperto_emitido = False
        self.longo_emitido = False

    def atualizar(self, agora):
        eventos = []
        v = self.pin.value()
        if v != self.estavel:
            self.estavel = v
            self.t_mudanca = agora
            if v == 0:
                self.t_aperto = agora
                self.aperto_emitido = False
                self.longo_emitido = False

        if self.estavel == 0:
            pressionado_ms = utime.ticks_diff(agora, self.t_aperto)
            if not self.aperto_emitido and pressionado_ms >= self.debounce_ms:
                self.aperto_emitido = True
                eventos.append(self.EVENTO_APERTO)
            if not self.longo_emitido and pressionado_ms >= self.tempo_longo_ms:
                self.longo_emitido = True
                eventos.append(self.EVENTO_LONGO)
        elif self.t_aperto and utime.ticks_diff(agora, self.t_mudanca) >= self.debounce_ms:
            if not self.longo_emitido:
                eventos.append(self.EVENTO_CURTO)
            self.t_aperto = 0
        return eventos

    def tempo_apertado_ms(self, agora):
        if self.estavel == 0 and self.t_aperto:
            return utime.ticks_diff(agora, self.t_aperto)
        return 0


def pisca_acesa(agora):
    return (agora // INTERVALO_PISCA_MS) % 2 == 0


# =============================================================================
#  TELA (SSD1306 opcional: qualquer falha desabilita so o display)
# =============================================================================

class TelaOLED:
    def __init__(self, oled):
        self.oled = oled
        self.ok = oled is not None

    def desabilitar(self, exc):
        self.ok = False
        print("[OLED] Falha no display ({}) - desabilitado.".format(exc))


def _enderecos(lista):
    return ["0x{:02X}".format(a) for a in lista]


def init_i2c(scl_num=PIN_SCL_NUM, sda_num=PIN_SDA_NUM):
    ultimo = None
    for freq in (I2C_FREQ_ALTO, I2C_FREQ_BAIXO):
        try:
            try:
                i2c = I2C(0, scl=Pin(scl_num), sda=Pin(sda_num), freq=freq)
            except TypeError:
                i2c = I2C(scl=Pin(scl_num), sda=Pin(sda_num), freq=freq)
            encontrados = i2c.scan()
            ultimo = i2c
            print("[BOOT] I2C a {} Hz, encontrados: {}".format(freq, _enderecos(encontrados)))
            if encontrados:
                return i2c, encontrados
        except Exception as exc:
            print("[BOOT] I2C indisponivel a {} Hz ({}).".format(freq, exc))
    return ultimo, []


def criar_oled(scl_num=PIN_SCL_NUM, sda_num=PIN_SDA_NUM):
    """Inicializa I2C + OLED; devolve (tela, enderecos_encontrados).

    Sem ssd1306.py, sem OLED no barramento ou com falha de init, a tela volta
    com ok=False e o teste segue pelo serial.
    """
    i2c, encontrados = init_i2c(scl_num, sda_num)
    if i2c is None or OLED_ADDR not in encontrados:
        print("[BOOT] OLED ausente no I2C - seguindo sem tela.")
        return TelaOLED(None), encontrados
    try:
        from ssd1306 import SSD1306_I2C
    except Exception as exc:
        print("[BOOT] ssd1306.py nao encontrado na placa ({})".format(exc))
        return TelaOLED(None), encontrados
    try:
        oled = SSD1306_I2C(OLED_W, OLED_H, i2c, OLED_ADDR)
        print("[BOOT] OLED SSD1306 encontrado em 0x{:02X}.".format(OLED_ADDR))
        return TelaOLED(oled), encontrados
    except Exception as exc:
        print("[BOOT] OLED nao inicializou ({}) - seguindo sem tela.".format(exc))
        return TelaOLED(None), encontrados


def _desenhar_idle(tela, estado):
    oled = tela.oled
    oled.fill(0)
    oled.rect(0, 0, OLED_W, OLED_H, 1)
    oled.text("IGNITOR - TESTE", 8, 6)
    oled.text("Aperte o botao", 8, 20)
    oled.text("para iniciar a", 8, 32)
    oled.text("seq. de IGNICAO", 8, 44)
    oled.text("seqs: {}".format(estado["sequencias"]), 8, 54)


def _desenhar_contagem(tela, estado, agora):
    oled = tela.oled
    oled.fill(0)
    if pisca_acesa(agora):
        oled.rect(0, 0, OLED_W, OLED_H, 1)
    oled.text("IGNICAO EM", 8, 6)
    oled.rect(6, 18, 28, 20, 1)
    oled.text("{}".format(estado["segundos"]), 14, 24)
    oled.text("ARM_CONFIRMED", 8, 44)
    oled.text("aperte=ABORTA", 8, 54)


def _desenhar_saida(tela, estado, agora):
    oled = tela.oled
    oled.fill(0)
    if pisca_acesa(agora):
        oled.rect(0, 0, OLED_W, OLED_H, 1)
    oled.text("=== FOGO! ===", 8, 6)
    oled.text("Saida ativa", 8, 22)
    oled.text("{}s".format(estado["segundos"]), 8, 36)
    oled.text("SAIDA SIMULADA", 8, 52)


def _desenhar_abortado(tela, estado):
    oled = tela.oled
    oled.fill(0)
    oled.rect(0, 0, OLED_W, OLED_H, 1)
    oled.text("ABORTADO!", 8, 6)
    oled.text("Ignicao", 8, 24)
    oled.text("cancelada.", 8, 36)
    oled.text("seguro :)", 8, 52)


def _desenhar_sucesso(tela, estado):
    oled = tela.oled
    oled.fill(0)
    if not LOGO_OK:
        oled.rect(0, 0, OLED_W, OLED_H, 1)
        oled.text("SUCESSO!", 8, 22)
        oled.text("seq. concluida", 8, 34)
        return
    for pagina in range(LOGO_ALTURA // 8):
        ini_logo = pagina * LOGO_LARGURA
        ini_tela = pagina * OLED_W + LOGO_X
        oled.buffer[ini_tela:ini_tela + LOGO_LARGURA] = LOGO_BYTES[ini_logo:ini_logo + LOGO_LARGURA]
    oled.text("SUCESSO!", 32, 56)


def mostrar(tela, estado, agora):
    """Desenha o estado atual; falha no display desabilita so a tela."""
    if not tela.ok:
        return
    try:
        atual = estado["estado"]
        if atual == ESTADO_CONTAGEM:
            _desenhar_contagem(tela, estado, agora)
        elif atual == ESTADO_SAIDA:
            _desenhar_saida(tela, estado, agora)
        elif atual == ESTADO_ABORTADO:
            _desenhar_abortado(tela, estado)
        elif atual == ESTADO_SUCESSO:
            _desenhar_sucesso(tela, estado)
        else:
            _desenhar_idle(tela, estado)
        tela.oled.show()
    except Exception as exc:
        tela.desabilitar(exc)


# =============================================================================
#  MAQUINA DE ESTADOS DA SEQUENCIA DE IGNICAO (teste)
#  CONTAGEM -> SAIDA -> SUCESSO, com ABORTADO no caminho. Nao bloqueante:
#  o loop principal segue lendo o botao enquanto a contagem roda.
# =============================================================================

def iniciar_sequencia(estado, buzzer, agora):
    estado["estado"] = ESTADO_CONTAGEM
    estado["sequencias"] += 1
    estado["t_contagem"] = agora
    estado["segundos"] = TEMPO_CONTAGEM_MS // 1000
    buzzer.bip(100, agora)
    print("[BTN] Iniciando sequencia de ignicao (teste) #{}...".format(estado["sequencias"]))
    print("[CMD] ARM_CONFIRMED (simulado) - contagem de {} s.".format(TEMPO_CONTAGEM_MS // 1000))


def abortar_sequencia(estado, buzzer, agora):
    estado["estado"] = ESTADO_ABORTADO
    estado["t_abortado"] = agora
    buzzer.tocar(((600, 0),), agora)
    print("[SEGURANCA] ABORTADO pelo botao! Contagem cancelada.")


def passo_sequencia(estado, buzzer, agora):
    atual = estado["estado"]

    # ------------------------------------------------------------------
    #  CONTAGEM REGRESSIVA (5 s, um bip por segundo)
    # ------------------------------------------------------------------
    if atual == ESTADO_CONTAGEM:
        decorrido = utime.ticks_diff(agora, estado["t_contagem"])
        restante = TEMPO_CONTAGEM_MS - decorrido
        segundos = max(1, (restante + 999) // 1000)
        if segundos != estado["segundos"]:
            estado["segundos"] = segundos
            buzzer.bip(100, agora)
            print("[CONTAGEM] {}s restantes...".format(segundos))
        if decorrido >= TEMPO_CONTAGEM_MS:
            estado["estado"] = ESTADO_SAIDA
            estado["t_saida"] = agora
            estado["segundos"] = TEMPO_SAIDA_MS // 1000
            buzzer.tocar(((400, 0),), agora)
            print("[IGNICAO] FOGO! Saida simulada ativa por {} s.".format(TEMPO_SAIDA_MS // 1000))

    # ------------------------------------------------------------------
    #  SAIDA ATIVA (2 s, igual ao rele do projeto)
    # ------------------------------------------------------------------
    elif atual == ESTADO_SAIDA:
        decorrido = utime.ticks_diff(agora, estado["t_saida"])
        restante = TEMPO_SAIDA_MS - decorrido
        estado["segundos"] = max(1, (restante + 999) // 1000)
        if decorrido >= TEMPO_SAIDA_MS:
            estado["estado"] = ESTADO_SUCESSO
            estado["t_sucesso"] = agora
            buzzer.tocar(SEQUENCIA_MARIO, agora)
            print("[TX] IGNITION_COMPLETE (simulado) - sequencia concluida!")
            print("[OK] ==============================================")
            print("[OK]  IGNICAO CONCLUIDA COM SUCESSO (teste) \\o/")
            print("[OK]  Mario no buzzer + logo na tela...")
            print("[OK] ==============================================")

    # ------------------------------------------------------------------
    #  ABORTADO (aviso curto e volta para o repouso)
    # ------------------------------------------------------------------
    elif atual == ESTADO_ABORTADO:
        if utime.ticks_diff(agora, estado["t_abortado"]) >= TEMPO_ABORTADO_MS:
            estado["estado"] = ESTADO_IDLE
            print("[OK] Aborto concluido. Pronto para nova sequencia.")

    # ------------------------------------------------------------------
    #  SUCESSO (Mario tocando; volta ao repouso quando termina)
    # ------------------------------------------------------------------
    elif atual == ESTADO_SUCESSO:
        if not buzzer.tocando and utime.ticks_diff(agora, estado["t_sucesso"]) >= TEMPO_POS_MARIO_MS:
            estado["estado"] = ESTADO_IDLE
            print("[OK] Mario tocado! Pronto para nova sequencia.")
