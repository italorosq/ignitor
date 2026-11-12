# Instalação

Resumo: montar a placa, gravar o firmware da estação, testar com carga dummy.

## 1. Material

- 2 × ESP32 DevKit V1, 30 pinos.
- 2 × SX1278 433 MHz + antena.
- 1 × botão momentâneo.
- 1 × OLED SSD1306 128×64 (só no comando).
- 2 × buzzers ativos.
- 1 × módulo relé 5 V com flyback.
- 1 × borne de ignição.
- 2 × bateria + TP4056 + boost 5 V.
- LEDs, resistores e fios.

## 2. Montagem

### Comando

Montar J1, J2/J3 (botão), J4/J5 (LED do botão), J10 (buzzer), J11 (OLED), U1
(LoRa), A1 e os LEDs D3/D4. Não montar Q1, Q2, J7/J8 nem J12.

### Ignição

Montar J1, J7/J8 (relé), J10 (buzzer), J12 (SMD) ou J9 (PTH), U1, A1, Q1, Q2,
Q4 e os LEDs D3/D4. Não montar J2/J3, J4/J5 nem J11.

O J8 é o ARM/RBF: feche os pinos 1–3 para alimentar a bobina do relé.

## 3. Firmware

| Estação | Arquivo | Salvar como |
| --- | --- | --- |
| Comando | `firmware/micropython/estacao_comando_esp.py` | `main.py` |
| Ignição | `firmware/micropython/estacao_ignicao_esp.py` | `main.py` |

As duas estações também precisam de `protocolo_lora.py`. O comando precisa ainda
de `ssd1306.py` e `logo_serra.py`; a ignição não usa esses dois.

Com `mpremote`:

```bash
mpremote connect COM5 fs cp firmware/micropython/protocolo_lora.py :protocolo_lora.py
mpremote connect COM5 fs cp firmware/micropython/estacao_comando_esp.py :main.py
mpremote connect COM5 fs cp firmware/micropython/ssd1306.py :ssd1306.py
mpremote connect COM5 fs cp firmware/micropython/logo_serra.py :logo_serra.py
```

Na ignição, troque `estacao_comando_esp.py` por `estacao_ignicao_esp.py` e não
copie `ssd1306.py` nem `logo_serra.py`.

## 4. Teste

1. Antenas conectadas.
2. Carga dummy no lugar do ignitor.
3. J8 aberto.
4. Ligar as duas estações.
5. Conferir `PING/PONG` e o link no OLED.
6. Fechar o J8.
7. Segurar o botão até o OLED mostrar `CONFIRMADO` (cerca de 13 s).
8. Conferir a contagem, o acionamento por 2 s e o `IGNITION_COMPLETE`.
9. Repetir soltando o botão antes dos 10 s e conferir o abort.
10. Repetir soltando o botão durante a queima e conferir o corte imediato.

## 5. Antes do ignitor real

- Conferir continuidade do ignitor.
- Afastar o operador pelo menos 10 m.
- Usar fonte limitada ou fusível no laço.
- Não energizar sem antena.
