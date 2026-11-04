# Changelog

Baseado em [Keep a Changelog](https://keepachangelog.com) e [Versionamento Semântico](https://semver.org).

## [Não lançado] - 2026-11-04

### Alterado
- Separação dos firmwares: `estacao_comando_esp.py` (ESP32 + OLED) e
  `estacao_ignicao_esp.py` (ESP32, sem OLED, botão, EXP ou ADC).
- Contagem de 10 s; o comando toca o tema do Mario ao receber
  `IGNITION_COMPLETE`.
- Pico movido para `firmware/micropython/legacy/`.
- Testes consolidados em `test/test_firmware.py`; scripts de bancada em
  `test/bancada/`.
- Documentação reescrita e relatórios antigos removidos.

## [1.1.0] - 2026-11-02

### Alterado
- **Reorganização do repositório**: projetos KiCad movidos para
  `hardware/kicad/placas/` e renomeados para `ignicao_smd`, `ignicao_pth` e
  `ignicao_cnc`; tabelas de biblioteca e caminhos de modelos 3D ajustados para
  `${KIPRJMOD}/../../shared/lib/`.
- A PCB SMD roteada (`smd_fr/pcbsmd_routed.kicad_pcb`) foi promovida a arquivo
  oficial de trabalho. Ela continua **não fabricável** (5 curtos, 3
  desconexões, 27 erros de DRC) e está marcada como candidata.
- `firmware/data/` movido para `software/web/`; a pasta `software/` deixou de
  ser apenas um placeholder legado.
- BOM/CPL de `hardware/kicad/**/jlcpcb/**` voltaram a ser versionados; o
  `.gitignore` agora separa fontes de artefatos gerados.
- Documentação reorganizada: `docs/ESTADO_DO_PROJETO.md`,
  `docs/ARQUITETURA.md`, `CONTRIBUTING.md`, READMEs por placa e histórico em
  `docs/historico/`.
- Ferramentas de fabricação consolidadas em
  `hardware/tools/kicad/fabricacao/gen_jlc_package.py`; a duplicata
  `check_fps.py` e o antigo `gen_jlc.py` foram removidos.

### Adicionado
- CI no GitHub Actions: `ruff check` no firmware/testes, testes de pinagem e
  verificacao de links relativos da documentacao.
- **Testes de bancada modularizados**: `test/mp_teste_comum.py` (infra
  compartilhada: buzzer, botao, I2C/OLED, telas, sequencia de ignicao e
  logo), `test/mp_teste_ignicao.py` (sequencia isolada no ESP8266),
  `test/mp_teste_transistor.py` (fail-safe e ordem da cadeia Q1/Q2 no ESP32,
  com carga dummy) e `test/mp_teste_rele.py` (interlock, toggles e ciclos do
  SRD-05VDC no ESP32); `mp_teste_hardware_esp8266.py` refatorado para o
  modulo comum.
- `test/test_scripts_bancada.py`: regressao estatica da bancada (compila os
  `mp_*.py`, confere pinos ESP32 x firmware, gates OFF no boot, rele inativo
  e ordem de desarme Q1 -> rele -> Q2), rodando tambem no CI.
- `test/test_pinagem.py`: regressao estatica de pinagem, tempos de seguranca e
  protocolo LoRa (cobre a classe de bug dos commits "alinha pinagem").
- `ruff.toml` e `requirements-dev.txt` para desenvolvimento local.
- **Hardware**: variante `pcbignicao_CNC/pcbcnc` para fabricacao caseira em CNC
  router — **1 camada (B.Cu)**, trilhas de 1,0 mm (com neck-downs curtos de
  0,8/0,6 mm), sem plano de terra, todos PTH e **22 jumpers de fio** com 27
  ilhas de solda (`JMP1`..`JMP27`) nas ligacoes que nao fecham em uma face;
  pacote de fresagem em `pcbcnc/cnc/` (gerber B_Cu + contorno, drill, dxf,
  preview e DRC com 0 erros).
- **Ferramentas**: `hardware/tools/kicad/cnc/fill_gaps.py` (roteador A* que
  fecha as ligacoes deixadas em aberto pelo Freerouting) e
  `hardware/tools/kicad/cnc/islands.py` (estende as ligacoes restantes e cria
  as ilhas de solda dos jumpers); `route.py` aceita argumentos extras do
  Freerouting (ex.: roteamento de 1 face); `set_netclasses.py` ganhou o perfil
  `pcbcnc` (netclasses, regras e severidades da variante CNC).

### Removido
- Projeto KiCad da estação de comando (`pcbcomando`) do repositório. Os
  gerbers históricos permanecem em `hardware/gerbers/legado/pcbcomando/`.
- `hardware/tools/kicad/fabricacao/gen_jlc.py` (substituído por
  `gen_jlc_package.py`) e a cópia duplicada de `check_fps.py`.
- Artefatos locais do `.opencode/`, `AUDITORIA_PCB/`, `analysis/` e
  intermediários de roteamento do índice do Git.

### Corrigido
- `requirements.txt`: removido `screen`, pacote PyPI homonimo ao binario do
  sistema, que fazia o `pip install -r requirements.txt` falhar.
- Documentacao: MCU da estacao de ignicao corrigido para ESP32 DevKit V1
  (ESP32-WROOM-32, 30 pinos); o ESP32-C3 SuperMini nao corresponde ao firmware.
- Espacos em branco ao final de linha nos firmwares.

### Planejado
- Firmware validado
- Testes de campo
- Cases 3D

## [1.0.0] - 2026-04-21

### Adicionado
- **Hardware**: BOM e pinagem para ESP32-C3 SuperMini (Estação de Ignição)
- **Firmware**: `estacao_ignicao_esp.py` para ESP32-C3
- **Protocolo**: Documentação simplificada com diagrama de estados
- **Documentação**: Repositório refatorado (arquivos renomeados, índice consolidado)

### Alterado
- **BOM**: Comando usa Raspberry Pi Pico; Ignição usa ESP32-C3 SuperMini
- **Estrutura**: docs/ renomeado para padrão consistente

## [0.1.0] - 2024-11-14

### Adicionado
- Estrutura inicial do repositório
- Documentação de arquitetura
- BOM e pinagem Raspberry Pi Pico
- Protocolo LoRa 433 MHz
- Guias de instalação e troubleshooting
- Plano de testes