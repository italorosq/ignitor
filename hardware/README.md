# Hardware - Serra Rocketry Ignitor

## Arquitetura do Sistema

O sistema é composto por **duas estações independentes** que se comunicam via rádio LoRa:

### 1. Estação de Comando
Operada remotamente pelo operador (distância segura do foguete).

**Função:**
- Iniciar sequência de ignição via botão dedicado
- Monitorar status da Estação de Ignição
- Fornecer feedback visual e sonoro ao operador

**Componentes:**
- 1x Raspberry Pi Pico
- 1x Módulo LoRa SX1278 433 MHz
- 1x Botão liga/desliga
- 1x Botão de ignição (ação mantida por 5 s)
- 2x LEDs: amarelo (conectado), vermelho (ignição iminente)
- 1x Buzzer ativo
- 1x Módulo TP4056 (com proteção) para recarregar a bateria
- 1x Bateria (a definir capacidade)
- Case impresso em 3D

### 2. Estação de Ignição
Conectada fisicamente ao ignitor do foguete.

**Função:**
- Receber comandos de ignição da Estação de Comando
- Executar contagem regressiva (5 s) com avisos sonoros
- Acionar o ignitor ao final da contagem
- Abortar procedimento se comando for interrompido

**Componentes:**
- 1x ESP32-C3 SuperMini
- 1x Módulo LoRa SX1278 433 MHz
- 2x LEDs: amarelo (conectado), vermelho (ignição iminente)
- 1x Buzzer ativo
- 1x Relé para acionamento do ignitor
- 1x Módulo TP4056 (com proteção) para recarregar a bateria
- 1x Bateria (a definir capacidade)
- Case impresso em 3D

## Lista de Componentes (BOM)

| Componente | Quantidade | Referência | Especificação | Link |
|------------|------------|------------|---------------|------|
| Raspberry Pi Pico | 1 | MCU1 | RP2040 | [Raspberry Pi](https://www.raspberrypi.com/products/raspberry-pi-pico/) |
| ESP32-C3 SuperMini | 1 | MCU2 | RISC-V 32 bits | [ESP32-C3 SuperMini](https://docs.espressif.com/projects/esp-idf/en/latest/esp32c3/hw-reference/esp32c3/user-guide-supermini.html) |
| Módulo LoRa SX1278 | 2 | LORA1, LORA2 | 433 MHz | [Hoperf](https://www.hoperf.com/) |
| LED Amarelo 5mm | 2 | LED_Y1, LED_Y2 | 20 mA | - |
| LED Vermelho 5mm | 2 | LED_R1, LED_R2 | 20 mA | - |
| Buzzer ativo 5V | 2 | BZ1, BZ2 | Piezo | - |
| Botão Liga/Desliga | 2 | BTN_PWR1, BTN_PWR2 | 12V 20A | - |
| Botão de Ignição | 1 | BTN_IGN | 22mm, 3-9V (5V), Momentary Reset, Vermelho | - |
| Relé | 1 | K1 | Para ignitor (corrente a definir) | - |
| Bateria | 12 | BAT1, BAT2 | A definir (LiPo/18650) | - |
| Resistores 220Ω | 4 | R1-R4 | Para LEDs | - |
| Antena LoRa | 2 | ANT1, ANT2 | 433 MHz | - |
| Módulo TP4056 | 2 | CHG1, CHG2 | Carregador Li-ion/LiPo 1 célula (4,2 V), entrada 5 V, corrente de carga ajustável (até 1 A), proteção recomendada (DW01A+8205A) | - |

## Pinagem

### Estação de Comando - Raspberry Pi Pico
| GPIO Pico | Conexão | Descrição |
|-----------|---------|-----------|
| GP0 | LoRa SPI RX | SPI MISO |
| GP1 | LoRa SPI CS | Chip Select |
| GP2 | LoRa SPI SCK | SPI Clock |
| GP3 | LoRa SPI TX | SPI MOSI |
| GP4 | LoRa RESET | Reset |
| GP15 | LoRa DIO0 | Interrupção do rádio |
| GP11 | LED Amarelo | Status: conectado |
| GP12 | LED Vermelho | Status: ignição iminente |
| GP13 | Botão Ignição | Comando de ignição (segurar 5 s) |
| GP19 | Buzzer | Alerta sonoro |
| GP14 | Chave geral | Liga/desliga de alimentação |

### Estação de Ignição - ESP32-C3 SuperMini
| GPIO | Conexão | Descrição |
|------|---------|-----------|
| GPIO0 | LoRa SPI RX | SPI MISO |
| GPIO1 | LoRa SPI CS | Chip Select |
| GPIO2 | LoRa SPI SCK | SPI Clock |
| GPIO3 | LoRa SPI TX | SPI MOSI |
| GPIO4 | LoRa RESET | Reset |
| GPIO5 | LoRa DIO0 | Interrupção do rádio |
| GPIO6 | LED Amarelo | Status: conectado com comando |
| GPIO7 | LED Vermelho | Status: ignição iminente |
| GPIO9 | Buzzer | Contagem regressiva |
| GPIO10 | Gate Ignitor | Comando Relé/ignitor |


## Sequência de Operação

### Estados dos LEDs
| Estado | LED Amarelo | LED Vermelho |
|--------|-------------|--------------|
| Desligado | OFF | OFF |
| Ligado (idle) | OFF | OFF |
| Conectado | ON | OFF |
| Ignição iminente | ON | PISCA |
| Ignição ativa | ON | ON |
| Erro | OFF | PISCA |

### Sequência de Ignição

1. **Operador pressiona botão de ignição na Estação de Comando**
   - Botão deve ser **mantido pressionado por 5 segundos**
   - LED vermelho começa a piscar
   - Buzzer emite tom contínuo

2. **Estação de Comando envia sinal LoRa para Estação de Ignição**
   - Envia `ARM_CONFIRMED` continuamente durante a fase de disparo
   - Requer confirmação `ACK` da Estação de Ignição

3. **Estação de Ignição recebe comando e inicia contagem**
   - LED vermelho pisca rapidamente
   - Buzzer emite **5 apitos** (1 por segundo) = contagem regressiva
   - Verifica continuamente se `ARM_CONFIRMED` segue ativo

4. **Durante a contagem (5 s):**
   - Se botão na Estação de Comando for **solto**: Comando envia `ABORT`
   - Se sinal `ARM_CONFIRMED` parar por > 500 ms: aborta por segurança
   - Ambas as estações voltam ao estado "Conectado"

5. **Ao final dos 5 segundos:**
   - LED vermelho fica **sólido** em ambas estações
   - Estação de Ignição aciona o ignitor (GP26 HIGH) por 2 s
   - Estação de Ignição envia `IGNITION_COMPLETE` para a base

6. **Após ignição:**
   - Estação de Comando aguarda 3 s e emite 2 bips de finalização
   - Sistema retorna ao estado "Conectado"

## Segurança

- Botão de ignição deve ser do tipo **momentâneo** (não trava)
- Ignição só ocorre se comando for mantido por toda a sequência (5 s)
- Comunicação LoRa bidirecional: Estação de Ignição confirma recebimento
- Timeout de comando: se Estação de Ignição não receber `ARM_CONFIRMED` por > 500 ms, aborta
- Sensor de continuidade (opcional): verifica se ignitor está conectado antes de armar

## Consumo de Energia

**Estimativas iniciais (a validar):**
- Operação normal (conectado): ~50 mA @ 3.3 V
- Transmissão LoRa: ~120 mA (picos)
- Autonomia estimada: 6-8 h com bateria 1000 mAh

### Carregamento com TP4056

- Cada estação usa um TP4056 dedicado (CHG1 e CHG2) para 2 células Li-ion/LiPo (3,7 V nominal).
- Conexão típica: `IN+ / IN-` (5 V da porta USB), `BAT+ / BAT-` (bateria), `OUT+ / OUT-` (alimentação da carga) quando a placa tiver proteção integrada.
- Corrente de carga recomendada para bateria de 1000 mAh: 0,5 A a 1,0 A (0,5C a 1C), respeitando especificação da bateria.
- Preferir módulos com proteção (DW01A + 8205A) para reduzir risco de sobrecarga, descarga profunda e curto.

## Galeria de Componentes

### Raspberry Pi Pico (Estação de Comando)
![Raspberry Pi Pico](images/pipico.png)

Microcontrolador dual-core ARM Cortex-M0+ (RP2040), 264KB SRAM, 2MB Flash.

### ESP32-C3 SuperMini (Estação de Ignição)
![ESP32-C3 SuperMini](images/esp32-c3-supermini.png)

Microcontrolador RISC-V 32 bits, 400KB SRAM, 4MB Flash. Wi-Fi + Bluetooth LE integrado, usado na Estação de Ignição.

### Módulo LoRa RA-02 / SX1278
![Módulo LoRa](images/lora.png)

Transceptor LoRa de longo alcance operando em **433 MHz**. Chip Semtech SX1278.

### Botão Liga/Desliga
![Botão Liga/Desliga](images/power-button.avif)

Botão de potência **12V 20A** para controle de energia das estações.

### Botão de Ignição
![Botão de Ignição](images/ignition-button.png)

Botão momentâneo (Momentary Reset), **22mm**, vermelho, **3-9V (5V)**. Usado exclusivamente na Estação de Comando para iniciar a sequência de ignição.

## Esquemáticos

### Estação de comando

<img src="./images/schematics/estacao-comando_bb.png" width="320" alt="Esquemático fritzing, caixa de comando"/>

### Estação de ignicão

<img src="./images/schematics/estacao-ignicao_bb.png" width="320" alt="Esquemático fritzing, caixa de ignição"/>

## Arquivos de Fabricação

- [Modelos 3D dos cases](./3d_models/) - *A criar*

## Notas Importantes

- **Sempre conectar antena LoRa antes de energizar** (dano ao módulo)
- Isolar circuito do ignitor via relé
- Testar sequência completa com carga dummy (lâmpada) antes de uso real
- Manter distância mínima de 10 m entre operador e foguete
