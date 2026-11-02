# Documentação do Ignitor

Guias para montar, operar, testar e manter o sistema.

## Comece por aqui

| Etapa | Documento |
| --- | --- |
| Entender a arquitetura | [ARQUITETURA.md](./ARQUITETURA.md) |
| Saber o que está pronto | [ESTADO_DO_PROJETO.md](./ESTADO_DO_PROJETO.md) |
| Montar | [INSTALL.md](./INSTALL.md#3-montagem-de-hardware) |
| Gravar firmware | [README_ENVIO.md](./README_ENVIO.md) |
| Testar | [../test/README.md](../test/README.md) |
| Diagnosticar | [troubleshooting.md](./troubleshooting.md) |
| Protocolo LoRa | [README_API.md](./README_API.md) |
| Registrar resultados | [README_TESTS.md](./README_TESTS.md) |
| Cases 3D | [ENCLOSURES.md](./ENCLOSURES.md) |

## Referências rápidas

- Pinagem e BOM: [../hardware/README.md](../hardware/README.md)
- Projetos KiCad: [../hardware/kicad/README.md](../hardware/kicad/README.md)
- Biblioteca compartilhada: [../hardware/kicad/shared/lib/README.md](../hardware/kicad/shared/lib/README.md)
- Ferramental de PCB: [../hardware/tools/kicad/README.md](../hardware/tools/kicad/README.md)

## Histórico

Os documentos abaixo descrevem revisões antigas e **não são o estado atual**:

- [historico/RELATORIO_REVISAO.md](./historico/RELATORIO_REVISAO.md)
- [historico/REVISAO_FAB_2026-10-15.md](./historico/REVISAO_FAB_2026-10-15.md)

## Planejamento

- [planejamento/2026-10-relayout-cnc.md](./planejamento/2026-10-relayout-cnc.md) — proposta de relayout da CNC (não executada)

## Design

- [design/PROMPT_FIGMA_SILKSCREEN.md](./design/PROMPT_FIGMA_SILKSCREEN.md)

## Avisos importantes

- Sempre usar carga dummy (lâmpada/LED) durante testes.
- Nunca energizar módulo LoRa sem antena conectada.
- Manter distância mínima de 10 m do foguete em testes de campo.
- Não fabricar a placa SMD enquanto o DRC tiver curtos/desconexões.
