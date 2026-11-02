# Projetos KiCad

Projetos ativos em [`placas/`](./placas/), biblioteca compartilhada em
[`shared/lib/`](./shared/lib/) e simulações em [`spice/`](./spice/).

## Matriz de placas

| Placa | Projeto | Dimensão | Camadas | Estado |
| --- | --- | --- | --- | --- |
| Ignição SMD | [`placas/ignicao_smd/`](./placas/ignicao_smd/) | 75×75 mm | 2 | **Candidata — não fabricar** |
| Ignição PTH | [`placas/ignicao_pth/`](./placas/ignicao_pth/) | 75×80 mm | 2 | Funcional, limpeza pendente |
| Ignição CNC | [`placas/ignicao_cnc/`](./placas/ignicao_cnc/) | 50×90 mm | 1 | Em projeto |

O projeto da estação de comando foi removido do repositório. Os gerbers
históricos ficam em [`../gerbers/legado/pcbcomando/`](../gerbers/legado/pcbcomando/).

## Como abrir

1. Instale o **KiCad 10**.
2. Abra o `.kicad_pro` da placa desejada.
3. A biblioteca compartilhada é resolvida por caminho relativo
   (`${KIPRJMOD}/../../shared/lib/`), sem depender de bibliotecas globais.
4. Não versione `.history/`, `analysis/`, `*.kicad_prl`, `jlcpcb/project.db`
   nem intermediários de roteamento. Eles já estão no `.gitignore`.

## Como validar sem abrir a GUI

```powershell
$cli = "C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"

# ERC
& $cli sch erc --severity-all placas/ignicao_smd/ignicao_smd.kicad_sch

# DRC + paridade esquema/PCB
& $cli pcb drc --severity-all --schematic-parity placas/ignicao_smd/ignicao_smd.kicad_pcb
```

Para conferir a biblioteca compartilhada:

```powershell
& "C:\Program Files\KiCad\10.0\bin\python.exe" -u `
    ../tools/kicad/biblioteca/extrair_biblioteca.py --check
```

> **Pendência conhecida:** o `--check` ainda reporta 61 componentes que vêm de
> bibliotecas globais do KiCad (S8050, BC337, 1N5819, TO-92, MountingHole
> etc.). O recorte local precisa ser regenerado; até lá, esses símbolos
> resolvem pelas bibliotecas padrão do KiCad.

## Estrutura

```text
kicad/
├── placas/
│   ├── ignicao_smd/      # projeto SMD + datasheets + jlcpcb/
│   ├── ignicao_pth/      # projeto THT + datasheets + jlcpcb/
│   └── ignicao_cnc/      # variante CNC (em projeto)
├── shared/lib/           # símbolos, footprints e modelos 3D compartilhados
└── spice/                # decks LTspice e resultados por módulo
```

## Documentos relacionados

- [Estado real das placas](../../docs/ESTADO_DO_PROJETO.md)
- [Arquitetura do sistema](../../docs/ARQUITETURA.md)
- [Ferramental KiCad](../tools/kicad/README.md)
- [Biblioteca compartilhada](./shared/lib/README.md)
