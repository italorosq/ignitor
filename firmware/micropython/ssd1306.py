# ==============================================================================
#   Driver minimalista SSD1306 (OLED 128x64) via I2C para MicroPython
#   Uso: display de status da estacao de ignicao (sem dependencias externas).
#   Se o OLED nao estiver presente no barramento, o chamador deve detectar via
#   scan e simplesmente nao usar o objeto (nunca travar o boot por causa disso).
# ==============================================================================

import framebuf


class SSD1306_I2C(framebuf.FrameBuffer):
    def __init__(self, width, height, i2c, addr=0x3C):
        self.i2c = i2c
        self.addr = addr
        self.buffer = bytearray((height // 8) * width)
        super().__init__(self.buffer, width, height, framebuf.MONO_VMSB)
        self._init_display()
        self.fill(0)
        self.show()

    def _init_display(self):
        for cmd in (
            0xAE,  # display off
            0xD5, 0x80,  # clock divide
            0xA8, 0x3F,  # multiplex 64
            0xD3, 0x00,  # display offset
            0x40,  # start line
            0x8D, 0x14,  # charge pump on
            0x20, 0x00,  # memory mode horizontal
            0xA1,  # segment remap
            0xC8,  # COM scan invertido
            0xDA, 0x12,  # COM pins
            0x81, 0xCF,  # contraste
            0xD9, 0xF1,  # pre-charge
            0xDB, 0x40,  # VCOM detect
            0xA4,  # resume RAM
            0xA6,  # display normal
            0xAF,  # display on
        ):
            self._write_cmd(cmd)

    def _write_cmd(self, cmd):
        self.i2c.writeto(self.addr, bytes((0x80, cmd)))

    def show(self):
        width = self.width
        for page in range(self.height // 8):
            self._write_cmd(0xB0 + page)
            self._write_cmd(0x00)
            self._write_cmd(0x10)
            ini = page * width
            self.i2c.writeto(self.addr, b"\x40" + self.buffer[ini:ini + width])
