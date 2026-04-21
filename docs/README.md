# Documentação do Ignitor

Guias práticos para montar, operar e fazer manutenção.

## Por onde Começar

```
Montar hardware → Gravar firmware → Testar → Usar
```

| O que Você Precisa | Guía |
|-----------------|------|
| Montar as estações | [INSTALL.md](./INSTALL.md#3-montagem-de-hardware) |
| Gravar firmware | [INSTALL.md#4-gravando-firmware](./INSTALL.md#4-gravando-firmware) |
| Testar em bancada | [INSTALL.md#5-validando-operacao](./INSTALL.md#5-validando-operacao) |
| Testar em campo | [test/README.md](../test/README.md) |
| Diagnosticar problemas | [troubleshooting.md](./troubleshooting.md) |
| Entender protocolo | [README_API.md](./README_API.md) |
| Registrar testes | [README_TESTS.md](./README_TESTS.md) |

## Referências Rápidas

- **Pinagem**: [hardware/README.md#pinagem](../hardware/README.md#pinagem)
- **BOM**: [hardware/README.md#lista-de-componentes-bom](../hardware/README.md#lista-de-componentes-bom)
- **Estados LEDs**: [hardware/README.md#estados-dos-leds](../hardware/README.md#estados-dos-leds)
- **Sequência**: [hardware/README.md#sequência-de-operação](../hardware/README.md#sequência-de-operação)

## Avisos

> **⚠️ Segurança**:
> - Sempre use carga dummy (lâmpada/LED) durante testes
> - Não energize módulos LoRa sem antenas
> - Mantenha distância ≥ 10 m do foguete