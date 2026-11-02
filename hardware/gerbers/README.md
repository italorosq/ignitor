# Gerbers e pacotes de fabricação

Esta pasta guarda **apenas pacotes históricos**. Os pacotes atuais ficam junto
de cada projeto KiCad:

| Placa | Pacote atual |
| --- | --- |
| Ignição SMD | [`../kicad/placas/ignicao_smd/jlcpcb/`](../kicad/placas/ignicao_smd/jlcpcb/) |
| Ignição PTH | [`../kicad/placas/ignicao_pth/jlcpcb/`](../kicad/placas/ignicao_pth/jlcpcb/) |
| Ignição CNC | [`../kicad/placas/ignicao_cnc/`](../kicad/placas/ignicao_cnc/) (pacote de fresagem na pasta do projeto) |

## Legado

- [`legado/pcbcomando/`](./legado/pcbcomando/) — estação de comando antiga.
  O projeto KiCad foi removido do repositório; estes gerbers ficam só como
  registro histórico.
- [`legado/pcbignicao/`](./legado/pcbignicao/) — revisão THT antiga.
- [`legado/pcbignicao_smd/`](./legado/pcbignicao_smd/) — revisão SMD 2.2, com
  U2/U3 em SOP-4.

> **Não use os pacotes desta pasta para fabricar.** Eles não correspondem
> necessariamente às placas atuais. Consulte o README da placa e o
> [`docs/ESTADO_DO_PROJETO.md`](../../docs/ESTADO_DO_PROJETO.md) antes de pedir
> qualquer PCB.
