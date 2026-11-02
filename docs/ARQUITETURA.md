# Arquitetura do sistema

## Visão geral

```text
┌──────────────────────┐         LoRa 433 MHz         ┌──────────────────────┐
│  Estação de Comando  │  PING / PONG / ARM_CONFIRMED  │  Estação de Ignição  │
│  Raspberry Pi Pico   │ ◄───────────────────────────► │  ESP32 DevKit V1     │
│  botão + LEDs + buzzer│        ACK / ABORT /         │  relé + Q1/Q2 +      │
│                      │      IGNITION_COMPLETE        │  buzzer + OLED       │
└──────────────────────┘                               └──────────┬───────────┘
                                                                  │
                                                          laço de disparo
                                                          (fonte externa +
                                                           relé + Q1 + ignitor)
```

As duas estações são independentes. A de comando fica na área segura; a de
ignição fica próxima ao foguete. A comunicação é feita por dois módulos
SX1278 em 433 MHz.

## Componentes lógicos

| Componente | Responsabilidade |
| --- | --- |
| Comando Pico | Lê o botão, mantém `ARM_CONFIRMED`, mostra link/status, envia `ABORT` |
| Ignição ESP32 | Recebe o comando, faz a contagem de 5 s, aciona o relé e a chave Q1 |
| Ignição Pico (THT) | Mesma lógica, variante legada |
| Relé + Q1/Q2 | Duas chaves em série no laço de disparo |
| OLED | Status local da ignição (opcional) |
| Testes de bancada | Validam periféricos e a ordem de arme/desarme |

## Protocolo

| Parâmetro | Valor |
| --- | --- |
| Frequência | 433 MHz |
| Largura de banda | 125 kHz |
| Spreading Factor | 7 |
| Coding Rate | 4/5 |
| Potência TX | 17 dBm |
| Retransmissão `ARM_CONFIRMED` | 200 ms |
| Timeout de comando na ignição | 500 ms |
| Timeout de link no comando | 3000 ms |

Mensagens: `PING`, `PONG`, `ARM_CONFIRMED`, `ACK`, `ABORT`,
`IGNITION_COMPLETE`. Detalhes em [`README_API.md`](./README_API.md).

## Máquina de estados

```text
IDLE
  │ PING/PONG
  ▼
CONNECTED ──(solta o botão)──► ABORT
  │ ARM_CONFIRMED (botão mantido)
  ▼
COUNTDOWN (5 s)
  │ perda de ARM_CONFIRMED > 500 ms ──► ABORT
  │ fim da contagem
  ▼
IGNITION (2 s)
  │
  ▼
IGNITION_COMPLETE ──► IDLE (após ~3 s)
```

## Cadeia de segurança

O laço de disparo tem **duas chaves em série**:

1. **Q2 (`GATE_1`)** chaveia o retorno de GND da bobina do módulo relé.
2. **Q1 (`GATE_2`)** fica em série com o contato NO do relé e o terminal SKIB.

Ordem de arme:

```text
boot:      GATE_1=0, GATE_2=0, RELE_IN=1   (tudo aberto)
contagem:  GATE_1=1, GATE_2=0, RELE_IN=1   (relé energizável, contato aberto)
fim:       GATE_1=1, GATE_2=1, RELE_IN=0   (contato fecha, Q1 assume)
desarme:   GATE_2=0 → RELE_IN=1 → GATE_1=0 (Q1 abre primeiro)
```

Os gates têm pull-down de 10 kΩ e nascem em 0 no boot. O firmware só arma
depois de 5 s contínuos de `ARM_CONFIRMED`; qualquer `ABORT` ou perda de sinal
por mais de 500 ms cancela o ciclo.

## Alimentação

```text
Bateria Li-ion/LiPo
  └── TP4056 (proteção/carga)
        └── buck 5 V (J1)
              ├── módulo relé (J7)
              ├── buzzer (J10)
              └── ESP32 DevKit V1 (VIN/5V)
                    └── regulador 3V3 onboard
                          ├── RA-02 (LoRa)
                          ├── OLED (J11)
                          └── LEDs / lógica
```

O contato de comutação do relé e a fonte do laço de disparo **não passam pela
placa**. A placa fornece apenas o acionamento do relé e a chave Q1 em série com
o terminal do ignitor. A ligação externa está em
[`hardware/README.md`](../hardware/README.md#ligação-externa-do-laço-de-disparo).

## Estrutura do repositório

| Pasta | Conteúdo |
| --- | --- |
| `firmware/micropython/` | Firmware oficial das estações |
| `hardware/kicad/placas/` | Projetos KiCad ativos |
| `hardware/kicad/shared/lib/` | Biblioteca compartilhada (símbolos, footprints, 3D) |
| `hardware/kicad/spice/` | Simulações LTspice por módulo |
| `hardware/tools/kicad/` | Automação de posicionamento, roteamento e fabricação |
| `hardware/gerbers/legado/` | Pacotes de fabricação históricos |
| `test/` | Testes estáticos e scripts de bancada |
| `software/web/` | UI web legada |
| `docs/` | Documentação, estado, histórico e planejamento |

## Falhas e abortos

| Condição | Ação |
| --- | --- |
| Botão solto antes de 5 s | `ABORT` imediato; ignitor não aciona |
| Perda de `ARM_CONFIRMED` > 500 ms | `ABORT`; contagem reinicia do zero |
| Perda de link > 3 s no comando | Comando volta para `IDLE` e sinaliza erro |
| Falha de inicialização do rádio | Firmware tenta novamente; não arma |
| Ausência de OLED | Firmware segue sem display |
| Watchdog/reset da ignição | Gates voltam a 0; relé inativo |

## Documentos relacionados

- [Estado do projeto](./ESTADO_DO_PROJETO.md)
- [Protocolo](./README_API.md)
- [Instalação](./INSTALL.md)
- [Testes](../test/README.md)
- [Hardware](../hardware/README.md)
