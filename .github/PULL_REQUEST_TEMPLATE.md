# Pull Request

## Resumo

<!-- O que muda e por quê? -->

## Tipo de mudança

- [ ] Correção de bug
- [ ] Nova funcionalidade
- [ ] Refatoração/organização
- [ ] Documentação
- [ ] Hardware (KiCad)
- [ ] Firmware
- [ ] CI/ferramental

## Checklist

- [ ] `ruff check firmware/ test/` passa
- [ ] `python -m pytest test/ -v` passa
- [ ] `python scripts/check_links.py` passa
- [ ] `python scripts/check_repo.py` passa
- [ ] Se mexeu em KiCad: ERC/DRC antes/depois registrados
- [ ] Se foi só renomeação/movimentação: netlist antes/depois idêntica
- [ ] `docs/ESTADO_DO_PROJETO.md` atualizado, se o estado da placa mudou
- [ ] Nenhum artefato gerado, backup ou credencial no diff

## Segurança

<!-- Alguma mudança afeta o laço de disparo, os gates Q1/Q2, o relé ou o
     procedimento de aborto? Se sim, descreva a validação. -->
