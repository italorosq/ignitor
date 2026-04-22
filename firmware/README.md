# Firmware - Serra Rocketry Ignitor

> Firmware oficial em MicroPython.

## Arquivos

| Placa | Arquivo | Salvar como |
| --- | --- | --- |
| Comando (Pico) | [micropython/estacao_comando.py](./micropython/estacao_comando.py) | `main.py` |
| Ignição (Pico) | [micropython/estacao_ignicao.py](./micropython/estacao_ignicao.py) | `main.py` |
| Ignição (ESP32-C3) | [micropython/estacao_ignicao_esp.py](./micropython/estacao_ignicao_esp.py) | `main.py` |

Pinagem: [hardware/README.md#pinagem](../hardware/README.md#pinagem)

## Gravar

Consulte [docs/INSTALL.md#4-gravar-firmware](../docs/INSTALL.md#4-gravar-firmware).

## Legado

- `code.ino` - Template Arduino para ESP32/ESP8266 (não faz parte do fluxo oficial MicroPython)
- `config.example.h` - Configuração de exemplo para o template Arduino

## Debug Serial

```bash
screen /dev/ttyACM0 115200
```

Logs esperados:

```text
[LoRa] SX1278 inicializado em 433 MHz.
[CMD] Link com ignicao: OK
[CMD] ACK recebido da base de ignicao.
[CMD] IGNITION_COMPLETE recebido.
```

> **⚠️ Segurança**: Sempre testar com carga dummy (LED/lâmpada) no pino do relé antes de usar ignitor real.
