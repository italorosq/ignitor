# API e Protocolo

## Visão Geral

O sistema usa protocolo textual simples entre Estação de Comando e Estação de Ignição via LoRa.

Este documento descreve o comportamento atualmente implementado no firmware MicroPython em [../software/estacao_comando.py](../software/estacao_comando.py) e [../software/estacao_ignicao.py](../software/estacao_ignicao.py).

## Camada Física

- Frequência: 433 MHz
- Largura de banda: 125 kHz
- Spreading Factor: 7
- Coding Rate: 4/5
- Potência TX: 17 dBm

## Mensagens Textuais

| Mensagem | Direção | Uso |
| --- | --- | --- |
| PING | Comando -> Ignição e Ignição -> Comando | Teste de conexão |
| PONG | Resposta ao PING | Confirma link |
| ARM_CONFIRMED | Comando -> Ignição | Mantém comando de arme ativo |
| ACK | Ignição -> Comando | Confirma recepção de ARM e início de contagem |
| ABORT | Comando -> Ignição | Cancela sequência imediatamente |
| IGNITION_COMPLETE | Ignição -> Comando | Informa que relé foi acionado e ciclo concluído |

## Fluxo Operacional

### 1. Conexão

1. Em idle, a Estação de Comando envia PING periódico.
2. A Estação de Ignição responde com PONG sempre que recebe PING.
3. Comando só permite armamento com link ativo (PONG recente).

### 2. Sequência de Ignição

1. Operador mantém botão pressionado por 5 segundos (validação local no Comando).
2. Comando entra em transmissão e envia ARM_CONFIRMED de forma contínua.
3. Ignição, ao receber ARM_CONFIRMED, responde ACK e inicia contagem regressiva de 5 segundos.
4. Durante a contagem, Ignição exige ARM contínuo.
5. Se botão for solto no Comando, ele envia ABORT e a Ignição cancela.
6. Ao fim da contagem, Ignição aciona relé e buzzer por 2 segundos.
7. Ignição envia IGNITION_COMPLETE para o Comando.
8. Comando entra em finalização, aguarda 3 segundos e emite 2 bipes.

### 3. Regras de Abort

Na Estação de Ignição:

- ABORT recebido durante contagem cancela ignição.
- Perda de ARM por mais de 500 ms cancela ignição.
- Verificação final de segurança ocorre imediatamente antes de ligar o relé.

## Timeouts Implementados

| Parâmetro | Valor |
| --- | --- |
| Intervalo de retransmissão de ARM_CONFIRMED | 200 ms |
| Timeout de perda de comando na Ignição | 500 ms |
| Timeout de link no Comando (sem PONG) | 3000 ms |
| Espera final no Comando após IGNITION_COMPLETE | 3000 ms |

## Observações

1. A versão atual não usa pacote binário com CRC explícito no payload da aplicação.
2. A validação de erro de pacote no lado LoRa é feita via flags do rádio.
3. O protocolo textual foi mantido por decisão de projeto para simplificar a bancada inicial.
