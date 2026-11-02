# Ignição PTH

> **Status: funcional, limpeza pendente.** ERC zerado, DRC sem erros e sem
> conexões faltando; restam 100 avisos (serigrafia e biblioteca) e 4 itens de
> paridade de footprints. Ver [`../../../../docs/ESTADO_DO_PROJETO.md`](../../../../docs/ESTADO_DO_PROJETO.md).

## Arquivos

| Arquivo | Função |
| --- | --- |
| `ignicao_pth.kicad_pro` | projeto KiCad 10 |
| `ignicao_pth.kicad_sch` | folha raiz |
| `ignicao_pth.kicad_pcb` | PCB roteada |
| subfolhas `*.kicad_sch` | alimentação, botão, buzzer, expansão, LEDs/OLED, LoRa, MCU, relé |
| `datasheets/` | datasheets usados no projeto |
| `jlcpcb/` | pacote de fabricação (conferir atualidade antes de usar) |

## Especificações

| Item | Valor |
| --- | --- |
| Dimensão | 75 × 80 mm |
| Camadas | 2 (1 oz) |
| MCU | ESP32 DevKit V1, 30 pinos (ESP32-WROOM-32) |
| Footprints | 35 |
| Trilhas | 173 |
| Furos de montagem | 4 × M3 |

## Conectores

| Ref | Uso |
| --- | --- |
| J1 | entrada 5 V (buck) |
| J7 | módulo relé |
| J9 | borne de ignição / SKIB |
| J10 | buzzer |
| J11 | OLED (I2C) |
| J2 / J3 | botão (COM / NO) |
| J4 / J5 | LED do botão |
| J8 | endstop / switch |

## Validação

```powershell
$cli = "C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"
& $cli sch erc --severity-all ignicao_pth.kicad_sch
& $cli pcb drc --severity-all --schematic-parity ignicao_pth.kicad_pcb
```

## Pendências

1. Revisar os 4 itens de paridade (`extra_footprint`).
2. Limpar os avisos de serigrafia e de biblioteca.
3. Regenerar o pacote JLCPCB se a PCB tiver mudado desde a última geração.

> O pacote em `jlcpcb/` foi gerado antes de algumas revisões; trate como
> histórico até regenerar com `gen_jlc_package.py`.
