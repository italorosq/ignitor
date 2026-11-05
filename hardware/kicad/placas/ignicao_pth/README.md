# Ignição PTH

Placa de 75 × 80 mm, duas camadas, quatro furos M3. Mesma topologia da SMD;
mudam os encapsulamentos (D1 1N5818, C3 de 10 µF e Q3 BC337).

## Estado

- DRC: 0 erros, 100 avisos (serigrafia e biblioteca), 0 desconexões.
- Paridade: 4 itens, todos os furos `H1`–`H4`.
- `Q1.3`/`J9.1` no GND; `Q1.2`/`J9.2` no dreno. O `J9.1` é o retorno
  BAT−/GND; o `J9.2` é o NO do relé/dreno.
- Pacote JLCPCB antigo; regenerar antes de fabricar.

## Conectores

| Ref | Uso |
| --- | --- |
| J1 | entrada 5 V |
| J2/J3 | botão (comando) |
| J4/J5 | LED do botão (comando) |
| J7 | módulo relé (ignição) |
| J8 | ARM/RBF (ignição) |
| J9 | dreno/source do Q1 (ignição) |
| J10 | buzzer |
| J11 | OLED (comando) |

## Validação

```powershell
$cli = "C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"
& $cli sch erc --severity-all ignicao_pth.kicad_sch
& $cli pcb drc --severity-all --schematic-parity ignicao_pth.kicad_pcb
```
