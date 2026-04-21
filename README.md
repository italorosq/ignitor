# Serra Rocketry Ignitor

Sistema de ignição remota para foguetes experimentais.

## O que é

Duas estações independentes que se comunicam via LoRa 433 MHz:

| Estação | Função | MCU |
|---------|-------|-----|
| **Comando** | Operador segura do foguete | Raspberry Pi Pico |
| **Ignição** | Aciona o ignitor | ESP32-C3 SuperMini |

## Sequência de Ignição

```
1. Operador segura botão por 5 s
2. Comando transmite ARM_CONFIRMED
3. Ignição faz contagem regressiva (5 bipes)
4. Relé aciona por 2 s
5. Ignição envia IGNITION_COMPLETE
```

## Comece Aqui

| Passo | Guía |
|-------|------|
| 1. Montar | [docs/INSTALL.md](./docs/INSTALL.md) |
| 2. Gravar firmware | [docs/INSTALL.md#4-gravando-firmware](./docs/INSTALL.md#4-gravando-firmware) |
| 3. Testar | [test/README.md](./test/README.md) |
| 4. Problemas? | [docs/troubleshooting.md](./docs/troubleshooting.md) |

## Arquitetura

### Estação de Comando
- Botão de ignição (segurar 5 s)
- LEDs: amarelo (conectado), vermelho (ignição iminente)
- Buzzer de feedback
- LoRa 433 MHz

### Estação de Ignição
- LEDs de status
- Buzzer de contagem regressiva
- Relé para ignitor
- LoRa 433 MHz

### Componentes Principais

| Qtd | Componente | Uso |
|-----|-----------|-----|
| 1 | Raspberry Pi Pico | Estação de Comando |
| 1 | ESP32-C3 SuperMini | Estação de Ignição |
| 2 | Módulo LoRa SX1278 | Comunicação 433 MHz |
| 2 | LED amarelo 5mm | Status conectado |
| 2 | LED vermelho 5mm | Status ignição |
| 2 | Buzzer ativo 5V | Feedback sonoro |
| 1 | Botão ignição 22mm | Acionamento |
| 1 | Relé | Acionar ignitor |
| 2 | Módulo TP4056 | Carregador bateria |

Pinagem completa e BOM: [hardware/README.md](./hardware/README.md)

## Arquivo do Repositório

```
ignitor/
├── docs/          # Guias de documentação
├── hardware/      # Pinagem, BOM, esquemáticos
├── software/     # Firmware MicroPython
└── test/        # Procedimentos de teste
```

## Segurança

- Botão de ignição deve ser **momentâneo** (sem trava)
- Manter comando por toda a janela de 5 s
- Em perda de sinal > 500 ms, ignição aborta
- Sempre testar com **carga dummy** antes de ignitor real
- Manter distância ≥ 10 m entre operador e foguete

## Status do Projeto

- [x] Arquitetura definida
- [x] Hardware documentado
- [ ] Firmware validado
- [ ] Testes de campo concluídos
- [ ] Cases 3D finalizados

## Equipe

Projeto da [Serra Rocketry](https://github.com/Serra-Rocketry).