# Projetos KiCad

Os projetos ativos ficam em `placas/`, a biblioteca compartilhada em `shared/lib/`
e as simulações em `spice/`.

| Placa | Dimensão | Camadas | Estado |
| --- | --- | --- | --- |
| Ignição SMD | 78,8 × 57,3 mm | 2 | candidata; corrigir DRC |
| Ignição PTH | 75 × 80 mm | 2 | funcional; limpeza pendente |
| Ignição CNC | 50 × 90 mm | 1 | em projeto |

A mesma PCB serve às duas estações. Na comando não são montados Q1, Q2,
J7/J8/J12 e o relé; na ignição não é montado o OLED J11.

## Como abrir

1. Instale o KiCad 10.
2. Abra o `.kicad_pro` da placa.
3. A biblioteca é resolvida por `${KIPRJMOD}/../../shared/lib/`.

## Como validar

```powershell
$cli = "C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"
& $cli sch erc --severity-all placas/ignicao_smd/ignicao_smd.kicad_sch
& $cli pcb drc --severity-all --schematic-parity placas/ignicao_smd/ignicao_smd.kicad_pcb
```

O estado atual e as pendências ficam em
[`../../docs/ESTADO_DO_PROJETO.md`](../../docs/ESTADO_DO_PROJETO.md).
