# Estado do projeto

**Data:** 2026-11-02
**Branch de referência:** `chore/reorganizacao-2026-11` (merge na `main`)

Este documento é a fonte de verdade sobre **o que está pronto, o que está em
andamento e o que não pode ser fabricado**. Os números de ERC/DRC foram
extraídos com `kicad-cli` 10.0.6 e devem ser reproduzidos antes de qualquer
pedido de PCB.

## Resumo das placas

| Placa | Arquivo canônico | Dimensão | Footprints | Trilhas | ERC | DRC | Desconexões | Paridade | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Ignição SMD | `hardware/kicad/placas/ignicao_smd/ignicao_smd.kicad_pcb` | 75×75 mm | 34 | 191 | 0 | 27 erros + 100 avisos | 3 | 17 | **Candidata — não fabricar** |
| Ignição PTH | `hardware/kicad/placas/ignicao_pth/ignicao_pth.kicad_pcb` | 75×80 mm | 35 | 173 | 0 | 0 erros + 100 avisos | 0 | 4 | Funcional, limpeza pendente |
| Ignição CNC | `hardware/kicad/placas/ignicao_cnc/ignicao_cnc.kicad_pcb` | 50×90 mm | 29 | 0 | 0 | 30 erros + 84 avisos | 57 | 1 | Em projeto |
| Comando | removida do repositório | — | — | — | — | — | — | — | Legado |

> **Paridade** = diferenças entre a netlist do esquema e os footprints da PCB
> (`--schematic-parity`). Não é o mesmo que DRC; ambos precisam estar limpos.

## Bloqueios da Ignição SMD

A versão roteada foi promovida a arquivo oficial de trabalho em 2026-11-02,
substituindo o arquivo sem trilhas. Ela **ainda não pode ser fabricada**:

| ID | Problema | Evidência |
| --- | --- | --- |
| SMD-B01 | 5 curtos entre redes | `shorting_items`: `Net-(Q1-G)`×NSS, `+5V_RELE`×GND (2×), GND×VIN, GND×`+5V_RELE` |
| SMD-B02 | 3 conexões faltando | `unconnected_items` |
| SMD-B03 | 1 violação de clearance | 0,0455 mm contra 0,2000 mm |
| SMD-B04 | 5 bridges de máscara | `solder_mask_bridge` |
| SMD-B05 | 13 sobreposições de courtyard | `courtyards_overlap` |
| SMD-B06 | 17 itens de paridade | inclui conflito `Net-(Q1-G)` × `GND` |

O pacote `hardware/kicad/placas/ignicao_smd/jlcpcb/` é de uma revisão anterior
e **não deve ser enviado** até ser regenerado e conferido.

## Estado da Ignição PTH

- ERC 0, DRC 0 erros e 0 conexões faltando.
- 100 avisos: serigrafia sobre cobre/sobreposição, `lib_footprint_mismatch` e
  `lib_footprint_issues`.
- 4 itens de paridade `extra_footprint` (footprints presentes na PCB e ausentes
  no esquema).
- O pacote `jlcpcb/` precisa ser regenerado se a PCB mudou desde a última
  geração.

## Estado da Ignição CNC

- Placa atual: 50×90 mm, 29 footprints, **0 trilhas**, 57 conexões faltando.
- DRC: 30 erros e 84 avisos.
- O relayout para 90×100 mm com GND em barramento, 22 jumpers e 27 ilhas está
  documentado, mas **não foi executado**:
  [`planejamento/2026-10-relayout-cnc.md`](./planejamento/2026-10-relayout-cnc.md).
- Não existe pacote de fresagem válido na pasta atual. Não fabricar.

## Estação de comando

O projeto KiCad `pcbcomando` foi removido do repositório por decisão de
2026-11-02. Os gerbers antigos ficam em
[`hardware/gerbers/legado/pcbcomando/`](../hardware/gerbers/legado/pcbcomando/)
apenas como registro histórico. O firmware da estação de comando continua em
[`firmware/micropython/estacao_comando.py`](../firmware/micropython/estacao_comando.py)
para o Raspberry Pi Pico.

## Firmware e testes

| Item | Estado |
| --- | --- |
| Ignição ESP32 DevKit V1 | Implementado: botão, OLED, ADC, EXP, logo, sequência de ignição |
| Ignição Pico (THT) | Legado funcional |
| Comando Pico | Funcional |
| Testes estáticos | 16 passando (`pytest test/`) |
| Lint | `ruff check firmware/ test/` passando |
| Testes de bancada | Scripts `test/mp_*.py`; exigem placa e carga dummy |

## Pendências priorizadas

| Prioridade | Item | Onde |
| --- | --- | --- |
| P0 | Corrigir os 5 curtos e o clearance da SMD | `placas/ignicao_smd/` |
| P0 | Corrigir as 3 conexões faltando da SMD | `placas/ignicao_smd/` |
| P1 | Revisar paridade SMD (Q1-G × GND) | `placas/ignicao_smd/` |
| P1 | Revisar os 4 `extra_footprint` da PTH | `placas/ignicao_pth/` |
| P1 | Regenerar pacotes JLCPCB antes de pedir | `fabricacao/gen_jlc_package.py` |
| P2 | Executar (ou cancelar) o relayout CNC 90×100 | `placas/ignicao_cnc/` |
| P2 | Limpar avisos de serigrafia/biblioteca | SMD e PTH |
| P2 | Regenerar o recorte da biblioteca compartilhada (61 itens ainda globais) | `hardware/kicad/shared/lib/` |
| P3 | Validar cases 3D atuais (OpenSCAD) | `hardware/3d_models/` |

## Como reproduzir os números

```powershell
$cli = "C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"
$raiz = "hardware/kicad/placas"

foreach ($placa in "ignicao_smd", "ignicao_pth", "ignicao_cnc") {
    & $cli sch erc --severity-all "$raiz/$placa/$placa.kicad_sch"
    & $cli pcb drc --severity-all --schematic-parity "$raiz/$placa/$placa.kicad_pcb"
}
```

> Os relatórios de auditoria de 2026-10-15 e 2026-10-30 são históricos e não
> versionados. Eles descrevem revisões anteriores das placas; use este documento
> para o estado atual.
