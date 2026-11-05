# Biblioteca compartilhada do projeto Ignitor

Biblioteca unica com **todos os componentes das placas** (simbolos, footprints e
modelos 3D) usados pelos tres projetos KiCad deste repositorio:

| Projeto | Caminho |
| --- | --- |
| Ignicao THT | `hardware/kicad/placas/ignicao_pth/` |
| Ignicao SMD | `hardware/kicad/placas/ignicao_smd/` |
| Ignicao CNC | `hardware/kicad/placas/ignicao_cnc/` |

Os projetos registram esta pasta por inteiro nas tabelas locais
`sym-lib-table` e `fp-lib-table` (dentro de cada projeto), sempre com caminho
relativo ao projeto:

```text
sym-lib-table -> ${KIPRJMOD}/../../shared/lib/<lib>.kicad_sym
fp-lib-table  -> ${KIPRJMOD}/../../shared/lib/<lib>.pretty
modelos 3D    -> ${KIPRJMOD}/../../shared/lib/3dmodels/<arquivo>
```

Assim nada depende das bibliotecas globais do KiCad, de pastas pessoais fora
do repositorio nem de variaveis de ambiente da maquina. As copias sao
**recortadas**: contem apenas os componentes que as placas usam, com o mesmo
nome de biblioteca original (por isso nenhum esquema ou PCB precisou ser
editado alem dos caminhos de modelo 3D).

> Antes existia uma pasta `lib/` duplicada dentro de cada projeto, o que
> causava os erros de ERC `lib_symbol_mismatch` e "biblioteca de simbolos nao
> encontrada". Ela foi removida.

## Simbolos (16 bibliotecas)

| Biblioteca | Origem | Simbolos usados |
| --- | --- | --- |
| `ignitor` | proprio | `Ra-02`, `ESP32_NodeMCU-32S`, `ESP32_DevKit-30` |
| `Connector` | KiCad oficial | `Screw_Terminal_01x02` |
| `Device` | KiCad oficial | `C`, `D_Schottky`, `D_TVS`, `Fuse` |
| `Diode` | KiCad oficial | `1N5400` (+ base `1N4001`) |
| `power` | KiCad oficial | `+3V3`, `GND`, `PWR_FLAG`, `VCC` |
| `Switch` | KiCad oficial | `SW_SP3T` |
| `easyeda2kicad` | conversao do usuario | `0805W8F2200T5E`, `1206W4F1002T5E`, `CL31A106KBHNNNE`, `CL31A107MQHNNNE`, `CL31B104KBCNNNC`, `SS34_C8678` |
| `PCM_SL_Capacitors` | KiCad-Simple-Libraries | `1000uF_16V`, `100uF_16V`, `10uF_16V` |
| `PCM_SL_Connectors` | KiCad-Simple-Libraries | `JST_02`, `JST_03`, `JST_04` |
| `PCM_SL_Development_Board` | KiCad-Simple-Libraries | `ESP32_DevKit_V1_DOIT_30GPIOs` |
| `PCM_SL_Devices` | KiCad-Simple-Libraries | `LED` |
| `PCM_SL_Pin_Headers` | KiCad-Simple-Libraries | `PINHD_1x1_Male`, `PINHD_1x2_Female`, `PINHD_1x2_Male`, `PINHD_1x3_Male` |
| `PCM_SL_Resistors` | KiCad-Simple-Libraries | `10k`, `220ohm` |
| `PCM_SL_Screw_Terminal` | KiCad-Simple-Libraries | `Screw_Terminal_2_P3.50mm` |
| `PCM_SparkFun-PowerSymbol` | SparkFun | `VIN` |
| `PCM_Transistor_MOSFET_AKL` | alternate-kicad-library | `IRLZ44N` (+ base `Q_NMOS-E_Generic_GDS`) |

## Footprints (12 bibliotecas)

| Biblioteca | Origem | Footprints usados |
| --- | --- | --- |
| `ignitor` | proprio | `RA-02`, `RA-02_THT`, `ESP32_NodeMCU-32S`, `ESP32_DevKit-30` |
| `Capacitor_THT` | KiCad oficial | `CP_Radial_D5.0mm_P2.00mm`, `CP_Radial_D10.0mm_P5.00mm` |
| `Connector_JST` | KiCad oficial | `JST_EH_B2B/B3B/B4B-EH-A` |
| `Connector_PinHeader_2.54mm` | KiCad oficial | `PinHeader_1x01/1x02/1x03_P2.54mm_Vertical` |
| `Connector_PinSocket_2.54mm` | KiCad oficial | `PinSocket_1x02_P2.54mm_Vertical` |
| `Diode_THT` | KiCad oficial | `D_DO-201AD_P15.24mm_Horizontal` |
| `LED_THT` | KiCad oficial | `LED_D5.0mm` |
| `Resistor_THT` | KiCad oficial | `R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal` |
| `TerminalBlock_Phoenix` | KiCad oficial | `TerminalBlock_Phoenix_PT-1,5-2-3.5-H_1x02_P3.50mm_Horizontal` |
| `easyeda2kicad` | conversao do usuario | `C1206`, `R0805`, `R1206`, `SMA_L4.3-W2.6-LS5.2-RD` |
| `PCM_Package_TO_SOT_THT_AKL` | alternate-kicad-library | `TO-220-3_Vertical_GDS` |
| `PCM_SL_Development_Boards` | KiCad-Simple-Libraries | `DOIT_ESP32_DEVKIT_30Pins` |

## Modelos 3D (`3dmodels/`)

Todos os caminhos `(model ...)` dos footprints e das tres PCBs apontam para
esta pasta. Sao 23 arquivos (~10 MB):

- **KiCad oficial (15 `.step`)**: JST EH ×3, PinHeader 1x01/1x02/1x03,
  PinSocket 1x02, CP_Radial D5/D10, D_DO-201AD, LED_D5.0mm, R_Axial DIN0207,
  TerminalBlock Phoenix, TO-220-3_Vertical, TO-92_Inline.
- **easyeda2kicad (5 `.step` + 1 `.wrl`)**: C1206, R0805, R1206, SMA, TO-92-3
  (o `.wrl` do R0805 continua referenciado por um footprint da PCB SMD).
- **DOIT ESP32 DevKit (1 `.wrl`)**.
- **RA-02 (1 `.STEP`)**: usado pelo footprint de adaptador `RA-02_THT` e tambem
  pelos footprints `RA-02` da `ignitor.pretty`.

> O modelo 3D do RA-02 foi incorporado a `ignitor.pretty` (antes existia apenas
> embutido no PCB SMD, com caminho absoluto de outra pasta do usuario).

## Regeneracao

A biblioteca inteira e reproduzivel pelo script:

```powershell
& "C:\Program Files\KiCad\10.0\bin\python.exe" -u `
    hardware/tools/kicad/biblioteca/extrair_biblioteca.py
```

Ele le as bibliotecas de origem na maquina (KiCad oficial, `easyeda2kicad`,
3rd-party), regera os recortes, copia os modelos 3D, reescreve as tabelas dos
dois projetos e corrige os caminhos de modelo nas PCBs. Para so conferir que
tudo resolve localmente:

```powershell
& "C:\Program Files\KiCad\10.0\bin\python.exe" -u `
    hardware/tools/kicad/biblioteca/extrair_biblioteca.py --check
```

## Simbolos proprios da biblioteca `ignitor`

| Simbolo | Uso |
| --- | --- |
| `Ra-02` | Modulo LoRa Ai-Thinker RA-02 (SX1278, 433 MHz, soquete IPEX) |
| `ESP32_NodeMCU-32S` | Modulo ESP32-WROOM-32 em placa de desenvolvimento, DIP-38 |
| `ESP32_DevKit-30` | Placa de desenvolvimento ESP32 de 30 pinos, socket 2x15 (clone DOIT DEVKIT V1) |

> Os dois simbolos ESP32 sao legado das versoes anteriores das placas (hoje os
> projetos usam `PCM_SL_Development_Board:ESP32_DevKit_V1_DOIT_30GPIOs`).

## Footprints proprios da biblioteca `ignitor`

### `RA-02`

Modulo RA-02 soldado direto na placa. Pads SMD castellated de 2,0 mm de passo,
3,0 x 1,4 mm, estendidos 1,5 mm alem da borda do modulo para facilitar a solda
manual. Modulo real: 17 x 16 mm.

Numeracao dos pads segue o pinout fisico do modulo:

- Coluna esquerda (topo -> base) = pads 1-8: `GND, GND, 3V3, RESET, DIO0, DIO1, DIO2, DIO3`
- Coluna direita (topo -> base) = pads 16-9: `GND, NSS, MOSI, MISO, SCK, DIO5, DIO4, GND`

### `RA-02_THT`

Adaptador plugavel (carrier) para o RA-02, 2 fileiras de 8 pinos, passo 2,54 mm,
fileiras a 25,4 mm, placa de 33 x 24 mm. Corresponde ao projeto
[kevinta893/LoRa-Breakout-Board](https://github.com/kevinta893/LoRa-Breakout-Board).

- Fileira esquerda (topo -> base) = pads 9,10,11,12,13,14,15,16
- Fileira direita (topo -> base) = pads 8,7,6,5,4,3,2,1

> O part de Fritzing original rotula o slot do pino 1 como `ANT` (off-by-one na
> serigrafia). O test point de antena **nao** e levado ao adaptador.

### `ESP32_NodeMCU-32S`

Modulo ESP32-WROOM-32 em placa, soquetado com 2 conectores femea 1x19 (furo 1,0 mm).

Especificacao Ai-Thinker confirmada no datasheet: **25,4 x 48,3 mm (±0,2),
DIP-38, passo 2,54 mm, fileiras a 22,86 mm (0,9")**.

> Cuidado: existem clones de 38 pinos com fileiras a **22,86 mm** (NodeMCU-32S,
> a variante adotada aqui) e a placa oficial ESP32-DevKitC V4, que usa
> **25,4 mm (1,0")**. Sao fisicamente incompativeis entre si. Se trocar de
> modulo, o footprint precisa ser refeito.

Numeracao DIP-38 (pin 1 no topo da fileira esquerda, sentido anti-horario):

| Pino | Sinal | Pino | Sinal | Pino | Sinal | Pino | Sinal |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 3V3 | 11 | GPIO27 | 21 | GPIO7 (flash) | 31 | GPIO19 |
| 2 | EN | 12 | GPIO14 | 22 | GPIO8 (flash) | 32 | GND |
| 3 | GPIO36 | 13 | GPIO12 | 23 | GPIO15 | 33 | GPIO21 |
| 4 | GPIO39 | 14 | GND | 24 | GPIO2 | 34 | GPIO3 (RX0) |
| 5 | GPIO34 | 15 | GPIO13 | 25 | GPIO0 | 35 | GPIO1 (TX0) |
| 6 | GPIO35 | 16 | GPIO9 (flash) | 26 | GPIO4 | 36 | GPIO22 |
| 7 | GPIO32 | 17 | GPIO10 (flash) | 27 | GPIO16 | 37 | GPIO23 |
| 8 | GPIO33 | 18 | GPIO11 (flash) | 28 | GPIO17 | 38 | GND |
| 9 | GPIO25 | 19 | 5V | 29 | GPIO5 | | |
| 10 | GPIO26 | 20 | GPIO6 (flash) | 30 | GPIO18 | | |

**Uso dos pinos — restricoes**

- `GPIO6` a `GPIO11` (pinos 16-18 e 20-22): ligados a flash SPI, **nao usar**.
  Estao marcados como `no_connect` no simbolo.
- `GPIO34`, `GPIO35`, `GPIO36`, `GPIO39`: **somente entrada**, sem pull-up
  interno. Otimos para ADC, ruins para saida.
- Pinos de strapping `GPIO0`, `GPIO2`, `GPIO12`, `GPIO15`: funcionam como I/O
  normal depois do boot, mas **nao podem ser puxados para o nivel errado durante
  o reset** ou o modulo entra em modo de download. Na placa de ignicao eles
  ficam no header de expansao J12 — a serigrafia avisa.
- `GPIO1` / `GPIO3` (pinos 34/35) sao tambem UART0 (TX/RX) — usar como I/O
  normal so se a serial de debug nao estiver em uso.

**Orientacao mecanica** (importante para RF e para acessar o USB):

- `+Y` = lado da **antena** do WROOM-32 -> manter **sem cobre** embaixo.
- `-Y` = lado do **micro-USB** -> precisa ficar acessivel, virado para a borda.

O footprint ja traz a marcacao `ANT` / `USB`, a seta de pino 1 e um courtyard que
inclui os 2,6 mm do conector USB.

### `ESP32_DevKit-30`

Socket **2x15 femea**, passo 2,54 mm, fileiras a **25,4 mm (1,0")**, para o
ESP32 DevKit de 30 pinos (clone DOIT DEVKIT V1). Pads THT 1,8 mm, furo 1,0 mm.

> **Atencao - convencao de numeracao.** Esta placa e serigrafada **apenas por
> nome de sinal** (`3V3`, `EN`, `D34`, `D22`, ...) e **nao tem marcador de pino
> 1**. Nao existe padrao de fabricante que faca a numeracao ser univoca. A
> numeracao adotada aqui e a convencao KiCad para header 2xN:
>
> - fileira 1 = pads **1-15**
> - fileira 2 = pads **16-30**
> - as duas fileiras correm **no mesmo sentido** (row-major), de modo que o
>   pad 16 fica exatamente alinhado com o pad 1
>
> Com isso `3V3` e `VIN` ficam no mesmo extremo fisico, o da USB. A sequencia de
> sinais foi confirmada por duas fontes independentes, mas **a numeracao e uma
> decisao de projeto, nao um dado do fabricante**.

Numeracao adotada:

| Pino | Sinal | Pino | Sinal | Pino | Sinal |
| --- | --- | --- | --- | --- | --- |
| 1 | 3V3 | 11 | GPIO27 | 21 | GPIO16 (RX2) |
| 2 | EN | 12 | GPIO14 | 22 | GPIO17 (TX2) |
| 3 | GPIO36 (VP) | 13 | GPIO12 | 23 | GPIO5 |
| 4 | GPIO39 (VN) | 14 | GPIO13 | 24 | GPIO18 |
| 5 | GPIO34 | 15 | GND | 25 | GPIO19 |
| 6 | GPIO35 | 16 | VIN | 26 | GPIO21 |
| 7 | GPIO32 | 17 | GND | 27 | GPIO3 (RX0) |
| 8 | GPIO33 | 18 | GPIO15 | 28 | GPIO1 (TX0) |
| 9 | GPIO25 | 19 | GPIO2 | 29 | GPIO22 |
| 10 | GPIO26 | 20 | GPIO4 | 30 | GPIO23 |

Equivalente em serigrafia, na ordem em que os pinos aparecem ao longo da borda:

| Fileira | Sequencia |
| --- | --- |
| 1 (pads 1-15) | `3V3, EN, VP, VN, D34, D35, D32, D33, D25, D26, D27, D14, D12, D13, GND` |
| 2 (pads 16-30) | `VIN, GND, D15, D2, D4, RX2, TX2, D5, D18, D19, D21, RX0, TX0, D22, D23` |

**Uso dos pinos - restricoes**

- So existem **2 pinos GND** (15 e 17), um em cada fileira. Sao suficientes, mas
  o retorno do GND do DevKit nao pode depender de um unico caminho.
- `GPIO34`, `GPIO35`, `GPIO36` (VP), `GPIO39` (VN): **somente entrada**, sem
  pull-up interno. Otimos para ADC, ruins para saida. No simbolo sao `input`.
- Pinos de strapping expostos: `GPIO2`, `GPIO5`, `GPIO12`, `GPIO15`. Funcionam
  como I/O normal apos o boot, mas **nao podem ser puxados para o nivel errado
  durante o reset** ou o modulo entra em modo de download. `GPIO0` **nao** e
  exposto nesta placa.
- `GPIO1` / `GPIO3` (pads 28 / 27) sao tambem UART0 (TX/RX) - usar como I/O
  normal so se a serial de debug nao estiver em uso.
- `GPIO6` a `GPIO11` (flash) **nao sao expostos** nesta placa de 30 pinos, ao
  contrario do DIP-38.
- O pino 1 do simbolo e `power_out` porque e a saida do regulador onboard; o 16
  (`VIN`) e `power_in`.

**Orientacao mecanica**

- `+Y` = lado da **USB** (pads 1 e 16) -> precisa ficar acessivel, virado para a
  borda.
- `-Y` = lado da **antena** do WROOM-32 -> manter **sem cobre** embaixo.

O footprint traz `USB` e `ANT` na serigrafia, marcador de pino 1 (canto superior
esquerdo) e o nome do sinal de cada pad na camada `F.Fab`.

> **Verificacao obrigatoria antes de pedir o PCB:** como a placa nao tem
> marcador de pino 1, confira se o `3V3` do seu modulo alinha com o pad 1 e se o
> lado da USB fica em `+Y`. Se estiver espelhado, o footprint e corrigido girando
> 180 graus ou espelhando em Y, sem editar o esquema.

O footprint e gerado por script, para que o mapeamento continue auditavel:

```text
python hardware/tools/kicad/versao-smd/gen_esp32_fp.py
```

E pode ser validado sozinho, sem abrir o KiCad, pelo script
`hardware/tools/kicad/posicionar/check_fps.py`, que confere se todo footprint
referenciado no esquema existe na biblioteca.

> Pendencia preexistente: `RA-02` tem um texto de serigrafia de 0,7 mm abaixo do
> minimo de 0,8 mm do DRC. Nao foi alterado aqui porque o footprint e usado por
> outros projetos.
