# Firmware - Serra Rocketry Ignitor

## Visão Geral

Implementação oficial em MicroPython para Raspberry Pi Pico:

- [../software/estacao_comando.py](../software/estacao_comando.py)
- [../software/estacao_ignicao.py](../software/estacao_ignicao.py)

Frequência de operação: 433 MHz (RA-02 / SX1278).

## Fluxo Atual

### Estação de Comando

1. Em idle, valida link com PING/PONG.
2. Só permite armamento com link ativo.
3. Ao segurar botão por 5 s, entra em transmissão de ARM_CONFIRMED.
4. Mantém ARM_CONFIRMED em retransmissão até receber IGNITION_COMPLETE.
5. Se botão for solto antes do final, envia ABORT.
6. Ao receber IGNITION_COMPLETE, aguarda 3 s e emite 2 bipes.

### Estação de Ignição

1. Inicializa LoRa e entra em recepção contínua.
2. Responde PONG quando recebe PING.
3. Ao receber ARM_CONFIRMED, responde ACK e inicia contagem de 5 s.
4. Se perder ARM por mais de 500 ms, aborta por segurança.
5. Ao fim da contagem, aciona relé (GP26) e buzzer por 2 s.
6. Envia IGNITION_COMPLETE ao comando.

## Pinagem de Referência

### Comando

- LoRa: GP0 (MISO), GP1 (CS), GP2 (SCK), GP3 (MOSI), GP4 (RESET), GP15 (DIO0)
- LED amarelo: GP11
- LED vermelho: GP12
- Buzzer: GP19
- Botão ignição: GP13 (pull-up interno)

### Ignição

- LoRa: GP0 (MISO), GP1 (CS), GP2 (SCK), GP3 (MOSI), GP4 (RESET)
- LED amarelo: GP11
- LED vermelho: GP12
- Buzzer: GP19
- Relé/ignitor: GP26

## Deploy

### Thonny

1. Instale MicroPython no Pico.
2. Abra [../software/estacao_comando.py](../software/estacao_comando.py) e salve no Pico como main.py.
3. Repita com [../software/estacao_ignicao.py](../software/estacao_ignicao.py) no outro Pico.

### Linha de Comando (ampy)

```bash
ampy --port /dev/ttyACM0 put software/estacao_comando.py main.py
ampy --port /dev/ttyACM1 put software/estacao_ignicao.py main.py
```

## Debug Serial

```bash
screen /dev/ttyACM0 115200
```

Mensagens úteis esperadas:

- [LoRa] SX1278 inicializado em 433 MHz.
- [CMD] Link com ignicao: OK
- [CMD] ACK recebido da base de ignicao.
- [CMD] Estado: CONFIRMED — IGNITION_COMPLETE recebido.

## Segurança

- Nunca testar com ignitor real na bancada.
- Usar carga dummy (lâmpada/LED + resistor) no GP26.
- Qualquer perda de comando durante a contagem deve abortar.
- Antena LoRa deve estar conectada antes de energizar.

## Legado

O arquivo [code.ino](code.ino) é legado para ESP32/ESP8266 (Arduino) e não faz parte do fluxo oficial atual com Raspberry Pi Pico + MicroPython.
