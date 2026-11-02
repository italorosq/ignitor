# Serra Rocketry Ignitor

[![CI](https://github.com/italorosq/ignitor/actions/workflows/ci.yml/badge.svg)](https://github.com/italorosq/ignitor/actions/workflows/ci.yml)

Sistema de ignição remota para foguetes experimentais. Duas estações
independentes se comunicam por LoRa 433 MHz:

| Estação | Função | MCU |
| --- | --- | --- |
| Comando | Operação remota e segurança | Raspberry Pi Pico |
| Ignição | Acionamento do ignitor | ESP32 DevKit V1 (ESP32-WROOM-32) ou Pico (legado) |

## Estado atual

> **Leia [`docs/ESTADO_DO_PROJETO.md`](./docs/ESTADO_DO_PROJETO.md) antes de
> fabricar qualquer placa.**

| Placa | Dimensão | Estado |
| --- | --- | --- |
| Ignição SMD | 75×75 mm | **Candidata — não fabricar** (5 curtos, 3 desconexões, 27 erros de DRC) |
| Ignição PTH | 75×80 mm | Funcional; limpeza de serigrafia/paridade pendente |
| Ignição CNC | 50×90 mm | Em projeto (0 trilhas; relayout 90×100 não executado) |
| Comando | — | Projeto removido; gerbers históricos em `hardware/gerbers/legado/` |

O firmware principal da ignição (ESP32) está implementado com botão, OLED,
ADC, expansão e sequência de ignição. Os testes estáticos passam
(`pytest test/`).

## Sequência de ignição

1. Operador segura o botão por 5 s.
2. Comando transmite `ARM_CONFIRMED` continuamente.
3. Ignição executa contagem regressiva (5 bipes).
4. Relé + Q1 acionam por 2 s.
5. Ignição envia `IGNITION_COMPLETE`.

## Comece aqui

| Passo | Guia |
| --- | --- |
| 1. Entender | [docs/ARQUITETURA.md](./docs/ARQUITETURA.md) |
| 2. Montar | [docs/INSTALL.md](./docs/INSTALL.md) |
| 3. Gravar firmware | [docs/README_ENVIO.md](./docs/README_ENVIO.md) |
| 4. Testar | [test/README.md](./test/README.md) |
| 5. Diagnosticar | [docs/troubleshooting.md](./docs/troubleshooting.md) |
| 6. Contribuir | [CONTRIBUTING.md](./CONTRIBUTING.md) |

## Estrutura do repositório

```text
ignitor/
├── docs/                 # arquitetura, estado, instalação, protocolo, histórico
├── firmware/
│   └── micropython/      # firmware oficial das estações
├── hardware/
│   ├── kicad/
│   │   ├── placas/       # ignicao_smd, ignicao_pth, ignicao_cnc
│   │   ├── shared/lib/   # símbolos, footprints e modelos 3D
│   │   └── spice/        # simulações LTspice
│   ├── tools/kicad/      # automação de posicionamento, roteamento e fabricação
│   ├── gerbers/legado/   # pacotes históricos de fabricação
│   ├── 3d_models/        # cases (OpenSCAD é o modelo atual)
│   ├── fritzing/         # diagramas de protoboard
│   └── images/           # fotos e esquemas
├── software/web/         # UI web legada
├── test/                 # testes estáticos e scripts de bancada
└── scripts/              # checagens de links e higiene do repositório
```

## Componentes principais

| Qtd | Componente | Uso |
| --- | --- | --- |
| 1 | Raspberry Pi Pico | Estação de Comando |
| 1 | ESP32 DevKit V1 (30 pinos) | Estação de Ignição (principal) |
| 2 | Módulo LoRa SX1278 433 MHz | Comunicação |
| 2 | LED amarelo 5 mm | Status de link |
| 2 | LED vermelho 5 mm | Status de ignição |
| 2 | Buzzer ativo | Feedback sonoro |
| 1 | Botão de ignição 22 mm | Acionamento |
| 1 | Relé + MOSFETs Q1/Q2 | Saída para ignitor |
| 2 | TP4056 | Carga de bateria |

BOM completa e pinagem: [hardware/README.md](./hardware/README.md).

## Segurança

- Botão de ignição deve ser momentâneo (sem trava).
- O comando precisa ser mantido pelos 5 s completos.
- Perda de sinal por mais de 500 ms deve abortar.
- Sempre usar carga dummy antes de ignitor real.
- Sempre conectar antena LoRa antes de energizar.
- Manter distância mínima de 10 m entre operador e foguete.
- Não fabricar a SMD enquanto o DRC tiver curtos ou desconexões.

## Projeto

Projeto da [Serra Rocketry](https://github.com/Serra-Rocketry).
