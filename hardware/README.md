# Hardware

Uma PCB, duas montagens. A placa é a mesma para baratear a fabricação; mudam
os componentes montados e o firmware.

| Item | Comando | Ignição |
| --- | --- | --- |
| MCU | ESP32 DevKit V1, 30 pinos | ESP32 DevKit V1, 30 pinos |
| LoRa | SX1278 433 MHz | SX1278 433 MHz |
| Botão J2/J3 | sim | não |
| LED do botão J4/J5 | sim | não |
| OLED J11 | sim | não |
| Relé J7/J8 | não | sim |
| Q1/Q2 e J12 (SMD) / J9 (PTH) | não | sim |
| LEDs D3/D4 | sim | sim |
| Buzzer J10 + Q4 | sim | sim |

A SMD mede 78,8 × 57,3 mm. A PTH mede 75 × 80 mm e tem quatro furos M3.

## Pinagem

| Função | GPIO | Comando | Ignição |
| --- | ---: | --- | --- |
| LoRa SCK | 18 | sim | sim |
| LoRa MISO | 19 | sim | sim |
| LoRa MOSI | 23 | sim | sim |
| LoRa NSS | 4 | sim | sim |
| LoRa RESET | 16 | sim | sim |
| LoRa DIO0 | 17 | sim | sim |
| LED STATUS | 25 | sim | sim |
| LED vermelho / contagem | 12 | sim | sim |
| LED do botão | 26 | sim | não |
| Botão | 27 | sim | não |
| Buzzer | 14 | sim | sim |
| OLED SDA | 21 | sim | não |
| OLED SCL | 22 | sim | não |
| Relé IN | 32 | não | sim |
| GATE_1 (Q2) | 13 | não | sim |
| GATE_2 (Q1) | 33 | não | sim |

O OLED usa I2C a 100 kHz. O módulo precisa ter os pull-ups da placa dele; a PCB
não tem pull-ups externos.

## Conectores

| Ref | Uso |
| --- | --- |
| J1 | entrada 5 V |
| J2/J3 | botão de comando (COM/NO) |
| J4/J5 | LED do botão |
| J7 | módulo relé (5 V, IN, GND chaveado) |
| J8 | ARM/RBF: fecha os pinos 1–3 e liga o VCC da bobina |
| J10 | buzzer |
| J11 | OLED I2C |
| J12 (SMD) / J9 (PTH) | dreno e source do Q1 (laço de ignição) |

## Laço de disparo

```text
BAT+ ── relé COM/NO ── ignitor ── J12.2 / J9.2 (dreno Q1)
Q1 source (J12.1 / J9.1) ───────── BAT− / GND
```

O Q1 é uma chave de baixo lado. O contato do relé e o Q1 ficam em série. A ordem
é: fecha o relé, depois liga o Q1; no fim, desliga o Q1 e só então abre o relé.
O firmware já faz nessa ordem.

Não ligue o ignitor entre J12.1 e J12.2: a carga fica em paralelo com o Q1.
Não inverta dreno e source: o diodo de corpo do IRLZ44N conduz e a carga dispara
mesmo com `GATE_2` em zero.

A fonte do laço é 2S (6,0 a 8,4 V). O J12/J9 é um borne de 3,5 mm; para 8 A de
pulso, use fio curto e grosso.

## Alimentação

```text
bateria 1S ── TP4056 ── boost 5 V ── J1
                                     ├── módulo relé (J7/J8)
                                     ├── buzzer (J10)
                                     └── ESP32 VIN ── regulador 3V3 ── LoRa/OLED/LEDs
```

O TP4056 é só carregador; o 5 V vem do boost (ou de um buck, se a bateria for
2S). A placa não tem proteção de polaridade nem fusível. Confira a polaridade
antes de energizar.

## Componentes principais

| Ref | Valor | Uso |
| --- | --- | --- |
| Q1 | IRLZ44N | chave de saída do ignitor |
| Q2 | S8050 | liga o GND da bobina do relé |
| Q4/Q3 | BC337 | driver do buzzer |
| D1 | SS34 (SMD) / 1N5818 (PTH) | diodo série da entrada |
| R2/R5 | 10 k | pull-down do gate/base |
| R4/R6 | 220 Ω | gate/base |
| R3 | 470 Ω | base do BC337 |
| R1/R7/R8 | 220 Ω | LEDs |

## Antes de energizar

- Antena LoRa conectada.
- Carga dummy no lugar do ignitor.
- J8 aberto na ignição.
- Botão solto no comando.
- Fonte limitada ou fusível no laço.

O estado atual das placas e os números de DRC ficam em
[`docs/ESTADO_DO_PROJETO.md`](../docs/ESTADO_DO_PROJETO.md).
