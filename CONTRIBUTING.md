# Como contribuir

## Antes de tudo

Este é um projeto de **ignição de foguete**. Mudanças em firmware, pinagem ou
circuito podem causar acionamento indevido. Leia
[`docs/ARQUITETURA.md`](./docs/ARQUITETURA.md) e
[`docs/ESTADO_DO_PROJETO.md`](./docs/ESTADO_DO_PROJETO.md) antes de mexer em
hardware.

## Requisitos

- Python 3.12+
- KiCad 10 (para abrir/validar os projetos)
- `mpremote` ou `ampy` (para gravar nas placas)
- Git

## Setup

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements-dev.txt
```

## Checagens antes de abrir PR

```bash
ruff check firmware/ test/
python -m pytest test/ -v
python scripts/check_links.py
python scripts/check_repo.py
```

Todas rodam no CI. Se você mexeu em um projeto KiCad, rode também:

```bash
kicad-cli sch erc --severity-all hardware/kicad/placas/<placa>/<placa>.kicad_sch
kicad-cli pcb drc --severity-all --schematic-parity hardware/kicad/placas/<placa>/<placa>.kicad_pcb
```

Os números atuais estão em [`docs/ESTADO_DO_PROJETO.md`](./docs/ESTADO_DO_PROJETO.md).
Não aumente erros/desconexões sem registrar o motivo.

## Fluxo KiCad

1. Abra o `.kicad_pro` da placa em `hardware/kicad/placas/<placa>/`.
2. Rode ERC e DRC antes e depois da mudança.
3. Se alterar a biblioteca, rode:
   `hardware/tools/kicad/biblioteca/extrair_biblioteca.py --check`.
4. Gere o pacote JLCPCB somente com o script canônico:
   `python hardware/tools/kicad/fabricacao/gen_jlc_package.py <pasta-do-projeto>`.
5. Não commite `.history/`, `analysis/`, `*.kicad_prl`, `smd_fr/`,
   `jlcpcb/project.db` nem backups (`*_bk*.kicad_pcb`).

## Branches e commits

- Branch: `feat/...`, `fix/...`, `docs/...`, `chore/...`.
- Commit: Conventional Commits em português, por exemplo:
  `fix(hw): corrige clearance da netclass IGN na SMD`.
- Um assunto por commit. Não misture refatoração de arquivos com mudança
  elétrica.
- Nunca force-push em `main`.

## Checklist de PR

- [ ] `ruff`, `pytest`, `check_links.py` e `check_repo.py` passam.
- [ ] ERC/DRC antes/depois registrados (quando houver mudança de hardware).
- [ ] Netlist antes/depois idêntica (quando for só renomeação/movimentação).
- [ ] Documentação atualizada (`README`, `docs/ESTADO_DO_PROJETO.md`).
- [ ] Nenhum artefato gerado ou credencial no diff.
- [ ] Se a placa não estiver pronta para fabricar, isso está explícito.

## Dúvidas

Abra uma issue com o template de bug/hardware ou converse com o responsável
do projeto. Para mudanças de segurança (laço de disparo, gates, relé),
peça revisão de pelo menos outra pessoa.
