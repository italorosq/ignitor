# Firmware

Dois firmwares, um por estação. A placa é a mesma; mudam os periféricos
montados e o código.

| Estação | Arquivo | Placa |
| --- | --- | --- |
| Comando | `micropython/estacao_comando_esp.py` | ESP32 DevKit V1 + OLED |
| Ignição | `micropython/estacao_ignicao_esp.py` | ESP32 DevKit V1 |

O comando usa `ssd1306.py` e `logo_serra.py`. A ignição não usa OLED.

As versões para Raspberry Pi Pico ficam em `micropython/legacy/` e não são
usadas nas placas atuais.

## Gravação

- `estacao_comando_esp.py` → `main.py` no comando.
- `estacao_ignicao_esp.py` → `main.py` na ignição.
- `ssd1306.py` e `logo_serra.py` → raiz do comando.

Guia completo: [../docs/INSTALL.md](../docs/INSTALL.md).

## Segurança

- Carga dummy antes de ignitor real.
- Antena LoRa conectada antes de energizar.
- J8 aberto fora do teste.
- Não alterar a ordem relé → Q1 → Q1 → relé sem revisar os testes.
