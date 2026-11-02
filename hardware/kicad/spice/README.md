# Simulação por módulos — Ignição SMD / PTH (LTspice)

Simulações por módulo do circuito das duas placas (mesma topologia; variantes de
parâmetros SMD/PTH), executadas com **LTspice 26.1.1** (`D:\LTspice.exe`, batch).

## Estrutura

```
spice/
├── models/            modelos usados (com fonte/aproximação em comentário)
│   ├── irlz44n.lib    VDMOS fit do datasheet Infineon (APROXIMADO)
│   ├── ss34.lib       fit datasheet SS34 (Schottky 40V/3A)
│   ├── 1n5400.lib     fit datasheet Vishay 1N5400
│   ├── led.lib        LED genérico 5mm (Vf ~1.95V)
│   ├── ldo_devkit.lib AMS1117-3.3 comportamental (dropout + quiescência)
│   └── relay_srd.lib  módulo relé SRD-05VDC (R+L da bobina)
├── smd/  m1..m10.cir  decks por módulo (SMD)
├── pth/  m1..m10.cir  decks por módulo (PTH — variantes de diodo/caps)
├── skill_circuits/    bancadas auto-geradas pela skill kicad-happy (M11, adaptadas p/ LTspice)
├── run_all.ps1        runner em lote (lança LTspice -b e aguarda o .log)
└── results/           logs (.log) de todos os decks + RESULTADOS.md
```

## Como reproduzir

```powershell
cd smd        # ou pth
powershell -ExecutionPolicy Bypass -File ..\run_all.ps1 -Dir .
```

O runner apaga `.log/.raw` antigos, executa `D:\LTspice.exe -b <deck>.cir` e
aguarda o `.log` (o LTspice 26 destaca o processo; sem polling o log sai vazio).
Resultados (`.meas`) ficam no próprio `.log`; cópias em `results/`.

## Módulos

| Deck | Tema | Critério principal |
|------|------|--------------------|
| m1_pwr | entrada 5V + diodo série + LDO do DevKit + cargas | V(3V3) ≥ 3,0 V; headroom do LDO |
| m2_backfeed | bloqueio do backfeed USB→rail pelo diodo série | I_rev ~0 |
| m3_relay_gnd | chave do GND do módulo relé (Q2, GATE_1) | Vgs≥3 V; Vds/PD baixos; OFF seguro |
| m4_relay_in | entrada IN do módulo relé (GPIO32, sink) | I_GPIO ≤ 20 mA |
| m5_ignition | saída de ignição (Q1, GATE_2, pulso 2 s) | I coerente com 8 A; SOA/energia |
| m6_leds | canais de LED (220 Ω; SKIB 10k no SMD) | 2–8 mA por canal |
| m7_buzzer | buzzer ativo direto no GPIO14 | I_GPIO ≤ 20 mA prático / 40 mA abs |
| m8_i2c | barramento I2C do OLED (sem pull-ups na placa) | tr ≤ 300 ns (400 kHz) / 1000 ns (100 kHz) |
| m9_v3v3_droop | degrau TX do RA-02 no rail 3V3 (Ltrilha) | dip < ~150 mV (qualitativo) |
| m10_spi | SPI 1 MHz com parasitários estimados da trilha | overshoot/undershoot dentro dos níveis |
| skill (m11) | bancadas auto-geradas (Vth dos FETs; PDN das caps) | Vth 1,5–2,0 V; Z(PDN) baixo |

## Limitações dos modelos

- `irlz44n.lib`: fit VDMOS a partir do datasheet — **não** é o modelo oficial
  Infineon; Rds(on) em Vgs=3,23 V (~40 mΩ no fit) é uma estimativa.
- `ldo_devkit.lib`: comportamento do AMS1117 aproximado (Vdo = 0,55 + 0,7·I).
  O modelo ativo do DevKit (proteções, chave USB) não é representado.
- Relé/buzzer/opto/e-match: modelos equivalentes simples (R/L), sem eletromecânica.
- m8: driver do GPIO modelado como chave 30 Ω; Cbus e pull-ups parametrizados.
- m9/m10: parasitários estimados (L 1 nH/mm, C 0,45 pF/mm) — não extraídos de field solver.

Resultados consolidados: `results/RESULTADOS.md`.
