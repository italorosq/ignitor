# Testes

## No PC

```bash
python -m pytest test/ -q
```

O `test_firmware.py` confere:

- sintaxe dos dois firmwares;
- pinagem da ignição e do comando;
- tempos de segurança (10 s de contagem, 2 s de ignição, 500 ms de timeout);
- protocolo LoRa;
- relé ativo em baixo e gates nascendo desligados;
- scripts de bancada.

## Na bancada

Os scripts ficam em `test/bancada/` e vão para a placa junto com os módulos que eles importam. Use carga dummy no lugar do ignitor.

| Script | Placa | O que testa |
|---|---|---|
| `mp_teste_rele.py` | ESP32 | módulo relé, Q2 e intertravamento |
| `mp_teste_transistor.py` | ESP32 | cadeia Q1/Q2, ordem de arme e desarme |
| `mp_teste_comum.py` | apoio | buzzer, botão, OLED e telas |
| `mp_lora_radio.py` | apoio | rádio SX1278 |
| `mp_logo_serra.py` | apoio | bitmap da logo para o OLED |

## Antes de energizar

1. Antenas LoRa conectadas.
2. Carga dummy no lugar do ignitor.
3. Botão solto e J8 aberto na ignição.
4. Fonte limitada ou fusível no laço de disparo.
