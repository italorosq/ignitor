# Caixas do Ignitor — requisitos e montagem

> Primeira versão em OpenSCAD. Modelo em
> `hardware/3d_models/openscad/`. Este documento registra as decisões,
> as interfaces e o que ainda precisa ser confirmado.

## 1. Escopo

Duas caixas para a **mesma placa SMD de 75 × 75 mm** (rev 2.4):

| Caixa | Dimensão externa | IP alvo | Conteúdo |
|---|---|---|---|
| **Comando** | **150 × 90 × 80 mm** | IP54 | Console com frente inclinada ~18°: placa + 2× 18650 (2P) à esquerda (pega), OLED/LEDs/falante na rampa, botão de hold 22 mm no topo-direita, switch mantido no topo-esquerda, micro-USB + SMA + tripé |
| **Ignição** | **150 × 110 × 75 mm** | IP65 / IPX5 | Placa + 2× 18650 (2P) + **3S2P (6× 18650)** + módulo 2 relés + RBF/endstop + falante + switch + saída de ignição + SMA + respiro |

A caixa de ignição assume o **3S2P dobrado (130 × 54 × 18 mm)**. Com suporte de
6 células (195 × 36 mm), a caixa precisa de **205 × 105 × 75 mm**.

Não faz parte deste escopo: redesenho elétrico, firmware e certificação do
circuito de disparo.

## 2. Placa e interfaces

Placa: 75 × 75 × 1,6 mm; furos M3 em **67 × 67 mm** (4 mm das bordas);
altura máxima **Q1 ≈ 28,5 mm**.

| Conector | Netlist / valor | Função | Comando | Ignição |
|---|---|---|---|---|
| `J1` | `5v_BUCK`, 2 pinos | Entrada 5 V (2P + boost/buck) | sim | sim |
| `J2/J3` | `COM_BT` / `NO_BT` | Botão momentâneo para GND | sim | não |
| `J4/J5` | `LED_BUTTON+/-` | LED do botão | sim | não |
| `J6` | `NO_RELE` | NO do relé → dreno do Q1 | não | sim |
| `J7` | `RELAY`, 3 pinos | 5 V, IN, GND chaveado do módulo relé | não | sim |
| `J8` | `ENDSTOP/SW`, 3 pinos | Switch 5 V da bobina; pino 2 NC | não | sim |
| `J9` | `SKIB` | Source do Q1 → ignitor | não | sim |
| `J10` | `BUZZER`, 2 pinos | Falante (via Q3) | sim | interno |
| `J11` | `OLED`, 4 pinos | OLED I2C 3,3 V | sim | interno |
| `A1` | DevKit V1 | **micro-USB**, não USB-C | sim | sem USB |
| `D3/D4` | LEDs 5 mm | Status/count; no comando vão para o painel | sim | não |
| EXP | `EXP1/EXP2/EXP_A/B/C` | Sem conector; fora do escopo | não | não |

### 2.1 Correções importantes

1. **`J6` e `J9` não são uma saída de 2 pinos.** O laço é:
   `BAT+ → relé COM/NO → J6 → Q1 D→S → J9 → ignitor → BAT−`.
   A saída é **J9 + BAT−**; ligar o bulkhead entre J6 e J9 coloca o ignitor em
   paralelo com Q1 e burla o Q1.
2. **`J6/J9` são pin headers 2,54 mm de 1 pino**, não conectores de 8 A.
   Soldar **16 AWG direto nos pads** (ou faston) e aliviar a tração.
3. **`J1` é a alimentação; `J8` não é.** `J8` é o switch de 5 V da bobina do
   relé (pino 1 `5V_RELE_S`, pino 3 `+5V_RELE`, pino 2 NC). É o ponto do
   **endstop/RBF/ARM**.
4. **O USB do DevKit é micro-USB**, não USB-C. O painel do comando usa
   feedthrough micro-USB para programação e um USB-C separado para carga.
5. **O falante não é um buzzer passivo.** O J10/Q3 chaveia DC; para tom, o
   firmware precisa gerar PWM no GPIO14. Sem PWM, o falante só estala.
6. **O GND do módulo relé é chaveado pelo Q2** (`GND_RELAY`). O módulo precisa
   ficar em **standoffs de nylon**; suporte metálico liga o GND ao chassi e
   burla o interlock.

## 3. Baterias

### Comando
- **2× 18650 em 2P** (3,7 V) sob a placa; **TP4056 + boost 5 V**.
- O switch da imagem corta o **+ da bateria antes do boost**.
- Carga por USB-C de painel; programação por micro-USB.

### Ignição
- **2× 18650 em 2P** para a eletrônica (5 V), no mesmo esquema.
- **3S2P (6× 18650)** para o SKIB, em compartimento separado na porta inferior:
  - BMS 3S 20 A com balanceamento;
  - fusível 10 A no + do pack;
  - XT90 para desconexão;
  - carga por M12 selado (ou pack removível);
  - respiro ePTFE no compartimento.
- **O switch da imagem corta apenas a 2P antes do regulador.** A 3S2P precisa
  de um **disconnect próprio** (XT90/key). O RBF/endstop corta a bobina do
  relé; o contato do relé é quem abre a 3S2P.
- O compartimento da 3S2P tem um **rebaixo frontal** para o módulo de relé
  encostar no fundo; ele **não é vedação de gás**. O respiro ePTFE é para
  equalização de pressão, não para venting de célula. A 3S2P deve usar células
  protegidas, BMS e fusível, e ser carregada fora ou por conector selado.

### Star ground
- O retorno de 8 A do ignitor vai **direto ao BAT−**, não pelo plano de GND da
  PCB.
- O GND da placa encontra o BAT− em **um único ponto** (Wago/terminal).
- O GND do módulo relé é o **GND chaveado** (Q2), separado do GND de potência.

## 4. RBF e endstop

- **Endstop interno:** reed switch **NC** atrás do bolsão frontal.
- **RBF magnético:** flag vermelha com ímã, encaixada no bolsão; sem furo
  passante.
- **RBF inserido** → reed abre → bobina do relé sem alimentação → **seguro**.
- **RBF removido** → reed fecha → sistema pode armar.
- O reed fica em série com o `J8` e com o switch ARM.
- Alternativa mecânica: pino pull-pin com bucha selada e O-ring.
- **Não há feedback de firmware**: o `J8` não é GPIO; é interlock de hardware.

> **Botão de hold:** o botão de 5 s é momentâneo e fica no **topo-direita** do
> comando, com **22 mm**, capa **côncava**, mola leve e **anel de guarda** de
> 4 mm. O polegar apoia e segura sem escorregar; soltar aborta a contagem. O
> switch da imagem é **mantido** e fica no **topo-esquerda**; ele não é o hold.

## 5. Módulos externos e modularidade

| Módulo | Envelope | Onde | Fixação |
|---|---|---|---|
| Módulo 2 relés | 50 × 40 × 19 mm | ignição, frente-esquerda | nylon, perto de J6/J9 |
| Reed/RBF | 20 × 10 × 5 mm | ignição, frente, sobre a 2P | suporte impresso |
| Falante 36 mm | Ø36 × 12 mm | comando (grade) / ignição (membrana) | tampa |
| OLED 0,96" | 27 × 27 × 4 mm | comando, frente | 4× M2 |
| Botão de hold | Ø22 × 25 mm | comando, topo-direita | porca + anel de guarda |
| Switch guarded | 30 × 30 × 45 mm | comando/ignição, topo | porca + capa |
| Bateria 2P | 65 × 36 × 18 mm | ambas, sob a placa | berço |
| Bateria 3S2P | 130 × 54 × 18 mm | ignição, porta | compartimento |

O modelo 3D usa **envelopes**; o ajuste fino é feito com o componente na mão.
**Imprimir o cupom e o template 1:1 do painel antes da caixa completa.**

## 6. Vedações

- **Gaxeta:** cordão de silicone Ø2,5 mm; canal **3,5 × 1,9 mm**; compressão
  **24%**; fill ratio **≈74%**.
- **Parafusos:** M3 A4, **insertos de latão cegos**; **arruelas de vedação
  M3** sob a cabeça; torque **0,4–0,5 N·m**, aperto em cruz.
- **Tampa:** groove no corpo; tampa plana com lip; parafusos dentro da linha
  da gaxeta, mas com arruela de vedação.
- **Porta inferior:** tampa completa com gaxeta; parafusos com arruela.
- **Penetrações da ignição:** saída Deutsch (esquerda), power M12 (traseira),
  carga M12 (direita), respiro ePTFE (direita), SMA (traseira), RBF (frente),
  switch (topo), membrana acústica (topo).
- **Nenhum furo passante** além dessas penetrações e das portas.
- **IP:** comando **IP54**; ignição **IP65**. **Não declarar IP67** sem caixa
  comercial ou potted.

## 7. Impressão

- **Perfil:** 0,4 mm; 0,2 mm layer; 5 perímetros; 35% infill; 5 topo/base;
  brim 5 mm; sem suportes; costura na traseira.
- **Corpo:** topo para cima.
- **Tampa:** invertida, lip para cima.
- **Porta:** lado interno para cima.
- **Material:** PETG no protótipo; ASA no final. ASA exige enclosure/ventilação;
  sem enclosure, PETG + verniz UV.
- **Impressoras:** Kobra 4 Combo (corpo da ignição) e Ender 3 V3 SE
  (comando, tampas, portas, cupons).
- **Insertos:** ferro de solda ~250 °C; furo Ø4,2 × 7; boss Ø7.
- **Cupons:** gaxeta e inserto **antes** da caixa completa.

## 8. Ensaios

| Ensaio | Condição | Critério |
|---|---|---|
| **Gaxeta** | cupom + cordão 2,5 mm | sem vazamento; compressão 20–30% |
| **Inserto** | M3, torque 0,5 N·m | sem arrancar/espanar |
| **IPX5** | jato 6,3 mm, 12,5 L/min, 3 m, 3 min | sem água no interior |
| **Pressão** | 0,3 bar pelo respiro | queda < 10% em 60 s |
| **Térmico** | relé + boost 30 min, 25 °C | interno < 60 °C; célula < 45 °C |
| **Queda** | 1 m em concreto, dummy | sem trinca, tampa fechada |
| **LoRa** | 10 m e 100 m, caixa fechada | RSSI/PER registrados |
| **Elétrico** | polaridade, sequência, isolação | sem bypass de Q1; relé só com Q2 + RBF |
| **Fusível** | 8 A dummy | abre no tempo esperado; sem aquecimento |

Registrar em `hardware/3d_models/openscad/TESTES.md`.

## 9. Pendências

1. **2P × 2S:** o modelo usa 2P (65 × 36) sob a placa. 2S (130 × 18) não cabe
   sob a placa de 75 mm; exigiria um berço lateral e uma caixa maior.
2. **3S2P dobrado × suporte 6 células:** o modelo usa 130 × 54; o suporte
   aumenta a ignição para 205 × 105 × 75 mm.
3. **Relé 2 canais:** definir 2 polos do SKIB ou 1 reserva; IN2 e JD-VCC.
4. **Falante:** drive direto no Q3 ou PAM8403; firmware com PWM.
5. **J6/J9:** confirmar o laço e o Q1 no lado alto; revisar o driver antes do
   teste de 8 A.
6. **Disconnect da 3S2P:** XT90/key separado ou switch de 2 polos.
7. **RBF:** magnético (modelo atual) ou pino mecânico.
8. **IP:** comando IP54 e ignição IP65; confirmar.

## 10. Segurança

O subsistema de acionamento do ignitor (SKIB) está **fora do escopo funcional**
desta auditoria e depende de revisão independente por profissional qualificado.
A caixa não certifica o circuito, não substitui procedimento de armar e não
torna o sistema à prova de falhas. O RBF e o endstop são interlock de hardware;
o firmware e o operador continuam sendo parte da cadeia de segurança.
