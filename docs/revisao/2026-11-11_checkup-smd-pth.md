# Checkup Ignição SMD / PTH — 2026-11-11

Auditoria independente das duas placas ativas do projeto. Escopo: corretude elétrica,
EMC/EMI, layout, ESD/imunidade, DFM e mecânica. **Somente diagnóstico** — nenhum
arquivo de placa foi alterado.

---

## 1. Veredito

| Placa | Veredito | Motivo curto |
|---|---|---|
| **Ignição SMD** | **NÃO FABRICAR** | Q4 fora do BOM/CPL (buzzer), sem furos M3, LEDs D3/D4 sob o DevKit |
| **Ignição PTH** | **FABRICAR COM RESSALVAS** | J10 (buzzer) sob o DevKit, 19 ilhas de cobre, sem desacoplamento no RA-02, relé 3,3 V |

A PTH está mais próxima de fabricável: o pacote JLCPCB atual **bate** com a PCB
(drill e cobre idênticos), e os problemas são de layout/robustez, não de arquivo.
A SMD tem bloqueios de montagem que impedem o uso na caixa atual.

---

## 2. Escopo e método

- **Elétrico**: netlist, pinout contra datasheet, árvore de potência, boot/strapping,
  desacoplamento, proteções de entrada e de saída.
- **EMC/EMI**: plano de terra, caminho de retorno, desacoplamento, chaveamento do
  relé, laço de ignição, antena LoRa, ESD/imunidade.
- **PCB/DFM**: DRC normal e "strict", ERC, paridade esquema↔placa, ilhas de cobre,
  serigrafia, furos, fiduciais, BOM/CPL, gerbers.
- **Não é escopo**: firmware funcional, software, `ignicao_cnc`.

Premissas confirmadas com o usuário: "EC" = EMC/EMI; só diagnóstico; snapshot em
temp; sem exigência formal de FCC/CISPR.

---

## 3. Baseline

- Branch `main`, HEAD `5783c46`, árvore com 29 arquivos modificados + 1 novo.
- Snapshot imutável: `C:\Users\italo\AppData\Local\Temp\opencode\ignitor-audit-2026-11-11\`
  (14,6 MB; 0 divergências de hash em relação ao repo no início).
- Hashes SHA-256 de todos os `.kicad_sch`, `.kicad_pcb`, `.kicad_pro`, `.kicad_prl`,
  BOM/CPL e ZIP em `baseline/baseline.md` dentro do snapshot.
- Cópias com regras "strict" (courtyard, isolated copper, etc.) em
  `mirror_strict/`; DRC normal e strict rodados sobre a **mesma** árvore de
  bibliotecas para comparação justa.

Nenhum arquivo de placa foi modificado. Os artefatos de análise foram gravados em
temp, não no repositório.

---

## 4. O que foi executado

| Etapa | Ferramenta | Estado |
|---|---|---|
| ERC | `kicad-cli sch erc --severity-all` | SMD 12 / PTH 10 violações |
| DRC normal | `kicad-cli pcb drc --schematic-parity` | SMD 92 / PTH 119 |
| DRC strict | `.kicad_pro` com courtyard/isolated como error | SMD 107 / PTH 127 |
| DRC com refill | `--refill-zones` | SMD 88 (4 clearance somem) / PTH 119 |
| Esquemático | `analyze_schematic.py` | OK |
| PCB | `analyze_pcb.py --full --proximity` | OK (inclui connectivity_graph) |
| Cross-domain | `cross_analysis.py` | 1 finding por placa (VS-002) |
| EMC | `analyze_emc.py` | SMD 34 / PTH 32 findings |
| Térmico | `analyze_thermal.py` | 0 findings (nenhum dissipador modelado) |
| Gerbers | `analyze_gerbers.py` | OK |
| SPICE | `simulate_subcircuits.py` + testbenches m1–m12 | SMD 4/4, PTH 3/3 pass |
| Parasitas | `extract_parasitics.py` | 29/28 nets |
| Diff vs 2026-10-15 | `diff_analysis.py` | mudanças grandes de Topologia |
| Lifecycle | não executado | sem MPN/rede |
| Pinout | datasheets RA-02, IRLZ44N, SS34, DOIT | verificado |
| Mecânica | renders 3D + courtyards + alturas | verificado por geometria |

---

## 5. Blockers

### B-01 — Q4 marcado DNP na PCB, ausente do BOM/CPL, mas obrigatório no INSTALL

- **Evidência**: PCB `ignicao_smd` Q4 com `dnp: true`; esquemático Q4 com
  `(dnp no)`; `BOM-ignicao_smd.csv` e `CPL-ignicao_smd.csv` **não têm Q4**;
  `docs/INSTALL.md:26-27` manda montar Q4 na estação de ignição.
- **DRC parity**: "As configurações de 'Não montar' são diferentes".
- **Impacto**: o driver do buzzer não é montado na estação de ignição. A estação
  perde a sinalização sonora de erro/ignição. Se a montagem for JLCPCB, o
  componente simplesmente não vem.
- **Recomendação**: decidir a variante; com Q4 `dnp=no`, regenerar BOM/CPL.
  Corrigir também `attr smd` → `through_hole` no footprint do Q4.
- **Esforço**: 0,5 h.

### B-02 — Placa SMD sem furos M3

- **Evidência**: 0 NPTH; `docs/ENCLOSURES.md:13-14` e `docs/ESTADO_DO_PROJETO.md:26`
  já registram; a PTH tem H1–H4.
- **Impacto**: a placa não fixa na caixa atual sem suporte improvisado. É um
  bloqueio mecânico, não elétrico.
- **Recomendação**: adicionar 4 furos M3 (como a PTH) ou aprovar um suporte
  impresso com prioridade.
- **Esforço**: 2 h + refill + DRC.

### B-03 — LEDs D3/D4 da SMD ficam sob o DevKit

- **Evidência**: A1 courtyard `x=178,7–207,7; y=64,1–115,4`; D3 em
  `(200,76, 82,99)`, D4 em `(186,19, 82,59)`; ambos os LEDs são THT de 5 mm
  (~8,6 mm de altura). O DRC strict acusa `courtyards_overlap` e
  `pth_inside_courtyard`; o render 3D mostra o DevKit cobrindo a região.
- **Impacto**: LEDs de status ocultos e risco de colisão com o módulo (o
  standoff típico de header fêmea é ~8,5 mm). Na PTH os LEDs ficam fora do
  DevKit; na SMD não.
- **Recomendação**: mover D3/D4 para fora do courtyard do A1 (como na PTH) ou
  definir solução mecânica com standoff > 10 mm.
- **Esforço**: 2 h + rerote.

---

## 6. Achados HIGH

| ID | Placa | Achado | Evidência | Impacto | Recomendação |
|---|---|---|---|---|---|
| H-01 | Ambas | J8 (ARM/RBF) usa pinos 1–3; pino 2 é NC; jumper padrão de 2 pinos não fecha 1–3 | Netlist `J8.2` isolado; `ENCLOSURES.md:35`, `INSTALL.md:29` | Trava física ambígua; risco de armar/desarmar errado | Ligar pino 2 ao 3 na PCB, ou usar conector de 2 pinos/chave |
| H-02 | Ambas | Módulo relé 5 V com IN em 3,3 V, sem level shifter; GND chaveado pelo Q2 | `RELE_IN`→GPIO32; firmware ativo-baixo; M4 3,57–8,07 mA; `ESTADO:56` | Relé pode não soltar ou back-power pelo IN | Validar módulo; usar módulo 3,3 V ou level shifter/MOSFET |
| H-03 | Ambas | Sem fusível e sem polaridade reversa no rail `+5V_RELE`; D1 protege só o DevKit | `J1`→`+5V_RELE` direto; C1–C3 no rail; D1 só `VIN`; `ARQUITETURA:88` | Reversão queima eletrolíticos/relé; curto pode incendiar | PTC/fusível + P-MOSFET ou Schottky no rail; conector keyed |
| H-04 | Ambas | Sem desacoplamento local no RA-02; C1–C3 a ~55–60 mm | DC-002; posições; M9: droop 146 mV → 14 mV com 10 µF+100 nF | TX LoRa de 105 mA derruba o 3V3 e pode resetar/perder pacotes | 10 µF + 100 nF junto ao pino 3 do U1 |
| H-05 | Ambas | NSS e RESET do RA-02 sem pull-up | Netlist direta U1↔A1; GPIO4/16 flutuantes no boot | Estado indefinido do SX1278 no boot | 10 kΩ pull-up em NSS e RESET para 3V3 |
| H-06 | SMD | Sem clamp/TVS na saída de ignição (J12 / `Net-(Q1-D)`) | Netlist; IRLZ44N tem E_AS, mas o modelo M12 não inclui indutância de chicote | Kick indutivo pode exceder 55 V e destruir o Q1 | TVS drain-source + snubber; validar com carga indutiva |
| H-07 | PTH | 19 ilhas de cobre isoladas no plano GND (até 90 mm²); `remove_islands=0` | DRC `isolated_copper`; polígonos de fill | Cobre flutuante: EMC, detuning, solda | Ativar remoção de ilhas e refill |
| H-08 | Ambas | Zero vias de costura GND (SMD 10 vias, PTH 2; todas de sinal) | VS-002; nets das vias | Retorno RF/SPI ruim; EMI | Adicionar 20–30 vias de costura |
| H-09 | SMD | Pacote JLCPCB tem F_Cu com fill de zona diferente da PCB atual | 52 operações só no antigo, 63 só no novo; 113 flashes/pads idênticos; B_Cu e drill idênticos | Cobre fabricado ≠ PCB atual | Refill + salvar + regenerar pacote |
| H-10 | Ambas | Sem TVS/ESD nos conectores de painel e no 3,3 V do RA-02 | EP-AUD; datasheet RA-02 p.13 recomenda ESD | ESD no chicote pode destruir GPIO/ESP32 | TVS arrays nos conectores externos |
| H-11 | Ambas | Sem resistores série nas linhas SPI | Netlist direta; datasheet RA-02 recomenda 10–100 Ω | Overshoot/EMI | 22–33 Ω em SCK/MOSI/NSS |
| H-12 | SMD | Q1 dissipa 2,83 W a 8 A com Vgs 3,23 V; TO-220 sem dissipador | M5; datasheet IRLZ44N | Aquecimento; falha em stuck-on | MOSFET logic-level 2,5 V ou gate driver; verificar SOA |
| H-13 | PTH | J10 (buzzer) sob o DevKit | J10 `(192,25,106,29)`; A1 courtyard `x=179–208,y=100,5–151,7`; render | Conector inacessível para plugar | Mover J10 para fora do courtyard; rerotear |

---

## 7. Achados MEDIUM

| ID | Placa | Achado | Evidência | Impacto | Recomendação |
|---|---|---|---|---|---|
| M-01 | Ambas | Logo de cobre flutuante na B.Cu (`G***`, sem net); na PTH um fica sob o RA-02 | Footprint `LOGO` B.Cu, `connected_nets` vazio | Acoplamento/EMC; possível detune do RF | Conectar ao GND ou manter só serigrafia |
| M-02 | SMD | Q4 com `attr smd` e pads THT | Footprint file; DRC `footprint_type_mismatch` | Classificação errada no CPL | `attr through_hole` |
| M-03 | Ambas | 0 fiduciais e 0 test points | FD-001/TE-001 | PnP/ICT | 3 fiduciais por face + TPs |
| M-04 | Ambas | BOM/CPL de variante única: inclui peças das duas estações; Q4 ausente | BOM/CPL; INSTALL | Montagem errada/custo | Gerar 2 BOMs/CPLs (comando/ignição) |
| M-05 | PTH | H1–H4 fora do esquemático (4 paridade) | DRC `extra_footprint` | Paridade/DRC | Adicionar mounting holes ao esquema ou waiver |
| M-06 | SMD | 4 erros de clearance (0,169 mm em Q2-B; 0,4305 mm em Q1-D) somem no refill (zona stale) | DRC normal 92 vs refill 88 | Se fabricar sem refill, clearance <0,2 mm | Refill + save + DRC antes do gerber |
| M-07 | Ambas | 7 labels isolados (EXP_A/B/C, ADC1/2, EXP1/2) | ERC `isolated_pin_label` | Parece wiring inacabado; EXP_C é GPIO15 (strapping) | Documentar/waiver ou remover; cuidado com GPIO15 |
| M-08 | Ambas | Base do Q4/Q3 sem pull-down (só R3 470 Ω) | Netlist `Net-(Q4-B)` / `Net-(Q3-B)` | Chirp no boot | 10 kΩ base-emitter |
| M-09 | Ambas | I2C sem pull-ups na placa; depende do módulo OLED | PU-001; firmware 100 kHz; M8 | OLED não funciona se o módulo não tiver 4,7 k | Verificar módulo ou adicionar 4,7 k |
| M-10 | Ambas | Sem ESD/filtro no chicote do botão/OLED | IO-001; netlist | Ruído/ESD | RC/TVS |
| M-11 | Ambas | Gaps de retorno: SMD RELE_IN 33%, Q2-B 59%; PTH GATE_2/BUZZ/RESET/MOSI 71–78%; SPI 70–86% | GP-001 | EMI/crosstalk | Revisar retorno/stitching; não é blocker |
| M-12 | Ambas | Q2 base 11,5 mA no GPIO13 (limite ~12 mA); R6 220 Ω superdimensionado | M3; firmware | Stress do GPIO | R6 1 kΩ |
| M-13 | Ambas | Buzzer sem flyback (se magnético) | Netlist; M7 | Q4 pode avariar | Verificar tipo; diodo se bobina |

---

## 8. Achados LOW / INFO

- **L-01** Serigrafia: 92/119 violações, a maioria do logo `G***` em B.Silkscreen e
  referências sobre pads. Cosmético; JLCPCB clipa. Triar antes de tratar como erro.
- **L-02** `lib_footprint_mismatch` 28 na PTH e 1 na SMD: as cópias na biblioteca
  divergem da placa. Manutenção, não elétrico.
- **L-03** ERC `lib_symbol_issues`: biblioteca `ignitor` não encontrada no caminho
  com acento (`Área de Trabalho`); símbolos R3 `1k` vs 470 colocado. Abrir o
  esquema em outra máquina pode mostrar símbolos faltando.
- **L-04** SS-001 "sourcing blocker" (5/24 ou 0/22 MPN) é **falso positivo** para
  JLCPCB: os SMD têm LCSC no BOM. Para montagem JLCPCB, o que falta é o Q4 e os
  passivos sem LCSC.
- **L-05** `ENCLOSURES/INSTALL` chamam J8 de "ENDSTOP/SW" e J2/J3 de
  "COM_BT/NO_BT" (são botão, não contato de relé). Risco de montagem errada.
- **L-06** Stackup 2 camadas sem plano de referência dedicado (SU-001). Informativo.
- **L-07** Ressonância de cavidade em 897 MHz; 2º harmônico do LoRa (866 MHz) próximo.
  Informativo.
- **L-08** A placa "SMD" tem 13 SMD + 16 THT. Para JLCPCB, é montagem mista/THT,
  não SMD puro.
- **L-09** PTH é 100% THT; CPL de THT não é usado pela linha SMT da JLCPCB.

---

## 9. Falsos positivos e correções de premissa

| Item | O que o analisador/discurso dizia | O que a verificação mostrou |
|---|---|---|
| 4 erros de clearance SMD | "Risco de curto/falha de fabricação" | **Zona stale**: somem com `--refill-zones`; a PCB armazenada tem o fill antigo. Ação: refill, não rerote. |
| Q4 com pinout trocado | "C/B/E pode estar trocado" | **Pinout correto**: símbolo CBE, footprint BC337-25 com pad 1=C. O problema real é **DNP/BOM**, não o pinout. |
| Pacote SMD com "A1 em posição antiga" | README do projeto | **A1 está correto**: CPL `(193,169, -91,945)` = centro dos pads. J7/J8/J10 também batem. O pacote só difere no **fill do F.Cu** e no **Q4 ausente**. |
| Pacote PTH "antigo" | README do projeto | **PTH está atual**: drill, F_Cu e B_Cu idênticos ao export novo. O README está errado. |
| IRLZ44N "não avalanche-rated" | Plano inicial | **Tem E_AS** no datasheet (gráfico de avalanche). Ainda assim, avalanche repetida não é recomendada; TVS é boa prática. |
| GP-005 "3 ground domains" | "Split de ground" | São **GND, GND_RELAY e GNDBUZZ** — retornos chaveados intencionais, não split analógico/digital. Falso positivo da regra. |
| IO-001 J12/J9 "ferrite bead" | "Adicionar ferrite" | Ferrite satura com 8 A. Para a saída de ignição, o correto é **TVS/snubber**, não ferrite. |
| SS-001 MPN coverage | "Board is not pre-fab ready" | Falso positivo para JLCPCB: os SMD têm LCSC. O bloqueio real é o **Q4 fora do BOM/CPL**. |

---

## 10. Base de verificação

### Verificado contra datasheet

- **RA-02**: pinout 1–16 (GND, GND, 3.3V, RESET, DIO0–5, GND, SCK, MISO, MOSI,
  NSS, GND) confere exatamente com a tabela do datasheet V1.1 (p. 10). Tensão
  2,7–3,6 V; TX 105 mA; antena IPEX; recomendação de ESD no 3,3 V e 10–100 Ω
  nas linhas de IO (p. 13).
- **DOIT ESP32 DevKit V1**: mapa de GPIO confere com o pinout oficial
  (GPIO4=NSS, GPIO16=RESET, GPIO17=DIO0, GPIO18/19/23=SPI, GPIO21/22=I2C,
  GPIO12=LED_COUNT/MTDI, GPIO13=GATE_1/MTMS, GPIO14=BUZZ). A ordem física dos
  30 pinos do header não foi conferida contra desenho mecânico — só o mapa lógico.
- **IRLZ44N**: TO-220 GDS (1=G, 2=D, 3=S); Vds 55 V; Rds(on) ~0,022 Ω;
  E_AS presente.
- **SS34**: 40 V, 3 A, Vf 0,60 V máx @3 A; polaridade K/A confere.

### Verificado por consistência interna (não datasheet)

- **Q2 S8050**: EBC no TO-92_Inline; convenção comum, mas **sem PDF no repo**.
- **Q4/Q3 BC337**: CBE; símbolo e footprint EasyEDA "BC337-25" concordam; **sem
  PDF local** (URL no símbolo).
- **1N5818**: DO-41, 30 V/1 A; **sem PDF local**.
- **Módulo relé 5 V**: sem modelo/datasheet; comportamento do IN em 3,3 V é
  **não verificado**.
- **Buzzer**: tipo (magnético vs piezo) **não verificado**.
- **Módulo OLED**: pull-ups **não verificados**.

### O que não foi verificado

- Lifecycle/obsolescência (sem MPN/rede).
- Térmico transiente do Q1 (modelo não inclui massa térmica).
- Indutância real do chicote de ignição.
- Altura/standoff real da caixa e do soquete do DevKit.
- Comportamento do módulo relé em 3,3 V e back-powering.
- EMC de pré-compliance (sem câmara/ensaio).
- Integridade de sinal em 433 MHz (sem VNA).

---

## 11. Delta vs análise de 2026-10-15

- **SMD**: +Q4 BC337, +R3 470, −J6 NO_RELE, −J9 SKIB; Q2 passou de IRLZ44N
  (TO-220) para S8050 (TO-92); R4/R6 220R→220ohm. Mudança **major**.
- **PTH**: +Q3 BC337, +R5 10k, +J9 terminal, +R1/R7; −R9/R10/R11, −J12 EXP,
  −D2; R3 220→470; R4 10k→220. Mudança **major**.
- As análises antigas **não são comparáveis 1:1**; os achados de EMC antigos
  foram substituídos pelos runs novos. O que permaneceu: falta de desacoplamento
  no RA-02, gaps de retorno e ausência de ESD.

---

## 12. Ordem sugerida de correção (fase separada)

1. **Segurança/montagem**: Q4 DNP, furos M3, LEDs/J10 sob o DevKit, J8 1–3.
2. **Robustez elétrica**: fusível/polaridade, TVS na ignição, level shifter do
   relé, pull-ups NSS/RESET, pull-down Q4.
3. **EMC**: 10 µF+100 nF no U1, vias de costura, remoção de ilhas, logo ao GND,
   séries SPI, TVS nos conectores.
4. **DFM**: refill, corrigir attr do Q4, regenerar BOM/CPL (2 variantes),
   fiduciais/test points, H1–H4 no esquema.
5. **Documentação**: corrigir README/ESTADO (CPL do A1 e pacote PTH).

Cada correção deve virar um commit pequeno, com DRC antes/depois e refill
explícito.

---

## 13. Anexos

- `baseline/baseline.md` — hashes e git status.
- `baseline/drc_summary.md` — contagem por regra (normal/strict).
- `baseline/findings_*.md` — findings completos dos analisadores.
- `reports/erc_*.json`, `reports/drc_*.json` — ERC/DRC.
- `analysis/<placa>/2026-11-11_1603/` — schematic, pcb, cross, emc, thermal,
  gerber, spice, parasitics.
- `renders/*.png` — top/bottom 3D.
- `fresh/` — gerbers/drill exportados da PCB atual para comparação.
- `strict/`, `mirror_strict/` — cópias com regras strict.

Todos em `C:\Users\italo\AppData\Local\Temp\opencode\ignitor-audit-2026-11-11\`.
Cópia durável dos principais artefatos (baseline, DRC/ERC, findings, renders,
SPICE) em `docs/revisao/evidencias/2026-11-11/`.
O issue register está em `docs/revisao/2026-11-11_issue-register.csv`.
