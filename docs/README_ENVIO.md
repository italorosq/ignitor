# Envio de firmware

## Comando (ESP32)

Arquivos:

- `firmware/micropython/estacao_comando_esp.py` → `main.py`
- `firmware/micropython/ssd1306.py`
- `firmware/micropython/logo_serra.py`

```bash
mpremote connect COM5 fs cp firmware/micropython/estacao_comando_esp.py :main.py
mpremote connect COM5 fs cp firmware/micropython/ssd1306.py :ssd1306.py
mpremote connect COM5 fs cp firmware/micropython/logo_serra.py :logo_serra.py
```

## Ignição (ESP32)

Arquivo:

- `firmware/micropython/estacao_ignicao_esp.py` → `main.py`

```bash
mpremote connect COM5 fs cp firmware/micropython/estacao_ignicao_esp.py :main.py
```

A ignição não usa OLED, então não precisa de `ssd1306.py` nem `logo_serra.py`.

## Pico (legado)

Os arquivos estão em `firmware/micropython/legacy/`. Não são usados nas placas
atuais.

## Depois de gravar

1. Abrir o monitor serial.
2. Conferir a mensagem de boot e o link LoRa.
3. Testar com carga dummy.
