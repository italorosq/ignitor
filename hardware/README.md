# Hardware - Serra Rocketry Ignitor

O sistema tem duas estações independentes ligadas por LoRa 433 MHz:

- **Comando**: operada pelo operador em área segura (Raspberry Pi Pico).
- **Ignição**: fica próxima ao foguete e aciona o ignitor (ESP32 DevKit V1
  30 pinos, ou Pico na variante THT legada).

## Estado atual das placas

> A fonte de verdade é [`docs/ESTADO_DO_PROJETO.md`](../docs/ESTADO_DO_PROJETO.md).
> Os números abaixo foram medidos com `kicad-cli` em 2026-11-02.

| Variante | Pasta | Dimensão | Camadas | ERC | DRC | Desconexões | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Ignição SMD | [`kicad/placas/ignicao_smd/`](./kicad/placas/ignicao_smd/) | 75×75 mm | 2 | 0 | 27 erros + 100 avisos | 3 | **Candidata — NÃO FABRICAR** |
| Ignição PTH | [`kicad/placas/ignicao_pth/`](./kicad/placas/ignicao_pth/) | 75×80 mm | 2 | 0 | 100 avisos | 0 | Funcional, limpeza pendente |
| Ignição CNC | [`kicad/placas/ignicao_cnc/`](./kicad/placas/ignicao_cnc/) | 50×90 mm | 1 | 0 | 30 erros + 84 avisos | 57 | **Em projeto** |
| Comando | removida do repositório | — | — | — | — | — | Legado (gerbers históricos) |

A SMD tem **5 curtos reais** entre redes de potência/sinal. Ela foi promovida
como arquivo oficial de trabalho, mas não pode ir para a fábrica antes de
corrigir o layout. A CNC ainda é um rascunho: o plano de relayout para 90×100 mm
está em [`docs/planejamento/2026-10-relayout-cnc.md`](../docs/planejamento/2026-10-relayout-cnc.md).

## Lista de componentes (BOM)

| Item | Qtd | Aplicação | Observação |
| --- | --- | --- | --- |
| Raspberry Pi Pico | 1 | Estação de Comando | MCU RP2040 |
| ESP32 DevKit V1 30 pinos | 1 | Estação de Ignição (SMD/PTH) | ESP32-WROOM-32 |
| Módulo LoRa SX1278 433 MHz | 2 | Comando e Ignição | Um por estação |
| Antena LoRa 433 MHz | 2 | Comando e Ignição | Obrigatória antes de energizar |
| LED amarelo 5 mm | 2 | Status de link | Com resistor |
| LED vermelho 5 mm | 2 | Status de ignição | Com resistor |
| Buzzer ativo | 2 | Feedback sonoro | Um por estação |
| Botão de ignição momentâneo | 1 | Comando | Segurar por 5 s |
| Relé ou MOSFET | 1 | Ignição | Saída para ignitor |
| TP4056 com proteção | 2 | Carga de bateria | Um por estação |
| Bateria Li-ion/LiPo | 2 | Alimentação | Definir capacidade |
| Resistores 220 Ω | 4 | LEDs | Dois por estação |

## Pinagem

### Estação de Comando — Raspberry Pi Pico

| Pino | Função |
| --- | --- |
| GP0 | LoRa MISO |
| GP1 | LoRa CS (NSS) |
| GP2 | LoRa SCK |
| GP3 | LoRa MOSI |
| GP4 | LoRa RESET |
| GP15 | LoRa DIO0 |
| GP11 | LED amarelo |
| GP12 | LED vermelho |
| GP13 | Botão de ignição |
| GP19 | Buzzer |
| GP25 | LED onboard (link) |

### Estação de Ignição — ESP32 DevKit V1 (30 pinos)

Mapa oficial do firmware [`firmware/micropython/estacao_ignicao_esp.py`](../firmware/micropython/estacao_ignicao_esp.py):

| Função | GPIO | Observação |
| --- | --- | --- |
| LoRa SCK | 18 | VSPI |
| LoRa MISO | 19 | VSPI |
| LoRa MOSI | 23 | VSPI |
| LoRa CS (NSS) | 4 | pull-up externo |
| LoRa RESET | 16 | HIGH = operação normal |
| LoRa DIO0 | 17 | IRQ (polling no driver nativo) |
| STATUS_LED | 25 | link/status |
| LED_BTN | 26 | espelha STATUS 1:1 |
| LED_COUNT | 12 | contagem/ignição; strapping (MTDI) |
| BUTTON_IN | 27 | active-low, aborta a contagem |
| BUZZER | 14 | buzzer ativo |
| RELE | 32 | IN do módulo relé, ativo em baixo |
| GATE_1 (Q2) | 13 | GND da bobina do relé, ativo em ALTO |
| GATE_2 (Q1) | 33 | chave de saída do ignitor, ativo em ALTO |
| EXP_A / EXP_B / EXP_C | 2 / 5 / 15 | J12; strapping, cuidado no reset |
| ADC1_IN1 / ADC1_IN2 | 34 / 35 | somente entrada |
| I2C SDA / SCL | 21 / 22 | OLED SSD1306 (opcional) |

> GPIO2, GPIO5, GPIO12 e GPIO15 são pinos de strapping. Não os puxe para o
> nível errado durante o reset. O LED_COUNT usa GPIO12: mantenha LOW no boot
> com pull-down externo de 10 kΩ para GND.

### Estação de Ignição — Raspberry Pi Pico (THT legado)

| Pino | Função |
| --- | --- |
| GP0 | LoRa MISO |
| GP1 | LoRa CS (NSS) |
| GP2 | LoRa SCK |
| GP3 | LoRa MOSI |
| GP4 | LoRa RESET |
| GP6 / GP7 | SDA / SCL (OLED) |
| GP8 / GP9 | CONT_A / CONT_B |
| GP11 | LED amarelo |
| GP12 | LED vermelho |
| GP16 | LED do botão (J9) |
| GP19 | Buzzer |
| GP21 | LoRa DIO0 |
| GP26 | Relé/MOSFET (ignitor) |
| GP25 | LED onboard (link) |

## Ligação externa do laço de disparo

O contato de comutação do relé e a fonte do laço **não passam pela placa**.
Nela entram apenas os dois MOSFETs e dois terminais:

```text
fonte (+) --+-- COM do módulo de relé
            |
            +-- NO do módulo de relé -- J6 (NO_RELE) -- Q1 (D -> S) -- J9 (SKIB) -- ignitor
                                                                                      |
                                                          fonte (-) -----------------+
```

Q2 (`GATE_1` → R6) chaveia o **retorno de GND dos 5 V da bobina** do módulo de
relé; Q1 (`GATE_2` → R4) fica **em série com a perna do SKIB e com o contato NO**.
São duas chaves em série no mesmo laço.

| Estado | GATE_1 (Q2) | GATE_2 (Q1) | RELE_IN | Efeito |
| --- | --- | --- | --- | --- |
| Repouso / boot | 0 | 0 | 1 | nenhum caminho fechado |
| ARM_CONFIRMED / contagem | 1 | 0 | 1 | relé energizável, contato NO aberto |
| Fim da contagem | 1 | 0 → 1 | 0 | contato NO fecha; Q1 assume a corrente |
| Janela de ignição (2 s) | 1 | 1 | 0 | duas chaves em série fechadas |
| Fim da janela | 1 → 0 | 1 → 0 | 1 | Q1 abre primeiro; depois o relé |

> A fiação externa foi confirmada pelo responsável do projeto em 2026-10-15.
> Ela não é derivável dos arquivos do repositório: o esquema termina em J6 e J9.

## Sequência de operação

1. Comando envia `ARM_CONFIRMED` enquanto o botão é mantido.
2. Ignição confirma com `ACK` e inicia contagem de 5 s.
3. Se houver `ABORT` ou perda de sinal > 500 ms, o ciclo é cancelado.
4. Ao final da contagem, a saída de ignição ativa por 2 s.
5. Ignição envia `IGNITION_COMPLETE`.

## Segurança

- Sempre conectar antena LoRa antes de energizar.
- Usar botão momentâneo (sem trava).
- Testar com carga dummy antes de ignitor real.
- Manter distância mínima de 10 m em testes operacionais.
- Não fabricar a SMD enquanto o DRC tiver curtos/desconexões.
- Não alterar a lógica de intertravamento sem revisar os testes de bancada.

## Pastas de hardware

- [`kicad/`](./kicad/): projetos KiCad ativos, biblioteca compartilhada e SPICE.
- [`tools/`](./tools): scripts de automação KiCad.
- [`gerbers/`](./gerbers): pacotes históricos; os atuais ficam em `kicad/placas/*/jlcpcb/`.
- [`3d_models/`](./3d_models): cases e modelos 3D (OpenSCAD é o modelo atual).
- [`fritzing/`](./fritzing): diagramas de protoboard.
- [`images/`](./images): fotos e esquemas de montagem.
