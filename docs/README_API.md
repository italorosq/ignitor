# Protocolo LoRa

As duas estações falam o mesmo protocolo em 433 MHz.

## Parâmetros de rádio

| Parâmetro | Valor |
| --- | --- |
| Frequência | 433 MHz |
| Largura de banda | 125 kHz |
| Spreading Factor | 7 |
| Coding Rate | 4/5 |
| Potência TX | 17 dBm |

## Quadro

```text
IG1|<epoch>|<seq>|<ciclo>|<BODY>
```

| Campo | Uso |
| --- | --- |
| `IG1` | identificador do sistema; quadro de outro sistema é descartado |
| `epoch` | 8 dígitos hex, sorteado a cada boot |
| `seq` | incrementa a cada quadro; replay e sequência antiga são descartados |
| `ciclo` | incrementa a cada novo armamento; `0` nos quadros de serviço |
| `BODY` | mensagem ou `STATUS:<estado>` |

Exemplo:

```text
IG1|5A3C91E7|42|3|ARM_CONFIRMED
```

## Mensagens

| Mensagem | Direção | Uso |
| --- | --- | --- |
| `PING` | comando → ignição | teste de link no `IDLE` |
| `PONG` | ignição → comando | resposta ao `PING` |
| `ARM_CONFIRMED` | comando → ignição | botão mantido; repetido a cada 200 ms |
| `ACK` | ignição → comando | quadro recebido; também mantém o link vivo |
| `ABORT` | comando → ignição | cancela o ciclo |
| `STATUS:<estado>` | ignição → comando | `AGUARDANDO`, `CONTAGEM`, `IGNICAO`, `COMPLETO`, `ABORT` ou `BLOQUEADO` |
| `IGNITION_COMPLETE` | ignição → comando | queima concluída; dispara o Mario no comando |

## Tempos

| Parâmetro | Valor |
| --- | --- |
| Botão mantido até `CONFIRMADO` | ~13 s (10 s de contagem + 2 s de queima) |
| Retransmissão de `ARM_CONFIRMED` | 200 ms |
| Timeout na ignição | 500 ms |
| Timeout de link no comando | 3000 ms |
| Janela de ignição | 2 s |
| Gap para aceitar um ciclo novo | 1500 ms |
| Espera após a música de conclusão | 3000 ms |

## Músicas

| Evento | Música |
|---|---|
| Boot do comando | Zelda |
| Botão pressionado (`ARMING`) | Bip curto de 2 kHz a cada 1 s |
| `IGNITION_COMPLETE` | Mario |

## Regras

- A contagem só começa depois do primeiro `ARM_CONFIRMED`.
- Perda de `ARM_CONFIRMED` por mais de 500 ms aborta.
- Soltar o botão envia `ABORT` na hora, inclusive durante a queima.
- Depois de `IGNITION_COMPLETE`, o comando para de enviar ARM, toca o Mario e
  espera o botão ser solto e pressionado de novo.
- A ignição vai para `BLOQUEADO` após aborto ou queima. Só aceita outro ciclo
  depois de 1,5 s sem ARM e com um `ciclo` novo.
- O mesmo `ciclo` não pode gerar um segundo disparo.
- `IG1` + `epoch` + `seq` não são autenticação criptográfica. Servem para
  separar estações e rejeitar replay simples; o J8 continua sendo a trava
  física.
- O comando mostra no OLED o último `STATUS` recebido.
