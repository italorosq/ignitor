# Plano: Re-layout da pcbcnc (fabricação CNC caseira, 1 camada)

> **Status:** proposta registrada em 2026-10, **não executada**.
> O estado atual da placa CNC está em [`../ESTADO_DO_PROJETO.md`](../ESTADO_DO_PROJETO.md).
> Este documento descreve o relayout pretendido para 90×100 mm; a placa em
> `hardware/kicad/placas/ignicao_cnc/` ainda está em 50×90 mm e sem trilhas.

## Contexto

Projeto: `hardware/kicad/placas/ignicao_cnc/` (KiCad 10.0.6)
Diagnóstico do estado atual (75×80 mm, 59 footprints THT, tudo roteado só no B.Cu, 0 vias):

- **22 erros de `unconnected_items`** no DRC + 1 net não roteada (`GND_RELAY`) — segmentos que não se encontram, ilhas soltas
- **GND como 43 trilhas meandradas (276 mm)** sem barramento organizado — bagunça visual e retorno de corrente ruim
- **Paridade esquemático/PCB quebrada**: esquemático tem `Q2 IRLZ44N` (TO-220), PCB tem `Q3 S8050` (TO-92) com nets `Net-(Q3-B)` ≠ `Net-(Q2-G)`
- **Sem desacoplamento no +3V3 do Ra-02** (módulo RF) — mandamento quebrado
- Silkscreen sobreposto no canto inferior direito (`Screw_Terminal...` empilhado)
- Regras CNC já adequadas no `.kicad_pro`: trilha mín. 0,6 mm / default 1,0 mm / IGN 2,5 mm, folga 0,4 mm, furo mín. 0,3 mm, borda-cobre 0,5 mm

## Decisões do usuário

| Item | Decisão |
|---|---|
| Estratégia de cobre | **1 camada, sem plano de terra** (roteamento no B.Cu como hoje) |
| Tamanho | **90 × 100 mm** |
| Driver do relé | **Manter S8050** (PCB fica como está; esquemático volta a S8050) |
| Desacoplamento RF | **Adicionar C4 10uF THT no +3V3 perto da U1** |
| Ambiente | **Usuário fecha o KiCad** antes da execução |

## Mandamentos EMC (adaptados para camada única sem plane)

1. **GND em barramento/estrela**: espinha central de GND com trilha **2,0 mm**, roteada primeiro; cada bloco recebe um ramo curto direto ao ponto-estrela (entrada do buck J1, junto do C1 de 100uF). Nenhuma ilha de GND flutuante (DRC unconnected = 0).
2. **Loop de ignição curto e largo**: `Q1 D/S ↔ J6` em 2,5 mm, caminho mínimo; retorno GND de Q1 vai por ramal próprio de 2,0 mm à estrela (não compartilha trecho com sinais fracos).
3. **Barramento de potência curto**: `J1 → D5 → C1/C2/C3 → relé/endstop` em 2,0 mm; bulk C1 junto do buck; C2 perto da alimentação do ESP32 (VIN), C3 no ramal do relé.
4. **Desacoplamento no RF**: novo **C4 10uF** colado no par de alimentação do Ra-02 (+3V3/GND), o mais próximo do pino.
5. **Loops de gate curtos (< 30 mm)**: R3/R6 (220Ω) e R2/R4 (10k) fisicamente junto aos gates de Q2/Q1; GATE_1/GATE_2 sem corrida paralela com potência.
6. **RF**: SPI (NSS/SCK/MISO/MOSI) o mais reto possível U1↔A1, sem cruzar o corredor de ignição; módulo Ra-02 com conector IPEX virado para a borda esquerda.
7. **Sem cruzamentos cegos**: roteamento planar; onde o cruzamento for inevitável, usar ilha `JUMPER_ILHA` (pad PTH 1,8 mm / furo 0,9 mm) + fio — já é o padrão da placa (27 ilhas hoje).
8. **Cantos 45°**, sem ângulos agudos; folga cobre-borda ≥ 0,5 mm; trilha mínima respeitando 0,6 mm (nunca menor que a regra).
9. **Sinais lentos (OLED I2C, EXP, botões, LEDs)** ficam nas bordas/periferia, longe do corredor de ignição e do buck.
10. **Silkscreen limpo**: referências dentro das courtyards, sem sobreposição, marcações de polaridade (C1–C4, D3–D5, Q1/Q3, terminal J6).

## Etapas de execução

### Fase 0 — Preparação
- Confirmar que KiCad está fechado (sem `.lck`)
- Backup: `pcbcnc_pre_relayout_<data>.kicad_pcb` e `.kicad_sch` copiados para `pcbcnc/backup/`
- Ferramenta: `"C:\Program Files\KiCad\10.0\bin\python.exe"` (tem `pcbnew` 10.0.6) + `kicad-cli` do mesmo bin

### Fase 1 — Correções no esquemático (arquivos .kicad_sch)
1. **rele.kicad_sch**: trocar `Q2 IRLZ44N` (PCM_Transistor_MOSFET_AKL) por NPN S8050 (TO-92, ref **Q3**):
   - Copiar/adaptar símbolo NPN (do Device padrão do KiCad, ex. `Q_NPN`) para `hardware/kicad/shared/lib/Device.kicad_sym` se não existir na lib local
   - **Verificação de pinout**: ler o mapeamento pad→net do Q3 já colocado na PCB (é o "ground truth" que funciona) e escolher/posicionar o símbolo que reproduz esse mapeamento; conferir contra pinagem datasheet S8050 (convenção E-B-C) — documentar o resultado
   - Rewire: B → R3 (220Ω de GATE_1) + R2 (10k pulldown); C → `GND_RELAY`; E → GND; redes viram `Net-(Q3-B)` (nome que já existe na PCB)
2. **LORA.kicad_sch**: adicionar **C4 10uF_16V** (CP_Radial_D5.0mm_P2.00mm) entre +3V3 e GND junto à U1
3. Validar: `kicad-cli sch erc` + export de netlist + conferência das nets novas (`Net-(Q3-B)`, +3V3 com C4)

### Fase 2 — Geometria e posicionamento (script pcbnew no .kicad_pcb)
1. Outline novo 90×100 mm (x: 150→240, y: 100→200); furos M3 H1–H4 nos 4 cantos (inset 5 mm)
2. Corrigir nets do Q3 (B/C/E) e renomear `Net-(Q3-B)` conforme fase 1
3. **Reposicionar tudo por blocos** (script define coordenadas):
   - Topo-esquerda: U1 Ra-02 (IPEX p/ borda esquerda) + ilhas de RESET/SPI
   - Topo-centro: A1 ESP32 (antena na borda superior, como hoje)
   - Topo-direita: J1 (buck), D5, C1, C2, C3 (entrada de potência), J8 (endstop)
   - Direita: J7 (relé) + R2/R3 + Q3 (driver do relé)
   - Inferior-direito: Q1 + J6 (ignição, loop 2,5 mm curto)
   - Inferior-centro: R9/R10/R11 + D3/D4 (LEDs), J2/J3/J4/J5 (botões)
   - Esquerda: J11 (OLED), J12 (EXP), J10 (buzzer) + C4 junto da U1
   - Ilhas JMP redistribuídas conforme roteamento (fase 3)

### Fase 3 — Roteamento (script pcbnew, camada única)
1. Apagar **todas** as trilhas atuais (143 segmentos)
2. Roteador próprio (A* em grade, sem vias, larguras/folgas por classe):
   1. **Espinha GND 2,0 mm primeiro** (estrela no J1/C1) + ramos por bloco
   2. IGN (2,5 mm) → potência VIN/+5V_RELE (2,0 mm) → 5V_RELE_S (1,5 mm) → GATE_1/GATE_2 (1,0 mm) → SPI/Reset/I2C (1,0 mm) → GPIO/LED/EXP (1,0 mm)
   3. Onde não couber: inserir ilha `JUMPER_ILHA` (copiar footprint existente, atribuir net) e retomar do outro lado
3. Teardrops onde possível (recurso nativo do KiCad 10) — opcional, se barato
4. Iterar: rotear → `kicad-cli pcb drc --format json` → corrigir até **0 erros / 0 avisos** (mantendo as verificações atualmente ignoradas)

### Fase 4 — Silkscreen
- Reposicionar referências sem sobreposição; esconder values redundantes; marcar polaridades e labels dos conectores (J6 = ignição, J7 = relé, J12 = EXP…)

### Fase 5 — Validação
- DRC 0 erros/avisos (com as exclusões atuais) e paridade esquemático/PCB limpa
- ERC limpo no esquemático
- `analyze_pcb.py` re-executado: `routing_complete: true`
- Checagens de "mandamentos" no resultado final: distância de desacoplamento (C1↔J1, C4↔U1, C2↔A1), comprimento dos SPI/gates, larguras de GND/IGN, cruzamentos de IGN × sinais
- Render prévio (PDF/SVG) para inspeção visual — mostro o resultado antes de exportar

### Fase 6 — Saída CNC
- Regenerar `cnc/` com o mesmo conjunto atual (espelhando as configurações existentes): `B_Cu.gbl`, `Edge_Cuts.gm1`/`.dxf`, `pcbcnc.drl`, `job.gbrjob`, `pcbcnc-preview.pdf`
- Reavaliar o DRC exportado (`cnc/drc.json`)

## Critérios de aceite
- DRC/ERC: 0 erros e 0 avisos (com as exclusões já definidas no projeto)
- Paridade esquemático↔PCB sem avisos (Q3 S8050 consistente nos dois lados, C4 presente nos dois)
- Nenhuma net quebrada; GND 100% contínuo via barramento (sem ilhas flutuantes)
- Trilhas: GND ≥ 2,0 mm; IGN 2,5 mm; potência 2,0 mm; sinal 1,0 mm (mín 0,6 mm); folga 0,4 mm; furos ≥ 0,9 mm nas ilhas
- Preview visual aprovado pelo usuário

## Riscos / observações
- Edição de s-expr do esquemático por script exige cuidado com geometria de pinos — mitigado por ERC + netlist + conferência de pinagem do S8050
- Sem plane de terra, a qualidade do GND depende do barramento — vou priorizar GND primeiro no roteador e usar o mínimo de ilhas para GND
- Arquivos em OneDrive: trabalhar direto no caminho real após backup (evita divergência de cópia)
- Test points: 0/42 nets — aceito (placa THT, quase todo pino é acessível)
