# Estado do projeto

Atualizado em 2026-11-04. Os números de DRC são do snapshot salvo às 11:19
(hash `37D7…`). A PCB SMD mudou durante a revisão; rode o DRC de novo antes de
fabricar.

## Placas

| Placa | Dimensão | DRC | Estado |
| --- | --- | --- | --- |
| Ignição SMD | 78,8 × 57,3 mm | 7 erros, 0 desconexões, 2 itens de paridade | candidata; não fabricar ainda |
| Ignição PTH | 75 × 80 mm | 0 erros, 100 avisos, 4 itens de paridade | funcional; limpeza pendente |
| Ignição CNC | 50 × 90 mm | 30 erros, 57 conexões faltando | em projeto |

### SMD

Os 7 erros atuais:

- 4 de clearance: `Net-(Q1-D)` × zona GND (0,4305 mm) e `Net-(Q2-B)` × zona
  GND (0,169 mm em três trechos).
- 3 de annular width nos pads do Q4 (0,099988 mm contra 0,1 mm).

Não há curtos nem conexões faltando. O pacote JLCPCB está desatualizado: o
BOM/CPL não tem o Q4 e o A1 está em posição antiga. A placa também não tem os
quatro furos M3.

O esquema ainda trata `Q1.3`/`J12.1` como `Net-(Q1-S)`, mas a PCB liga os dois
ao GND. A PCB está correta para chave de baixo lado; falta alinhar o esquema.

### PTH

Não há erros de DRC. Os 100 avisos são de serigrafia e biblioteca. Os 4 itens de
paridade são os furos `H1`–`H4`. O pacote JLCPCB é antigo e precisa ser
regenerado.

### CNC

A placa atual tem 29 footprints e nenhuma trilha. O relayout para 90 × 100 mm
está documentado, mas não foi executado. Não fabricar.

## Firmware

| Estação | Arquivo | Estado |
| --- | --- | --- |
| Comando | `firmware/micropython/estacao_comando_esp.py` | ESP32, botão, OLED, LEDs, buzzer e LoRa |
| Ignição | `firmware/micropython/estacao_ignicao_esp.py` | ESP32, relé, Q1/Q2, LEDs, buzzer e LoRa |
| Pico | `firmware/micropython/legacy/` | legado; não usado nas placas atuais |

O comando tem OLED e mostra o estado da ignição. A ignição não tem botão, OLED,
EXP nem ADC.

## Pendências

- Corrigir os 4 erros de clearance e os 3 de annular width da SMD.
- Ligar `Q1.3`/`J12.1` ao GND no esquema da SMD.
- Regenerar o pacote JLCPCB da SMD depois de fechar a revisão.
- Decidir sobre os furos M3 da SMD: adicionar na placa ou refazer a caixa.
- Regenerar o pacote JLCPCB da PTH.
- Verificar se o módulo relé solta com 3,3 V no pino IN. Se não, usar módulo
  compatível ou um level shifter.
- Adicionar pull-ups de 10 k em NSS e RESET do RA-02, pull-down de 10 k na base
  do Q4 e pull-down de 10 k no GPIO12.
- Adicionar 10 µF + 100 nF perto do RA-02/OLED.
- Proteger a entrada J1 contra polaridade invertida e colocar fusível.
- Limpar avisos de serigrafia e biblioteca.
- Executar ou cancelar o relayout da CNC.

## Como medir

```powershell
$cli = "C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"
$raiz = "hardware/kicad/placas"

foreach ($placa in "ignicao_smd", "ignicao_pth", "ignicao_cnc") {
    & $cli sch erc --severity-all "$raiz/$placa/$placa.kicad_sch"
    & $cli pcb drc --severity-all --schematic-parity "$raiz/$placa/$placa.kicad_pcb"
}
```
