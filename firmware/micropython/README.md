# Firmware MicroPython

## Estações atuais

- `estacao_comando_esp.py` — ESP32, botão, OLED, LEDs, buzzer e LoRa.
- `estacao_ignicao_esp.py` — ESP32, relé, Q1/Q2, LEDs, buzzer e LoRa.

## Apoio do comando

- `ssd1306.py` — driver do OLED.
- `logo_serra.py` — bitmap da logo.

## Legado

- `legacy/estacao_comando.py` — Pico.
- `legacy/estacao_ignicao.py` — Pico.
- `legacy/config_lora.py`, `legacy/sx127x.py` — apoio do Pico.

Os arquivos de `legacy/` não são usados nas placas atuais.
