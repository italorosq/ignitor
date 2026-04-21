# Plano de Testes

## Objetivos
- Validar comunicação LoRa bidirecional entre as duas estações
- Confirmar sequência de segurança (botão mantido por 5 s)
- Testar feedback visual (LEDs) e sonoro (buzzers) em ambas estações
- Verificar abort automático e manual

## Testes Prioritários

### 1. Comunicação LoRa Básica
**Objetivo:** Confirmar que as duas estações se comunicam de forma confiável.

Antes de começar, confirme que as duas antenas LoRa estão conectadas. Sem antena, o módulo pode inicializar normalmente e ainda assim não fechar enlace.

Checklist:
- [ ] Estação de Comando envia `PING`, Estação de Ignição responde com `PONG`
- [ ] LED amarelo acende em ambas estações quando conectadas
- [ ] Testar perda de comunicação: desligar uma estação e verificar timeout

**Procedimento:**
1. Ligar ambas estações a 1 m de distância
2. Observar LEDs e monitor serial
3. Afastar estações gradualmente (10 m, 50 m, 100 m, 500 m)
4. Registrar RSSI e taxa de perda de pacotes
5. Se não houver PING/PONG, conferir primeiro antenas, depois SPI e alimentação

### 2. Sequência de Ignição Completa
**Objetivo:** Validar contagem regressiva de 5 segundos e acionamento do ignitor.

Checklist:
- [ ] Pressionar botão de ignição na Estação de Comando por 5 s completos
- [ ] LED vermelho pisca em ambas estações durante contagem
- [ ] Buzzer da Estação de Ignição emite 5 apitos (1 por segundo)
- [ ] Ao final, GP26 da Estação de Ignição vai HIGH por 2 s
- [ ] Estação de Comando recebe `IGNITION_COMPLETE`
- [ ] LED vermelho fica sólido ao acionar ignitor
- [ ] Usar **carga dummy** (lâmpada 12 V ou LED) no lugar do ignitor real

**Procedimento:**
1. Conectar lâmpada/LED ao GP26 da Estação de Ignição
2. Pressionar e **segurar** botão de ignição
3. Observar: LEDs, buzzers, e acionamento da carga
4. Confirmar que lâmpada acende apenas após 5 s

### 3. Abort Manual
**Objetivo:** Garantir que soltar o botão antes de 5 s cancela a ignição.

Checklist:
- [ ] Pressionar botão de ignição
- [ ] Soltar botão após 2-3 segundos
- [ ] Estação de Comando envia `ABORT`
- [ ] Estação de Ignição interrompe contagem
- [ ] Ambas voltam ao estado `CONNECTED` (LED amarelo)
- [ ] Ignitor **não** é acionado

**Procedimento:**
1. Iniciar sequência de ignição
2. Soltar botão no 2º ou 3º apito
3. Verificar que GP26 permanece LOW
4. Repetir 5 vezes para consistência

### 4. Abort Automático por Timeout
**Objetivo:** Estação de Ignição aborta se perder comunicação durante sequência.

Checklist:
- [ ] Iniciar sequência de ignição
- [ ] Desligar Estação de Comando no 3º segundo
- [ ] Estação de Ignição detecta timeout (> 500 ms sem `ARM_CONFIRMED`)
- [ ] LED vermelho pisca rapidamente (erro)
- [ ] Buzzer emite padrão de erro
- [ ] Ignitor **não** é acionado

**Procedimento:**
1. Iniciar sequência de ignição
2. Desconectar antena ou desligar Estação de Comando após 2-3 s
3. Observar comportamento da Estação de Ignição

### 5. Indicadores Visuais e Sonoros
**Objetivo:** Confirmar padrões de LEDs e buzzer conforme especificação.

Checklist:
- [ ] **Amarelo:** acende quando conectado (PING/PONG OK)
- [ ] **Vermelho:** pisca durante ignição iminente, sólido ao acionar
- [ ] **Buzzer Ignição:** 5 apitos durante contagem + tom longo ao acionar
- [ ] **Buzzer Comando:** pisca junto com LED amarelo durante armamento

**Procedimento:**
1. Testar cada estado individualmente via comandos seriais (debug)
2. Testar sequência completa e documentar com vídeo

### 6. Teste de Alcance em Campo
**Objetivo:** Determinar alcance máximo confiável.

Não remover antenas durante o teste; antena ausente invalida a medição de alcance.

Checklist:
- [ ] Posicionar estações em LOS (linha de visão)
- [ ] Aumentar distância: 50 m, 100 m, 200 m, 500 m, 1 km
- [ ] Registrar RSSI e taxa de sucesso de pacotes
- [ ] Executar sequência completa de ignição na distância máxima validada

**Procedimento:**
1. Usar tripé/suporte para estações
2. Medir distância com GPS ou trena a laser
3. Executar 10 ciclos de ignição (com carga dummy) em cada distância
4. Registrar falhas em `docs/README_TESTS.md`

## Scripts MicroPython de Bancada

Novos scripts na pasta `test/`:

- `mp_lora_radio.py`: modulo comum de radio LoRa (sx127x + fallback nativo SPI)
- `mp_teste_conexao.py`: teste de link com `PING/PONG`, RTT e taxa de sucesso
- `mp_teste_envio_dados.py`: envio de payload `DATA` com `ACK`, retry e estatisticas

### Execucao no Pico (duas placas)

1. Copiar para cada Pico os arquivos `mp_lora_radio.py` e o script de teste desejado
2. Ajustar `ROLE` no topo do script:
	- Conexao: `initiator` em uma placa e `responder` na outra
	- Envio de dados: `tx` em uma placa e `rx` na outra
3. Executar o script no REPL/Thonny e observar os logs seriais
4. Repetir o teste em diferentes distancias para validar estabilidade

Obs.: os scripts usam a mesma configuracao do projeto (433 MHz, BW 125 kHz, SF7, CR 4/5).

## Como Executar

### Testes Automatizados
```bash
cd test
python run_tests.py --all         # todos os testes
python run_tests.py --lora        # apenas comunicação LoRa
python run_tests.py --ignition    # sequência de ignição
```

### Testes Manuais
Seguir procedimentos descritos acima. Documentar resultados em `docs/README_TESTS.md`.

## Segurança nos Testes

⚠️ **NUNCA usar ignitor real durante testes!**

- Sempre usar carga dummy (lâmpada, LED, resistor)
- Confirmar que não há propelente próximo
- Testar a >= 10 m de pessoas
- Usar óculos de proteção ao manipular eletrônica energizada

## Registro de Resultados

Após cada sessão de testes, preencher tabela em `docs/README_TESTS.md` com:
- Data
- ID do teste
- Resultado (pass/fail)
- Observações
- Link para logs/vídeos
