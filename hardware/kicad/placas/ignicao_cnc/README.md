# Ignição CNC

> **Status: em projeto.** A placa atual tem 50 × 90 mm, 29 footprints e
> **0 trilhas**; o DRC acusa 30 erros, 84 avisos e 57 conexões faltando. O plano
> de relayout para 90 × 100 mm está em
> [`../../../../docs/planejamento/2026-10-relayout-cnc.md`](../../../../docs/planejamento/2026-10-relayout-cnc.md)
> e **não foi executado**. Não fabricar.

## Arquivos

| Arquivo | Função |
| --- | --- |
| `ignicao_cnc.kicad_pro` | projeto KiCad 10 |
| `ignicao_cnc.kicad_sch` | folha raiz |
| `ignicao_cnc.kicad_pcb` | PCB em rascunho (sem trilhas) |
| subfolhas `*.kicad_sch` | alimentação, botão, buzzer, expansão, LEDs/OLED, LoRa, MCU, relé |
| `datasheets/` | datasheets usados no projeto |

## Especificações

| Item | Valor |
| --- | --- |
| Dimensão | 50 × 90 mm |
| Camadas | 1 (B.Cu), sem plano de terra |
| MCU | ESP32 DevKit V1, 30 pinos |
| Footprints | 29 |
| Trilhas | 0 |
| Furos de montagem | — |

## Objetivo

Variante para fabricação caseira em CNC router: uma face, trilhas largas,
jumpers de fio (`JUMPER_ILHA`) onde o roteamento planar não fecha. O relayout
pretendido para 90 × 100 mm inclui:

- GND em barramento/estrela, trilha de 2,0 mm;
- ignição 2,5 mm, potência 2,0 mm, sinal 1,0 mm (mínimo 0,6 mm);
- folga 0,4 mm e cobre-borda ≥ 0,5 mm;
- desacoplamento extra no RA-02 (C4 10 µF);
- 22 jumpers / 27 ilhas de solda na versão anterior.

## Validação

```powershell
$cli = "C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"
& $cli sch erc --severity-all ignicao_cnc.kicad_sch
& $cli pcb drc --severity-all --schematic-parity ignicao_cnc.kicad_pcb
```

## Pendências

1. Executar o relayout (ou decidir abandonar a variante).
2. Rotear a placa e zerar as 57 conexões faltando.
3. Gerar o pacote de fresagem (B.Cu + contorno, drill, DXF, preview).
4. Atualizar o README e o estado do projeto quando a placa ficar pronta.
