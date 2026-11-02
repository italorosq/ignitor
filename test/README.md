# Plano de Testes

## Objetivos

- Validar comunicacao LoRa bidirecional entre as estacoes.
- Confirmar sequencia de seguranca com botao mantido por 5 s.
- Testar feedback visual (LEDs) e sonoro (buzzers).
- Verificar abort manual e abort por timeout.

## Requisito Inicial

Antes de qualquer teste, confirme as duas antenas LoRa conectadas e apertadas.

## Testes Prioritarios

### 1. Comunicacao LoRa Basica

Objetivo: confirmar `PING/PONG` de forma estavel.

Checklist:

- [ ] Comando envia `PING` e ignicao responde `PONG`.
- [ ] LED amarelo acende nas duas estacoes quando conectadas.
- [ ] Ao desligar uma estacao, timeout de link ocorre conforme esperado.

Procedimento:

1. Ligar as duas estacoes a 1 m.
2. Observar serial e LEDs.
3. Repetir em 10 m, 50 m, 100 m e 500 m.
4. Registrar RSSI e perdas.

### 2. Sequencia de Ignicao Completa

Objetivo: validar contagem e acionamento final.

Checklist:

- [ ] Botao mantido por 5 s.
- [ ] LED vermelho pisca durante contagem.
- [ ] Buzzer da ignicao emite 5 apitos.
- [ ] Saida de ignicao aciona por 2 s.
- [ ] Comando recebe `IGNITION_COMPLETE`.

Procedimento:

1. Conectar carga dummy na saida de ignicao.
2. Segurar botao de ignicao por 5 s.
3. Confirmar acionamento apenas no final da contagem.

### 3. Abort Manual

Objetivo: garantir cancelamento ao soltar o botao.

Checklist:

- [ ] Botao solto antes de 5 s envia `ABORT`.
- [ ] Contagem para imediatamente.
- [ ] Ignitor nao e acionado.

Procedimento:

1. Iniciar contagem.
2. Soltar no 2o ou 3o apito.
3. Repetir cinco vezes.

### 4. Abort por Timeout

Objetivo: abortar em perda de `ARM_CONFIRMED`.

Checklist:

- [ ] Durante contagem, interromper link/comando.
- [ ] Ignicao detecta timeout (> 500 ms).
- [ ] Estado de erro e sinalizado.
- [ ] Ignitor nao e acionado.

### 5. Alcance em Campo

Objetivo: determinar alcance confiavel do enlace.

Checklist:

- [ ] Executar testes em linha de visao.
- [ ] Avaliar 50 m, 100 m, 200 m, 500 m e 1 km.
- [ ] Registrar taxa de sucesso e RSSI.

## Scripts

Arquivos da pasta `test/`:

Testes de bancada (rodam **na placa**, MicroPython):

- `mp_teste_comum.py`: infraestrutura compartilhada (buzzer, botao, I2C/OLED,
  telas, sequencia de ignicao e logo). Vai para a placa junto com o script.
- `mp_lora_radio.py`: modulo comum de radio.
- `mp_teste_conexao.py`: link `PING/PONG` com estatisticas.
- `mp_teste_envio_dados.py`: envio `DATA` com `ACK` e retry.
- `mp_teste_hardware_esp8266.py`: OLED + buzzer + botao + LED do botao no
  ESP8266 (bancada, sem LoRa).
- `mp_teste_ignicao.py`: sequencia de ignicao isolada no ESP8266 (contagem
  de 5 s, abort e janela de saida de 2 s).
- `mp_teste_transistor.py`: cadeia de seguranca Q1/Q2 no ESP32 (fail-safe no
  boot, ordem de arme/desarme e abort, com carga dummy).
- `mp_teste_rele.py`: modulo rele SRD-05VDC no ESP32 (interlock sem Q2,
  toggles manuais e 10 ciclos automaticos).
- `mp_logo_serra.py`: bitmap 1-bit da logo (68x56), usada nas telas de
  sucesso.
- `esp8266_main.py`: bootstrap que vai como `main.py` (o boot do ESP8266 so
  executa `main.py`).

Testes estaticos (rodam **no PC**, sem placa):

- `test_pinagem.py`: confere pinagem, tempos de seguranca e protocolo LoRa
  contra o mapa oficial do projeto, por analise estatica dos firmwares.
- `test_scripts_bancada.py`: compila todos os `mp_*.py` (pega erro de sintaxe
  antes de subir para a placa) e confere a seguranca da bancada: pinos ESP32
  iguais aos do firmware, gates OFF no boot, rele inativo e ordem de desarme
  Q1 -> rele -> Q2.

Uso em duas placas:

1. Copiar `mp_lora_radio.py` e o script desejado.
2. Ajustar `ROLE` no topo.
3. `initiator` e `responder` para teste de conexao.
4. `tx` e `rx` para teste de envio de dados.

Os scripts seguem a configuracao de radio em `firmware/micropython/`.

### Teste de bancada no ESP8266 (tela + buzzer + botao + LED)

Firmware dedicado para validar OLED, buzzer, botao e LED do botao em uma
placa ESP8266 (NodeMCU v3 / Wemos D1 mini) antes de energizar o hardware
final: `mp_teste_hardware_esp8266.py`. Teste isolado: nao usa LoRa.

Ligacao (rotulos da placa):

| Sinal | Pino da placa | GPIO |
| --- | --- | --- |
| OLED SDA | D2 | GPIO4 |
| OLED SCL | D1 | GPIO5 |
| Buzzer ativo 3,3 V | D5 | GPIO14 |
| Botao (outro terminal em GND) | D6 | GPIO12 |
| LED do botao (~220R para GND) | D7 | GPIO13 |

Uso:

1. Enviar `ssd1306.py` do firmware e os modulos do teste para a placa.
2. Aperte o botao: a tela mostra o comando de ignicao com contagem de 5 s
   (um bip por segundo, LED do botao piscando).
3. Aperte de novo durante a contagem para ABORTAR (teste de seguranca).
4. No fim: tela "FOGO!" com saida simulada de 2 s, `IGNITION_COMPLETE` no
   serial, som do Mario no buzzer e a logo da Serra Rocketry na tela.
5. Em repouso o LED do botao pisca 100 ms a cada 1 s (heartbeat).

```bash
mpy-cross -march=xtensa -o ignitor_teste.mpy mp_teste_hardware_esp8266.py
mpy-cross -march=xtensa -o mp_teste_comum.mpy mp_teste_comum.py
mpy-cross -march=xtensa -o mp_logo_serra.mpy mp_logo_serra.py
mpremote connect COM5 fs cp ../firmware/micropython/ssd1306.py :ssd1306.py
mpremote connect COM5 fs cp esp8266_main.py :main.py
mpremote connect COM5 fs cp ignitor_teste.mpy :ignitor_teste.mpy
mpremote connect COM5 fs cp mp_teste_comum.mpy :mp_teste_comum.mpy
mpremote connect COM5 fs cp mp_logo_serra.mpy :mp_logo_serra.mpy
```

Observacoes:

- O firmware vai como `.mpy` (mpy-cross com a mesma versao do MicroPython
  gravado na placa): o port ESP8266 nao consegue compilar os ~19 KB de fonte
  em RAM (`MemoryError` no boot). `mp_teste_comum.py` vai como `.mpy` pelo
  mesmo motivo.
- Se o OLED nao responder no scan I2C, o teste segue com buzzer, botao e
  LED, repetindo o status no serial a 115200.

### Teste de bancada no ESP8266 (sequencia de ignicao isolada)

`mp_teste_ignicao.py` usa a mesma ligacao acima e valida so a logica da
sequencia (contagem de 5 s, abort pelo botao e janela de saida de 2 s). Para
roda-lo no lugar do teste de perifericos, compile-o para o mesmo nome que o
bootstrap importa:

```bash
mpy-cross -march=xtensa -o ignitor_teste.mpy mp_teste_ignicao.py
mpremote connect COM5 fs cp ignitor_teste.mpy :ignitor_teste.mpy
```

### Teste de bancada no ESP32 (cadeia de seguranca Q1/Q2)

`mp_teste_transistor.py` valida a cadeia em serie dos MOSFETs: Q2 (GATE_1,
que liga o GND do modulo rele) e Q1 (GATE_2, chave de saida do ignitor).

**Nunca ligue um ignitor real.** Use carga dummy (LED + resistor de 1k).

| Sinal | Ligacao | Observacao |
| --- | --- | --- |
| Modulo rele VCC / GND | 5V / GND | alimentacao do modulo |
| Modulo rele IN | GPIO32 | ativo em baixo (so clica com Q2 ligado) |
| Q2 / GATE_1 | GPIO13 | nativo da placa: chaveia o GND do modulo |
| Q1 / GATE_2 | GPIO33 | nativo da placa: chave de saida do ignitor |
| Ignitor (dummy) | LED + 1k no lugar do ignitor | **nunca** ligar ignitor real |
| Buzzer ativo | GPIO14 | + em GPIO14, - em GND |
| Botao | GPIO27 | outro terminal em GND |

Passos (botao curto avanca; botao longo aborta):

1. `GATE_1` (Q2) ON: modulo rele **energiza** (sem click ainda).
2. `RELE` ON (IN em baixo): modulo **clica**; LED dummy segue apagado
   (Q1 aberto = interlock).
3. `GATE_2` (Q1) ON: LED dummy **acende por 2 s** (janela do firmware).
4. Desarme automatico na ordem segura: Q1 -> rele -> Q2.

No boot o script confere o fail-safe: se Q1/Q2 nao estiverem OFF ou o IN do
rele estiver ativo, o teste **bloqueia** com alarme no buzzer.

```bash
mpremote connect COM5 fs cp mp_teste_comum.py :mp_teste_comum.py
mpremote connect COM5 run mp_teste_transistor.py
```

### Teste de bancada no ESP32 (modulo rele SRD-05VDC)

`mp_teste_rele.py` valida a entrada IN ativo em baixo, o click do contato e
o interlock com Q2 (sem GATE_1 o modulo nem energiza). Mesma ligacao da
tabela acima; `GATE_2` fica fixado em OFF.

Testes:

1. **Interlock** (automatico no boot): com `GATE_1` OFF, pulso de 1,5 s no
   IN. O modulo **nao pode clicar**; se clicar, PARE e revise o hardware.
2. **Toggles manuais**: clique curto alterna o rele (bipe sincronizado).
3. **Ciclos automaticos**: clique longo roda 10 ciclos de 500 ms; um clique
   durante os ciclos cancela e desliga o rele.

```bash
mpremote connect COM5 fs cp mp_teste_comum.py :mp_teste_comum.py
mpremote connect COM5 run mp_teste_rele.py
```

## Execucao

### Testes Automatizados (no PC)

```bash
pip install -r ../requirements-dev.txt
python -m pytest test_pinagem.py test_scripts_bancada.py -v
# ou, sem pytest instalado:
python test_pinagem.py
python test_scripts_bancada.py
```

Nao exigem placa conectada: leem os fontes em `../firmware/micropython/` e
`test/`, compilam os scripts e comparam com o mapa oficial de pinos.

### Testes Manuais

Seguir os procedimentos acima e registrar resultado em `docs/README_TESTS.md`.

## Seguranca

- Nunca usar ignitor real em bancada.
- Sempre usar carga dummy (LED + resistor).
- Nos testes do ESP32, o IN do rele e os gates Q1/Q2 nascem desligados e o
  script bloqueia se o fail-safe falhar.
- Manter pessoas a pelo menos 10 m.
- Usar EPI adequado durante testes energizados.
