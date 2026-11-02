# Resultados de Testes

## Matriz de Testes

| ID | Tipo | Descrição | Critério | Status |
|----|------|---------|---------|--------|
| LORA-01 | LoRa | PING/PONG bidirecional | PONG < 500 ms | Pendente |
| LORA-02 | LoRa | RSSI a 50 m | RSSI > -80 dBm | Pendente |
| LORA-03 | LoRa | RSSI a 500 m | RSSI > -120 dBm | Pendente |
| IGN-01 | Ignição | Sequência completa (5 s) | Relé aciona após 5 s | Pendente |
| IGN-02 | Ignição | Contagem de apitos | 5 apitos audíveis | Pendente |
| IGN-03 | Ignição | LEDs | Vermelho pisca → sólido | Pendente |
| IGN-04 | Ignição | Sequência isolada (`mp_teste_ignicao.py`) | Contagem 5 s + abort + janela 2 s | Pendente |
| TRX-01 | Segurança | Fail-safe dos gates no boot (`mp_teste_transistor.py`) | Q1/Q2 = 0 e IN inativo | Pendente |
| TRX-02 | Segurança | Ordem de arme da cadeia | LED dummy só acende no passo 3 | Pendente |
| TRX-03 | Segurança | Ordem de desarme / abort | Q1 → relé → Q2 | Pendente |
| RELE-01 | Relé | Interlock sem Q2 (`mp_teste_rele.py`) | Sem clique com GATE_1 OFF | Pendente |
| RELE-02 | Relé | 10 ciclos automáticos | 10 cliques sem falha | Pendente |
| ABORT-01 | Segurança | Abort manual | Botão solto cancela | Pendente |
| ABORT-02 | Segurança | Abort por timeout | Perda > 500 ms cancela | Pendente |

**Status**: Pendente | Passou | Falhou

## Registro de Sessões

| Data | ID | Resultado | Distância | RSSI | Observações |
|------|----|---------|---------|------|-----------|
| - | - | - | - | - | - |

- Logs salvos em `test/logs/` (não versionado)
- Vídeos/fotos grandes linkados externamente

## Procedimento

Após cada sessão:

1. Preencher registro acima
2. Salvar logs em `test/logs/sessao_YYYYMMDD.csv`
3. Linkar evidências no registro

Consulte [test/README.md](../test/README.md) para procedimentos detalhados.