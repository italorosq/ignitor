# Serra Rocketry Ignitor

Sistema de ignição remota para foguetes experimentais. Duas estações
independentes conversam por LoRa 433 MHz.

A mesma PCB é usada nas duas estações para baratear a fabricação. O que muda é
a população e o firmware:

| Estação | Firmware | Módulos ligados |
| --- | --- | --- |
| Comando | `estacao_comando_esp.py` | botão, OLED, LEDs, buzzer, LoRa |
| Ignição | `estacao_ignicao_esp.py` | relé, Q1/Q2, LEDs, buzzer, LoRa |

Na estação de comando não são montados Q1, Q2, J7/J8/J12 nem o módulo relé. Na
ignição, o OLED (J11) não é montado. O resto da placa é comum.

## Como funciona

1. O operador segura o botão por **10 s**.
2. O comando transmite `ARM_CONFIRMED` a cada 200 ms.
3. A ignição responde `ACK` e começa a contagem de **10 s**.
4. Se o comando sumir por mais de **500 ms**, a ignição aborta.
5. No fim da contagem, o relé e o Q1 fecham por **2 s**.
6. A ignição envia `IGNITION_COMPLETE`. O comando mostra o resultado no OLED e
   toca o tema do Mario no buzzer.

O laço de disparo usa duas chaves em série: o contato do relé e o Q1. O Q1 fica
no lado de baixo:

```text
BAT+ ── relé COM/NO ── ignitor ── J12.2 (dreno Q1)
Q1 source (J12.1) ──────────────── BAT−
```

Não ligue o ignitor entre J12.1 e J12.2: isso coloca a carga em paralelo com o
Q1. Também não inverta dreno e source; o diodo de corpo do MOSFET conduz e a
carga dispara mesmo com `GATE_2` em zero.

## Firmware

- Comando: `firmware/micropython/estacao_comando_esp.py` (ESP32 + OLED).
- Ignição: `firmware/micropython/estacao_ignicao_esp.py` (ESP32, sem OLED).
- Pico: `firmware/micropython/legacy/` (não é usado nas placas atuais).

Os dois firmwares são independentes. O comando não carrega código de relé ou
ADC; a ignição não carrega código de OLED, botão ou EXP.

## Placas

| Placa | Dimensão | Estado |
| --- | --- | --- |
| Ignição SMD | 78,8 × 57,3 mm | candidata; conferir DRC antes de fabricar |
| Ignição PTH | 75 × 80 mm | funcional; limpeza de serigrafia pendente |
| Ignição CNC | 50 × 90 mm | em projeto |

## Segurança

- Use carga dummy antes de qualquer ignitor real.
- Conecte a antena LoRa antes de energizar.
- Feche o J8 (ARM/RBF) só no momento do teste.
- Mantenha o operador a pelo menos 10 m do foguete.
- O botão de comando é momentâneo: soltar antes dos 10 s aborta na hora.
- Depois de um abort, solte o botão antes de tentar de novo.
- A ignição não tem botão local; o abort vem por LoRa ou pela perda de sinal.

## Documentação

- [Arquitetura](docs/ARQUITETURA.md)
- [Instalação](docs/INSTALL.md)
- [Protocolo](docs/README_API.md)
- [Estado do projeto](docs/ESTADO_DO_PROJETO.md)
- [Testes](test/README.md)

Projeto da [Serra Rocketry](https://github.com/Serra-Rocketry).
