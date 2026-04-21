# README - Envio de Codigo para RP (Raspberry Pi Pico) e ESP32-C3

Este guia mostra como enviar os codigos MicroPython para as placas do projeto.

## Arquivos que vao para cada Pico

### Pico da Estacao de Comando

- `software/config_lora.py`
- `software/sx127x.py`
- `software/estacao_comando.py` (deve ser salvo como `main.py` no Pico)

### Pico da Estacao de Ignicao

- `software/config_lora.py`
- `software/sx127x.py`
- `software/estacao_ignicao.py` (deve ser salvo como `main.py` no Pico)

### ESP32-C3 da Estacao de Ignicao (alternativa)

- `software/sx127x.py` (opcional; o script tem fallback nativo)
- `software/estacao_ignicao_esp.py` (deve ser salvo como `main.py` no ESP32-C3)

## Pre-requisitos

- Linux com Python 3
- Dependencias instaladas:

```bash
pip install -r requirements.txt
```

- MicroPython instalado no Pico
- Cabo USB de dados

## 1. Descobrir a porta serial no Linux

Com o Pico conectado:

```bash
ls /dev/ttyACM* /dev/ttyUSB*
```

Exemplo comum:

- Comando: `/dev/ttyACM0`
- Ignicao: `/dev/ttyACM1`

## 2. Envio via terminal (ampy)

A partir da raiz do repositorio:

### 2.1 Pico da Estacao de Comando

```bash
ampy --port /dev/ttyACM0 put software/config_lora.py
ampy --port /dev/ttyACM0 put software/sx127x.py
ampy --port /dev/ttyACM0 put software/estacao_comando.py main.py
ampy --port /dev/ttyACM0 ls
```

### 2.2 Estacao de Ignicao em Raspberry Pi Pico

```bash
ampy --port /dev/ttyACM1 put software/config_lora.py
ampy --port /dev/ttyACM1 put software/sx127x.py
ampy --port /dev/ttyACM1 put software/estacao_ignicao.py main.py
ampy --port /dev/ttyACM1 ls
```

### 2.3 Estacao de Ignicao em ESP32-C3 SuperMini

```bash
ampy --port /dev/ttyUSB0 put software/sx127x.py
ampy --port /dev/ttyUSB0 put software/estacao_ignicao_esp.py main.py
ampy --port /dev/ttyUSB0 ls
```

## 3. Envio via Thonny (alternativa)

1. Abrir o Thonny.
2. Selecionar interpretador MicroPython (Raspberry Pi Pico).
3. Abrir os arquivos em `software/`.
4. Salvar no dispositivo:
   - `config_lora.py`
   - `sx127x.py`
   - `estacao_comando.py` como `main.py` no Pico de comando
   - `estacao_ignicao.py` (Pico) ou `estacao_ignicao_esp.py` (ESP32-C3) como `main.py` na ignicao

## 4. Ver logs seriais

Para acompanhar o boot e os logs:

```bash
screen /dev/ttyACM0 115200
```

Troque a porta para a estacao de ignicao quando necessario.

## 5. Antena e enlace LoRa

Antes de ligar qualquer placa ou gravar firmware para teste, confira se as duas antenas LoRa estão rosqueadas/conectadas nos módulos SX1278. O rádio pode inicializar mesmo sem antena, mas o enlace PING/PONG não vai fechar corretamente.

## 6. Erros comuns

### Permissao negada na porta serial

Se aparecer erro de permissao:

```bash
sudo usermod -aG dialout $USER
```

Depois, saia e entre novamente na sessao.

### Pico nao aparece em `/dev/ttyACM*`

- Trocar o cabo USB (muitos cabos so carregam).
- Testar outra porta USB.
- Regravar o firmware MicroPython no Pico.

## Creditos da biblioteca LoRa

Este projeto usa/adapta a biblioteca `SX127x` para MicroPython:

- Projeto: [SX127x driver for (Micro)Python on ESP8266/ESP32/Raspberry_Pi](https://github.com/Wei1234c/SX127x_driver_for_MicroPython_on_ESP8266)
- Autor principal: Wei Lin (`Wei1234c`)
- Licenca original: GPL-3.0

Arquivos relacionados no projeto:

- `software/sx127x.py`
- `software/config_lora.py`
