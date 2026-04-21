# API e Protocolo

> Protocolo de comunicação entre as duas estações via LoRa 433 MHz.

## Camada Física

| Parâmetro | Valor |
|----------|------|
| Frequência | 433 MHz |
| Largura de banda | 125 kHz |
| Spreading Factor | 7 |
| Coding Rate | 4/5 |
| Potência TX | 17 dBm |

## Mensagens

| Mensagem | Direção | Uso |
|----------|---------|-----|
| PING | Comando → Ignição | Teste de conexão |
| PONG | Ignição → Comando | Resposta ao PING |
| ARM_CONFIRMED | Comando → Ignição | Comando mantido (retransmitido a cada 200 ms) |
| ACK | Ignição → Comando | Confirma recebimento e início da contagem |
| ABORT | Comando → Ignição | Cancela imediatamente |
| IGNITION_COMPLETE | Ignição → Comando | Ciclo concluído |

## Diagrama de Estados

```
        ┌──────────┐
        │  IDLE    │
        └────┬─────┘
             │ PONG
        ┌────▼─────┐
   ┌────│ CONNECTED│◄──┐
   │    └────┬─────┘   │
   │         │ARM_CONFIRMED
   │    ┌───▼──────┐   │ timeout
   │    │ COUNTDOWN │───┴───┘
   │    └────┬─────┘
   │         │ fim (5s)
   │    ┌───▼──────┐
   └───►│ IGNITION │──────► ACK
        └──────────┘
```

## Timeouts

| Parâmetro | Valor |
|----------|------|
| Retransmissão ARM_CONFIRMED | 200 ms |
| Timeout de comando (Ignição) | 500 ms |
| Timeout de link (Comando) | 3000 ms |
| Espera após IGNITION_COMPLETE | 3000 ms |

## Regras de Segurança

- Contagem só inicia após `ACK` recebido
- Perda de `ARM_CONFIRMED` por > 500 ms aborta
- Soltar botão envia `ABORT` imediatamente
- Verificação final antes de acionar relé

Consulte [software/estacao_ignicao_esp.py](../software/estacao_ignicao_esp.py) para implementação de referência.