# Protocolo LoRa

As duas estações falam o mesmo protocolo em 433 MHz.

| Parâmetro | Valor |
| --- | --- |
| Frequência | 433 MHz |
| Largura de banda | 125 kHz |
| Spreading Factor | 7 |
| Coding Rate | 4/5 |
| Potência TX | 17 dBm |

## Mensagens

| Mensagem | Direção | Uso |
| --- | --- | --- |
| `PING` | comando → ignição | teste de link |
| `PONG` | ignição → comando | resposta ao PING |
| `ARM_CONFIRMED` | comando → ignição | botão mantido; repetido a cada 200 ms |
| `ACK` | ignição → comando | comando recebido, contagem iniciada |
| `ABORT` | comando → ignição | cancela |
| `STATUS:<estado>` | ignição → comando | `AGUARDANDO`, `CONTAGEM`, `IGNICAO`, `COMPLETO` ou `ABORT` |
| `IGNITION_COMPLETE` | ignição → comando | ciclo concluído |

## Tempos

| Parâmetro | Valor |
| --- | --- |
| Botão mantido | 10 s |
| Retransmissão de `ARM_CONFIRMED` | 200 ms |
| Timeout na ignição | 500 ms |
| Timeout de link no comando | 1000 ms |
| Janela de ignição | 2 s |
| Espera após o Mario | 3000 ms |

## Regras

- A contagem só começa depois do `ACK`.
- Perda de `ARM_CONFIRMED` por mais de 500 ms aborta.
- Soltar o botão envia `ABORT` na hora.
- A ignição não tem botão local; o abort vem por LoRa ou por timeout.
- Depois de um abort, o comando exige que o botão seja solto antes de rearmar.
- O comando mostra no OLED o último `STATUS` recebido.
