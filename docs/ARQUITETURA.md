# Arquitetura

O sistema tem duas estações independentes ligadas por LoRa 433 MHz. A mesma PCB
é usada nas duas para baratear a fabricação; mudam a população e o firmware.

```text
Comando (ESP32 + OLED)            Ignição (ESP32)
botão, LEDs, buzzer, LoRa   ───►  LoRa, LEDs, buzzer
OLED de status              ◄───  relé, Q1/Q2
```

## Estações

| Estação | O que faz | O que tem |
| --- | --- | --- |
| Comando | arma, mostra o status e aborta | botão, OLED, LEDs, buzzer, LoRa |
| Ignição | recebe o comando e aciona o ignitor | relé, Q1/Q2, LEDs, buzzer, LoRa |

A ignição não tem botão, OLED, EXP nem ADC. O abort vem por `ABORT` ou pela
perda de `ARM_CONFIRMED`.

## Protocolo

| Parâmetro | Valor |
| --- | --- |
| Frequência | 433 MHz |
| Largura de banda | 125 kHz |
| Spreading Factor | 7 |
| Coding Rate | 4/5 |
| Potência TX | 17 dBm |
| `ARM_CONFIRMED` | a cada 200 ms |
| Timeout na ignição | 500 ms |
| Timeout de link no comando | 3000 ms |

Cada quadro tem o formato:

```text
IG1|<epoch>|<seq>|<ciclo>|<BODY>
```

- `IG1`: identificador do sistema.
- `epoch`: 8 dígitos hex, sorteado a cada boot.
- `seq`: incrementa a cada quadro; replay e sequência antiga são descartados.
- `ciclo`: incrementa a cada novo armamento; `0` nos quadros de serviço.
- `BODY`: `PING`, `PONG`, `ARM_CONFIRMED`, `ACK`, `ABORT`,
  `IGNITION_COMPLETE` ou `STATUS:<estado>`.

## Sequência

1. No `IDLE`, o comando manda `PING` a cada 1 s. A ignição responde `PONG`.
2. O operador segura o botão até o OLED mostrar `CONFIRMADO` (cerca de 13 s).
   O comando manda `ARM_CONFIRMED` a cada 200 ms.
3. A ignição responde `ACK` e começa a contagem de 10 s.
4. Se o `ARM_CONFIRMED` sumir por mais de 500 ms, ou chegar `ABORT`, a ignição
   desliga tudo e vai para `BLOQUEADO`.
5. No fim, a ignição fecha o relé e liga o Q1 por 2 s.
6. A ignição manda `IGNITION_COMPLETE`; o comando mostra o resultado no OLED,
   toca o tema do Mario e espera um novo ciclo.
7. Soltar o botão a qualquer momento, inclusive durante a queima, manda `ABORT`.

Ao energizar, o comando toca o tema do **Zelda**; enquanto o botão está
pressionado, dá um bip curto por segundo; no fim da queima, o tema do
**Mario**. A ignição também manda `STATUS:AGUARDANDO`, `STATUS:CONTAGEM`,
`STATUS:IGNICAO`, `STATUS:COMPLETO`, `STATUS:ABORT` e `STATUS:BLOQUEADO`.
O comando usa o último status para atualizar o OLED.

## Laço de disparo

```text
BAT+ ── relé COM/NO ── ignitor ── Q1 dreno
Q1 source ───────────────────────── BAT− / GND
```

O relé e o Q1 ficam em série. O Q1 é uma chave de baixo lado; a fonte do laço é
2S (6,0 a 8,4 V). O firmware fecha o relé antes de ligar o Q1 e desliga o Q1
antes de abrir o relé.

## Alimentação

```text
bateria 1S ── TP4056 ── boost 5 V ── J1
                                     ├── relé
                                     ├── buzzer
                                     └── ESP32 ── 3V3 ── LoRa / OLED / LEDs
```

O TP4056 é carregador; o 5 V vem do boost (ou de um buck, se a bateria for 2S).
A placa não tem proteção de polaridade nem fusível.

## Firmware

- `firmware/micropython/estacao_comando_esp.py`: comando com OLED.
- `firmware/micropython/estacao_ignicao_esp.py`: ignição sem OLED.
- `firmware/micropython/legacy/`: versões Pico, não usadas nas placas atuais.

## Segurança

- Carga dummy antes de ignitor real.
- Antena LoRa conectada antes de energizar.
- J8 (ARM/RBF) aberto fora do teste.
- Operador a pelo menos 10 m do foguete.
- Botão solto a qualquer momento aborta na hora. Só solte após `CONFIRMADO`.
- Perda de `ARM_CONFIRMED` por mais de 500 ms aborta na hora.
- Depois de um abort ou de uma queima, solte o botão antes de tentar de novo.
- A ignição só aceita um ciclo novo depois de 1,5 s sem ARM.
- O link de 3 s do comando é supervisão; o corte real é o timeout de 500 ms da
  ignição.
- `IG1` + sequência separam estações e rejeitam replay simples, mas não são
  autenticação criptográfica. O J8 continua sendo a trava física.
