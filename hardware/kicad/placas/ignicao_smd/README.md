# Ignição SMD

Placa de 78,8 × 57,3 mm, duas camadas. É a mesma placa das duas estações; na
comando não são montados Q1, Q2, J7/J8/J12 nem o relé, e o OLED J11 não é
montado na ignição.

## Estado

- DRC: 4 erros de clearance, 0 desconexões, 2 itens de paridade.
- Sem curtos. Os pads do Q4 foram corrigidos.
- Sem furos M3 na revisão atual.
- Pacote JLCPCB desatualizado: o BOM/CPL não tem o Q4 e o A1 está em posição
  antiga.

Não fabricar antes de corrigir o clearance e regenerar o pacote.

## Conectores

| Ref | Uso |
| --- | --- |
| J1 | entrada 5 V |
| J2/J3 | botão (comando) |
| J4/J5 | LED do botão (comando) |
| J7 | módulo relé (ignição) |
| J8 | ARM/RBF (ignição) |
| J10 | buzzer |
| J11 | OLED (comando) |
| J12 | dreno/source do Q1 (ignição) |

## Validação

```powershell
$cli = "C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"
& $cli sch erc --severity-all ignicao_smd.kicad_sch
& $cli pcb drc --severity-all --schematic-parity ignicao_smd.kicad_pcb
```

O esquema e a PCB estão alinhados: `Q1.3`/`J12.1` no GND e `Q1.2`/`J12.2` no
dreno. O `J12.1` é o retorno BAT−/GND; o `J12.2` é o NO do relé/dreno.
