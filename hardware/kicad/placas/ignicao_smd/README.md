# Ignição SMD

> **Status: candidata — NÃO FABRICAR.** O arquivo roteado foi promovido a
> oficial em 2026-11-02, mas o DRC ainda acusa 5 curtos reais, 5 bridges de
> máscara, 13 sobreposições de courtyard, 3 conexões faltando e 1 violação de
> clearance. Ver [`../../../../docs/ESTADO_DO_PROJETO.md`](../../../../docs/ESTADO_DO_PROJETO.md).

## Arquivos

| Arquivo | Função |
| --- | --- |
| `ignicao_smd.kicad_pro` | projeto KiCad 10 |
| `ignicao_smd.kicad_sch` | folha raiz |
| `ignicao_smd.kicad_pcb` | PCB roteada (promovida de `smd_fr/` em 2026-11-02) |
| `alimentacao.kicad_sch`, `botao.kicad_sch`, `BUZZER.kicad_sch`, `EXPANSAO.kicad_sch`, `leds_oled.kicad_sch`, `LORA.kicad_sch`, `mcu_esp32.kicad_sch`, `protecao.kicad_sch`, `rele.kicad_sch` | subfolhas |
| `datasheets/` | datasheets usados no projeto |
| `jlcpcb/` | pacote de fabricação (gerar novamente antes de usar) |

## Especificações

| Item | Valor |
| --- | --- |
| Dimensão | 75 × 75 mm |
| Camadas | 2 (1 oz) |
| MCU | ESP32 DevKit V1, 30 pinos (ESP32-WROOM-32) |
| Footprints | 34 |
| Trilhas | 191 (versão roteada promovida) |
| Furos de montagem | 4 × M3 |
| Máscara | roxa (opção paga na JLCPCB) |

## Conectores

| Ref | Uso |
| --- | --- |
| J1 | entrada 5 V (buck) |
| J7 | módulo relé |
| J6 | NO_RELE (contato do relé) |
| J9 | SKIB (saída para o ignitor) |
| J10 | buzzer |
| J11 | OLED (I2C) |
| J2 / J3 | botão (COM / NO) |
| J4 / J5 | LED do botão |
| J8 | endstop / switch |

## Mapa de GPIOs

O mapa oficial está no firmware
[`firmware/micropython/estacao_ignicao_esp.py`](../../../../firmware/micropython/estacao_ignicao_esp.py)
e resumido em [`hardware/README.md`](../../../README.md#estação-de-ignição--esp32-devkit-v1-30-pinos).

## Validação

```powershell
$cli = "C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"
& $cli sch erc --severity-all ignicao_smd.kicad_sch
& $cli pcb drc --severity-all --schematic-parity ignicao_smd.kicad_pcb
```

## Pendências antes de fabricar

1. Corrigir os 5 curtos (`shorting_items`) e a violação de clearance.
2. Corrigir as 3 conexões faltando.
3. Resolver as 13 sobreposições de courtyard e os 5 bridges de máscara.
4. Revisar a paridade esquema/PCB (17 itens, incluindo conflito de rede Q1-G/GND).
5. Regenerar o pacote `jlcpcb/` com o gerador canônico:
   `python ../../../tools/kicad/fabricacao/gen_jlc_package.py .`

> O pacote atual em `jlcpcb/` pode estar de uma revisão anterior. Não envie
> para a JLCPCB sem regenerar e conferir BOM/CPL contra a PCB.
