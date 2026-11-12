"""Quadro de comunicacao LoRa compartilhado pelas duas estacoes.

Formato:

    IG1|<epoch>|<seq>|<ciclo>|<BODY>

- IG1: identificador do sistema.
- epoch: 8 digitos hex, sorteado a cada boot.
- seq: incrementa a cada quadro transmitido.
- ciclo: numero do ciclo de armamento; 0 nos quadros de servico.
- BODY: PING, PONG, ARM_CONFIRMED, ABORT, ACK, IGNITION_COMPLETE
  ou STATUS:<estado>.

Isto nao e autenticacao criptografica. Serve para separar estacoes,
descartar quadros de outro sistema e rejeitar replay simples.
"""

try:
    import utime
except ImportError:  # permite importar o modulo no PC para conferencia
    import time as utime

try:
    import ubinascii as _binascii
except ImportError:
    import binascii as _binascii

try:
    import os as _os
except ImportError:
    _os = None

SYS_ID = "IG1"
MAX_QUADRO = 64

MSG_ARM = "ARM_CONFIRMED"
MSG_ABORT = "ABORT"
MSG_ACK = "ACK"
MSG_DONE = "IGNITION_COMPLETE"
MSG_PING = "PING"
MSG_PONG = "PONG"
MSG_STATUS = "STATUS:"

ESTADOS = (
    "AGUARDANDO",
    "CONTAGEM",
    "IGNICAO",
    "COMPLETO",
    "ABORT",
    "BLOQUEADO",
)

_MENSAGENS = (MSG_ARM, MSG_ABORT, MSG_ACK, MSG_DONE, MSG_PING, MSG_PONG)


def _ticks_ms():
    ticks = getattr(utime, "ticks_ms", None)
    if ticks is not None:
        return ticks()
    return int(utime.time() * 1000)


def _novo_epoch():
    if _os is not None:
        try:
            return _binascii.hexlify(_os.urandom(4)).decode()
        except Exception:
            pass
    return "{:08X}".format(_ticks_ms() & 0xFFFFFFFF)


def _epoch_valido(texto):
    if len(texto) != 8:
        return False
    for ch in texto:
        if ch not in "0123456789abcdefABCDEF":
            return False
    return True


def _corpo_valido(body):
    if body in _MENSAGENS:
        return True
    if body.startswith(MSG_STATUS):
        return body[len(MSG_STATUS):] in ESTADOS
    return False


class Codec:
    """Codifica e decodifica os quadros de uma estacao."""

    def __init__(self, epoch=None):
        self.epoch = epoch or _novo_epoch()
        self.seq = 0
        self.peer_epoch = None
        self.peer_seq = -1

    def encode(self, body, ciclo=0):
        self.seq = (self.seq + 1) & 0x7FFFFFFF
        if self.seq == 0:
            self.seq = 1
        return "{}|{}|{}|{}|{}".format(
            SYS_ID, self.epoch, self.seq, int(ciclo), body
        )

    def decode(self, quadro):
        """Retorna (body, ciclo) ou None se o quadro for invalido/repetido."""
        if not isinstance(quadro, str):
            return None
        if len(quadro) > MAX_QUADRO:
            return None

        partes = quadro.split("|")
        if len(partes) != 5:
            return None
        if partes[0] != SYS_ID:
            return None

        epoch = partes[1]
        if not _epoch_valido(epoch):
            return None

        try:
            seq = int(partes[2])
            ciclo = int(partes[3])
        except (TypeError, ValueError):
            return None
        if seq <= 0 or ciclo < 0:
            return None

        body = partes[4]
        if not _corpo_valido(body):
            return None

        if epoch == self.peer_epoch:
            if seq <= self.peer_seq:
                return None
        else:
            # A outra estacao reiniciou: aceita o epoch novo e recomeca a
            # sequencia. Sem assinatura, isto nao prova identidade.
            self.peer_epoch = epoch
            self.peer_seq = 0

        self.peer_seq = seq
        return body, ciclo
