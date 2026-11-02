# Firmware - Serra Rocketry Ignitor

Firmware MicroPython das duas estações e arquivos de apoio.

## Estrutura

```text
firmware/
└── micropython/
    ├── estacao_comando.py       # Raspberry Pi Pico (comando)
    ├── estacao_ignicao_esp.py   # ESP32 DevKit V1 30 pinos (ignição principal)
    ├── estacao_ignicao.py       # Raspberry Pi Pico (ignição legada)
    ├── config_lora.py           # configuração de rádio
    ├── logo_serra.py            # bitmap da logo para o OLED
    ├── ssd1306.py               # driver OLED (vendorizado)
    └── sx127x.py                # driver LoRa legado (vendorizado)
```

A interface web legada que ficava em `firmware/data/` foi movida para
[`../software/web/`](../software/web/).

## Firmware oficial

| Estação | Arquivo | Placa alvo | Salvar como |
| --- | --- | --- | --- |
| Comando | [micropython/estacao_comando.py](./micropython/estacao_comando.py) | Raspberry Pi Pico | `main.py` |
| Ignição (principal) | [micropython/estacao_ignicao_esp.py](./micropython/estacao_ignicao_esp.py) | ESP32 DevKit V1 (ESP32-WROOM-32, 30 pinos) | `main.py` |
| Ignição (legado) | [micropython/estacao_ignicao.py](./micropython/estacao_ignicao.py) | Raspberry Pi Pico | `main.py` |

Arquivos de apoio:

- [micropython/config_lora.py](./micropython/config_lora.py)
- [micropython/logo_serra.py](./micropython/logo_serra.py)
- [micropython/ssd1306.py](./micropython/ssd1306.py)
- [micropython/sx127x.py](./micropython/sx127x.py)

Pinagem e BOM: [../hardware/README.md](../hardware/README.md).
Mapa de GPIOs do ESP32 e estado das placas: [../docs/ESTADO_DO_PROJETO.md](../docs/ESTADO_DO_PROJETO.md).

## Gravação nas placas

- Guia rápido: [../docs/README_ENVIO.md](../docs/README_ENVIO.md)
- Instalação completa: [../docs/INSTALL.md](../docs/INSTALL.md#4-gravar-firmware)

## Debug serial

```bash
screen /dev/ttyACM0 115200
```

Exemplo de logs esperados:

```text
[LoRa] SX1278 inicializado em 433 MHz.
[CMD] Link com ignicao: OK
[CMD] ACK recebido da base de ignicao.
[CMD] IGNITION_COMPLETE recebido.
```

## Segurança

- Sempre conectar antena LoRa antes de energizar.
- Testar primeiro com carga dummy (LED/lâmpada).
- Manter distância segura durante qualquer teste operacional.
- Não alterar a lógica de intertravamento sem revisar `hardware/README.md`,
  `docs/ARQUITETURA.md` e os testes de bancada.
