# Revisão pré-fabricação — Ignição SMD e PTH (2026-10-15)

Revisão completa das duas placas de ignição antes de mandar fabricar (atualizada
com a verificação do módulo ESP32 e a campanha de simulação por módulos):

| Placa | Projeto | Dimensões | Camadas | Pacote fab |
| --- | --- | --- | --- | --- |
| Ignição SMD | `hardware/kicad/pcbignicao/pcbignicao_smd/pcbsmd` | 95 × 95 mm | 2, 1,6 mm | `jlcpcb/` (gerber+BOM+CPL) |
| Ignição PTH | `hardware/kicad/pcbignicao/pcbignicao_PTH/pcbpth` | 100 × 100 mm | 2, 1,6 mm | `jlcpcb/` (gerber+BOM) |

> Nota de estado: o projeto PTH foi renomeado de `pcbsmd/` para `pcbpth/` durante a
> revisão; um `.kicad_pro` órfão ficou em `pcbignicao_PTH/pcbsmd/` (idêntico, pode
> ser apagado). O KiCad estava aberto durante a revisão; nada foi gravado nos projetos.

## Veredito

**PRONTO PARA FABRICAR** (estado de 2026-10-15, após as correções da 2ª fase — ver
"Correções aplicadas"). DRC das duas placas: **0 erros, 0 itens desconectados,
0 problemas de paridade** (SMD resta apenas aviso cosmético de serigrafia; nada de
cobre). Pacotes JLCPCB regenerados e validados contra a convenção do Fabrication
Toolkit (BOM/CPL do SMD batem 100% com o pacote oficial regenerado pelo toolkit;
CPL da PTH validado por cruzamento com o cobre/DRC do próprio KiCad).

Checklist de pedido: 1,6 mm, 1 oz, HASL; contorno 95×95 (SMD) e 100×100 (PTH);
máscara roxa é opção paga no SMD; conferir no preview de montagem a rotação do D1
(SS34/SMA) e manter os THT fora da montagem; PTH = somente placa bare.

## Correções aplicadas (2ª fase, 2026-10-15)

| Item | Onde | Correção | Verificação |
| --- | --- | --- | --- |
| SKIB/J9 no laço de disparo | SMD (esquema+PCB) | J9 religado ao **Q1.S** (`Net-(Q1-S)` = {J9.1, Q1.3}); LED D2 + R3 10k removidos do projeto | netlist + cobre + paridade 0 — **o ignitor dispara pelo caminho NO→J6→Q1→J9→ignitor** (fiação externa documentada no README) |
| Trilha pendurada RELE_IN | SMD | Segmento de 1,28 mm removido | DRC: warning zerado |
| Ilhas de cobre na zona GND | SMD+PTH | `island_removal_mode` → 0 (remover ilhas) + refill | 14 `isolated_copper` zerados |
| Zona sem net (`net 0`) | PTH | Zona atribuída ao **GND** + refill | 8 itens desconectados zerados; plano de terra real nas duas camadas |
| `GATE_2` interrompida | PTH | Trilha estendida até o pad 2 do R6 (250,38; 160,46) | DRC: desconexão zerada |
| Sobras D2/R5 | PTH | Footprints + 5 trilhas removidos (circuito indicador antigo) | Paridade 0; furos 106→102 |
| `+5V_RELE` na borda | PTH | Traço superior afastado (94,69→94,99 mm; folga 0,27→0,57) + desvio de 0,3 mm no R9 | DRC borda e clearance zerados |
| Pacotes JLCPCB | ambas | Regenerados com `hardware/tools/kicad/fab/gen_jlc_package.py` (kicad-cli): gerber X2, drill PTH/NPTH + mapas, BOM/CPL | SMD: BOM 24 grupos OK vs toolkit / CPL 0 divergências (29 refs); PTH: 28 comps, furos 102 |

Notas: o CPL do pacote **antigo** da PTH usava âncora do footprint como posição (não
o centro) — foi substituído pela convenção correta (centro da bbox dos pads, igual ao
toolkit do SMD). Backups dos pacotes anteriores em `%TEMP%\opencode\jlcpcb_bk_*` e das
PCBs (`*_bk*.kicad_pcb`).

## Correção de análise — módulo ESP32 (A1) verificado OK

A análise anterior desta revisão levantou a hipótese de que o par símbolo+footprint do
A1 (`PCM_SL_Development_Board:ESP32_DevKit_V1_DOIT_30GPIOs` +
`PCM_SL_Development_Boards:DOIT_ESP32_DEVKIT_30Pins`) estivesse espelhado. **Era falso
alarme do revisor** (erro de orientação em raciocínio de rotação, não dos arquivos).
Verificação final, conclusiva:

- Imagem oficial do diagrama (espboards, 3200 px) baixada e inspecionada visualmente:
  com o USB no topo, a coluna **esquerda** é `3V3, GND, D15, D2, D4, D16, D17, D5, D18,
  D19, D21, D3, D1, D22, D23` e a **direita** é `VIN, GND, D13, D12, D14, D27, D26, D25,
  D33, D32, D35, D34, VN, VP, EN` (recortes salvos em `analysis/2026-10-15_1244/doit_verify_*.png`).
- Medição das margens: footprint topo = **10,69 mm** / base = **5,45 mm**; placa física
  topo (USB) ≈ **10,0 mm** / base (antena) ≈ **5,8 mm** ⇒ a ponta USB do footprint é o topo.
- Nessa orientação, os pads **1–15** (coluna esquerda, 3V3→D23) e **16–30** (coluna
  direita, EN→VIN numerada de baixo para cima) casam **pino a pino** com o módulo.
- O render 3D (`analysis/2026-10-15_1244/top_render.png`) mostra o módulo encaixado com
  o USB no topo, coerente com tudo acima.

⇒ **A1 correto**: símbolo, footprint, netlist e firmware estão consistentes entre si e
com o módulo físico. Nada a corrigir no A1. (O rascunho não usado
`ignitor.pretty/ESP32_DevKit-30.kicad_mod` tem numeração estilo DIP e **não deve ser
usado** como está — pode ser removido ou refeito.)

## Simulação por módulos (LTspice 26.1.1)

Campanha completa em `hardware/kicad/pcbignicao/spice/` (bancadas `.cir`, modelos,
runner em lote e logs). Tabela completa em `spice/results/RESULTADOS.md`. Resumo:

| Módulo | Resultado | Veredito |
| --- | --- | --- |
| M1 entrada + diodo + LDO do DevKit | V(vin) mín.: **4,597 V (SMD)** / **4,270 V (PTH)**; V(3V3)=3,300 V nas duas | OK · **PTH com margem menor (~0,27 V)** — ver achado 3 |
| M2 bloqueio de backfeed USB | I reversa 0,2 µA (SS34) / 10 nA (1N5400); USB sozinho roda o DevKit (125 mA) | OK |
| M3 chave do GND do relé (Q2) | Vgs=3,229 V; Vds=2,09 mV (Rds≈40 mΩ); Pd=0,11 mW; OFF seguro (pulldown) | OK |
| M4 entrada IN do relé (GPIO32) | 8,07 / 4,13 / 3,57 mA (Rp 1k/4,7k/10k) | OK |
| M5 saída de ignição (Q1, 2 s) | **8,04 A @8,4 V** (5,75 A @6 V; 7,09 A @7,4 V) — bate com o “8 A de pulso” documentado; P ≤ 2,83 W; E ≤ 5,7 J no pulso | OK |
| M6 LEDs | 6,03 mA por canal; SKIB (10k) 0,15 mA | OK · SKIB quase invisível (conferir intenção) |
| M7 buzzer no GPIO14 | 41,2 mA @80 Ω (**acima dos 40 mA abs!**), 27,5 @120 Ω, 18,3 @180 Ω, 13,2 @250 Ω | **Atenção — seleção de componente** |
| M8 I2C do OLED | tr = 242 ns (2,2k/50p) … **1,03 µs (4,7k/100p)** … 4,4 µs (10k/200p) | **Atenção — 400 kHz do firmware não atende com pull-up típico** |
| M9 droop do 3V3 no RA-02 | dip no TX: 146 mV sem decap → 111 mV (100n) → **14 mV (10 µF)** | OK · quantifica a recomendação de decap local |
| M10 SPI 1 MHz | pico 3,52 V / mínimo −0,22 V (SMD); 3,53/−0,23 V (PTH) | OK |
| M11 bancadas da skill (adaptadas) | Vth dos FETs = 1,5417 V; Z do rail 5V: 15,2 mΩ @100 kHz, 5,3 mΩ @1 MHz | OK |

**Achados acionáveis da simulação:**

1. **Buzzer (M7):** sem transistor, toda a corrente passa pelo GPIO14. Especificar
   **buzzer ativo 3 V com consumo ≤20 mA @3,3 V** (≥180 Ω equivalente); um modelo de
   80 Ω puxaria 41 mA (acima do máximo absoluto). O BOM ainda não tem buzzer — decisão de compra.
2. **I2C 400 kHz (M8):** com pull-ups típicos de módulo OLED (4,7k) o tempo de subida
   fica em 0,5–2,2 µs (Fast-mode pede ≤300 ns). Opções: firmware a **100 kHz** ou
   pull-ups de 2,2k; não bloqueia a fabricação.
3. **PTH com 1N5400 (M1):** o diodo consome ~0,7 V do headroom do LDO; margem de
   ~0,27 V em 5,0 V (contra ~0,60 V na SMD). Conferir a tensão real do buck (se <5,0 V,
   considerar SS34/1N5822) e não usar WiFi no firmware (burst de ~500 mA não fecha na PTH).
4. **Decap local no U1 (M9):** 100 n + 10 µ junto ao RA-02/OLED reduz o dip de TX de
   146 mV para 14 mV — mantém-se como recomendação para a próxima revisão.

Limitações: modelos aproximados (IRLZ44N VDMOS fit, LDO comportamental, relé/buzzer
equivalentes R-L), sem eletromecânica, sem WiFi no cenário, parasitários estimados.
A simulação valida os módulos **por netlist** — não cobre o layout de cobre (itens 1–4
do veredito) nem montagem.

## O que foi executado

- `analyze_schematic.py`, `analyze_pcb.py --full --proximity`, `cross_analysis.py`,
  `analyze_emc.py`, `analyze_thermal.py`, `analyze_gerbers.py` (saídas em
  `analysis/<run>/`; runs `2026-10-15_1244` SMD e `2026-10-15_1247` PTH).
- ERC e DRC via `kicad-cli` 10.0.6 (incluindo DRC com refill em modo leitura na PTH).
- SPICE: ngspice (subcircuitos auto-detectados) e **LTspice 26.1.1** (campanha por
  módulos M1–M11, `spice/`).
- Regressão de gerbers em pasta temporária contra o pacote `jlcpcb/`.
- Render 3D + recortes do diagrama oficial para a verificação do A1.
- Datasheets em `datasheets/` (RA-02, DOIT, IRLZ44N, SS34, 1N5400).
- Firmware: netlist ↔ `estacao_ignicao_esp.py` ↔ `test/test_pinagem.py` (10/10 testes).

## Avisos e recomendações (não bloqueiam)

| Item | Placa | Nota |
| --- | --- | --- |
| Pull-down 10k em GPIO12 (`LED_COUNT`) ausente | ambas | README/firmware exigem; ESP32 tem pull-down interno fraco em MTDI (risco moderado de boot). Adicionar na próxima revisão. |
| Sem fiduciais / 0 test points | ambas | Montagem JLC de placa pequena é viável sem fiduciais; melhorar na próxima revisão. |
| Decap local no U1/A1 | ambas | Ver achado 4 (M9). |
| I2C sem pull-ups na placa | ambas | Ver achado 2 (M8). |
| Buzzer no GPIO sem transistor | ambas | Ver achado 1 (M7). |
| Trilha pendurada `RELE_IN` (1,28 mm) | SMD | Limpar no passe final. |
| Silkscreen sobre máscara (alguns refdes) | SMD | Cosmético. |
| `ADC1/ADC2/EXP1/EXP2` são stubs (só rótulo no A1) | ambas | OK; documentar ou usar como test points. |
| Return path SPI (EMC RP-001/RP-002) | ambas | Recomendação de vias de costura junto às transições de camada. |

## Verificação contra datasheet

- **RA-02** (spec completa V1.1, 15 pág.): tabela de pinos confere 100% com o símbolo
  U1 (`1 GND, 2 GND, 3 3.3V, 4 RESET, 5 DIO0 … 12 SCK, 13 MISO, 14 MOSI, 15 NSS, 16 GND`).
- **ESP32 DOIT DEVKIT V1 30 pinos**: layout físico verificado por imagem oficial +
  medição de margens + render 3D (ver “Correção de análise”).
- **IRLZ44N**: TO-220 pinagem 1=G/2=D/3=S ✓; usado como base do fit VDMOS das simulações.
- **SS34 / 1N5400**: polaridade cátodo=faixa; direção do diodo série correta no netlist;
  quedas simuladas 0,37 V (SS34) e 0,70 V (1N5400).
- **Footprint `RA-02_THT`**: adaptador kevinta893 (2×8, 2,54 mm, fileiras 25,4 mm);
  conferir a orientação do módulo no adaptador na primeira montagem.

## Estado dos pacotes de fabricação e BOM/CPL

- **SMD**: pacote regenerado hoje (14:00 pelo toolkit + 15:46 pela ferramenta deste
  repositório, validadas entre si — BOM 100% igual, CPL 0 divergências). BOM com 29
  componentes (D2/R3 fora), LCSC dos 12 SMD; CPL com 29 posições (convenção de centro).
  Sem D2/R3; J9/SKIB presente.
- **PTH**: pacote regenerado nesta revisão (BOM 28 componentes com J6 = borne Phoenix,
  sem D2/R5/J9; CPL 28 posições na convenção correta; gerber/drill com 102 furos).
- ERC: 8 violações SMD / 4 PTH — todas triadas como aceitáveis (ver abaixo); DRC final:
  SMD 0 erros (29 avisos de silk) e PTH 0 violações.

## Falsos positivos triados

- **Espelhamento do A1** — falso alarme do revisor (não do analisador); ver correção acima.
- `GR-004` “paste 24 vs 159 cobre” (SMD): esperado — só 24 pads SMD no total.
- `IO-001` do EMC em J1..J12: conectores internos; sem filtragem necessária.
- ERC `pin_not_driven` nos gates (resistor de gate em série) e `pin_to_pin` do D1
  (proteção série): artefatos; `PU-001` EN: pull-up/RC fica no módulo DevKit.
- `DS-002/SS-001`: auditoria de MPN sobre propriedades do esquema — esperado para
  jellybean/THT; o BOM JLC do SMD tem LCSC de todos os SMD.
- EMC PTH `GP-001/GP-002/PS-002`: consequência da zona sem net (item 2 do veredito).

## Firmware (sincronização aplicada)

Verificação pin a pin do `estacao_ignicao_esp.py` contra o netlist: **todos os GPIOs
batem com o esquema e com a placa física** (SPI 18/23/19, CS 4, RESET 16, DIO0 17,
RELE 32, GATE_1 13, GATE_2 33, BUZZ 14, STATUS 25, LED_BTN 26, LED_COUNT 12, BTN 27,
EXP 2/5/15, ADC 34/35, I2C 21/22).

Correções aplicadas (comportamento elétrico inalterado):

1. `test/test_pinagem.py`: mapa do ESP32 corrigido (`PIN_EXP_A/B/C_NUM` = 2/5/15 no
   lugar dos obsoletos `EXP_IN1/IN2`) — suíte passou de 9/10 para **10/10**.
2. `firmware/micropython/estacao_ignicao_esp.py`: comentários/docstring dos gates
   corrigidos (`GATE_1` → R6 → gate do **Q2**, GND do módulo relé; `GATE_2` → R4 →
   gate do **Q1**, saída do ignitor). Só comentários.

Recomendação pendente (achado 2 da simulação): avaliar `I2C freq` de 400 kHz → 100 kHz
com o módulo OLED real, ou garantir pull-ups de 2,2k. `estacao_ignicao.py` (Pico) é
legado; `estacao_comando.py` fora do escopo.

## Pendências restantes (nenhuma de layout)

1. **BOM**: escolher **buzzer ativo 3 V ≤20 mA @3,3 V** (achado 1 da simulação).
2. **Firmware**: avaliar `I2C` em 100 kHz (ou pull-ups 2,2k) com o módulo OLED real (achado 2).
3. **Próxima revisão** (não bloqueiam): decap 100n+10µ junto ao U1/A1; pull-down 10k em
   GPIO12; fiduciais/test points; verificar tensão real do buck da PTH (achado 3).
4. Pedido JLC: máscara roxa (opção paga, SMD); conferir rotação do D1 no preview;
   PTH = somente placa bare.

## Análises não executadas / limitações

- **Lifecycle audit**: não executado (sem credenciais de distribuidor).
- **Thermal**: 0 componentes avaliados (sem MPN/dissipação no esquema); a energia do
  pulso de ignição foi estimada na simulação (M5).
- **Datasheets**: obtidos manualmente (sem chave DigiKey); extração textual via pypdf.
- Simulação: modelos aproximados e cenários documentados em `spice/README.md`; não
  substitui o teste físico (recomendado testar continuidade e uma ignição com carga
  dummy antes do voo).

## Anexo A — Mapa ground-truth do DOIT DEVKIT V1 30 pinos (vista topo, USB para cima)

| Coluna esquerda (USB→antena) | GPIO | Coluna direita (USB→antena) | GPIO |
| --- | --- | --- | --- |
| 3V3 | — | VIN | — |
| GND | — | GND | — |
| D15 | 15 | D13 | 13 |
| D2 | 2 | D12 | 12 |
| D4 | 4 | D14 | 14 |
| RX2 | 16 | D27 | 27 |
| TX2 | 17 | D26 | 26 |
| D5 | 5 | D25 | 25 |
| D18 | 18 | D33 | 33 |
| D19 | 19 | D32 | 32 |
| D21 | 21 | D35 | 35 |
| RX0 | 3 | D34 | 34 |
| TX0 | 1 | VN | 39 |
| D22 | 22 | VP | 36 |
| D23 | 23 | EN | — |

## Anexo B — Artefatos

- `analysis/2026-10-15_1244/` (SMD) e `analysis/2026-10-15_1247/` (PTH): JSONs dos analisadores.
- `analysis/2026-10-15_1244/{top_render.png, doit_verify_top.png, doit_verify_bottom.png}`:
  render 3D e recortes da verificação do A1.
- `hardware/kicad/pcbignicao/spice/`: campanha LTspice (models/, smd/, pth/, skill_circuits/,
  run_all.ps1, results/ com logs e `RESULTADOS.md`).
- `hardware/tools/kicad/fab/gen_jlc_package.py`: gerador do pacote JLCPCB via kicad-cli
  (gerber X2 + drill + mapas + BOM/CPL na convenção do Fabrication Toolkit), validado
  contra os pacotes oficiais (SMD BOM 100%, CPL 0 divergências).
- `analysis/2026-10-15_1526/` e `2026-10-15_1526-2/` (SMD, pós-correção) + runs anteriores.
- `datasheets/`: RA-02, DOIT, IRLZ44N, SS34, 1N5400.
