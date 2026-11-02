# RESULTADOS — Simulação por módulos (LTspice 26.1.1)

Execução: 2026-10-15. Bancadas: `smd/` e `pth/` (logs em `results/smd|pth|skill_*`).
Valores extraídos via `.meas` (logs originais preservados).

## Resumo

| Módulo | Métrica | SMD | PTH | Critério | Veredito |
|---|---|---|---|---|---|
| M1 entrada+LDO | V(vin) mín. | **4,597 V** | **4,270 V** | ≥ ~4,0 V (LDO) | SMD OK folgado · PTH OK com margem de ~0,27 V |
| M1 | Vf do diodo (méd.) / Pd | 0,373 V / 63 mW (SS34) | 0,695 V / 117 mW (1N5400) | ratings 3 A/40-50 V | OK/OK |
| M1 | V(3V3) sob burst | 3,300 V | 3,300 V | ≥ 3,0 V | OK |
| M2 backfeed | I reversa pelo diodo | 0,2 µA | 10 nA | ~0 | OK |
| M2 | USB sozinho alimenta DevKit | 125 mA @3,3 V | 125 mA | operar a partir do USB | OK |
| M3 chave relé | Vgs ON / Vgs OFF | 3,229 V / ~0 | idem | ≥3 V / <0,1 V | OK |
| M3 | Vds(on) @ ~52 mA méd. | 2,09 mV (Rds ≈ 40 mΩ) | idem | <100 mV | OK |
| M3 | Pd / fuga OFF | 0,11 mW / 1 µA | idem | — | OK |
| M4 IN do relé | I no GPIO32 (Rp 1k/4,7k/10k) | 8,07 / 4,13 / 3,57 mA | idem | ≤20 mA | OK |
| M5 ignição | I (6/7,4/8,4 V) | 5,75 / 7,09 / **8,04 A** | idem | ~8 A @8,4 V | OK (bate com o “8 A de pulso”) |
| M5 | Rds efetivo @Vgs 3,23 V | 42,7–43,8 mΩ | idem | SOA p/ 2 s | OK (P ≤ 2,83 W; E ≤ 5,7 J; sem dissipador) |
| M6 LEDs | I por canal (220 Ω) | 6,03 mA | 6,03 mA | 2–8 mA | OK |
| M6 | canal SKIB (10k, só SMD) | 0,151 mA | — | ver nota | canal **removido do projeto em 15/10** (J9 = Q1.S, laço de ignição) |
| M7 buzzer | I no GPIO14 (R 80/120/180/250 Ω) | **41,2 / 27,5** / 18,3 / 13,2 mA | idem | ≤20 mA prático (40 abs) | ⚠ escolher buzzer que puxe ≤20 mA @3,3 V |
| M8 I2C | tr (2,2k/50p) | **242 ns** | idem | ≤300 ns (400 kHz) | OK nesse ponto |
| M8 | tr (4,7k/50p · 4,7k/100p) | 516 ns · 1,03 µs | idem | 300 ns / 1000 ns | ✗ p/ 400 kHz · ✗/marginal p/ 100 kHz |
| M8 | tr (10k/100p · 10k/200p) | 2,20 µs · 4,40 µs | idem | idem | ✗ |
| M9 droop 3V3 | dip na entrada do U1 (sem/100n/10µ) | 146 / 111 / **14 mV** | idem | < ~150 mV | OK; decap local melhora ~10× |
| M10 SPI 1 MHz | pico máx/mín no receptor | 3,518 V / −0,218 V | 3,534 V / −0,234 V | VIH 2,31 V; <3,6 V | OK |
| M11 (skill) | Vth dos FETs genéricos (Q1/Q2) | 1,5417 V | 1,5417 V | 1,0–2,0 V (IRLZ44N) | OK |
| M11 | Z PDN do rail 5V (SMD) | 15,2 mΩ @100 kHz; 5,3 mΩ @1 MHz; mín. 3,9 mΩ | n/d (skill não detectou decoupling na PTH) | baixo | OK |

## Achados acionáveis

1. **Buzzer (M7) — atenção na seleção de componente.** Sem transistor, o GPIO14
   fornece toda a corrente. Buzzer com equivalente DC de 80 Ω puxa **41 mA**
   (acima do máximo absoluto de 40 mA do ESP32); ≥180 Ω fica em ~18 mA (seguro).
   **Comprar buzzer ativo 3 V com consumo ≤20 mA @3,3 V** (ou prever transistor na próxima revisão).
2. **I2C do OLED (M8) — firmware em 400 kHz.** Com pull-ups típicos de módulo
   (4,7k) o tempo de subida fica em 0,5–2,2 µs — acima dos 300 ns do Fast-mode.
   Opções: baixar o firmware para 100 kHz (atende com 4,7k/50p), ou garantir
   pull-ups de 2,2k (242 ns @50 pF). Não bloqueia a fabricação da placa.
3. **PTH com 1N5400 (M1) — headroom do LDO.** O diodo consome ~0,7 V; a margem
   cai para ~0,27 V (contra ~0,60 V na SMD). Com buck em 4,9 V a margem vira ~50 mV;
   se o firmware algum dia usar WiFi (burst ~500 mA) a PTH não fecha. Recomendo
   conferir a tensão real do buck ou considerar SS34/1N5822 na PTH.
4. **Decap local no U1 (M9).** O dip de TX cai de 146 mV (sem) para 14 mV (10 µF local) —
   mantém-se a recomendação de 100 n + 10 µ junto ao RA-02/OLED na próxima revisão.
5. **SKIB (SMD) — resolvido em 15/10.** O canal antigo (J9→D2 LED→R3 10k→GND, ~0,15 mA)
   foi removido do projeto; agora `Net-(Q1-S)` = {J9.1, Q1.3} — o J9 é o terminal do
   ignitor no laço NO→J6→Q1→J9→ignitor (ver relatório de revisão).

## Notas de método

- M1/M2 incluem o LDO comportamental do DevKit com dropout dependente de corrente;
  cenário conservador (sem WiFi; só LoRa TX + OLED). M2 usou o caso pior (saída do
  buck em ~0 V) para a checagem de bloqueio.
- M5 simula 20 ms do pulso de 2 s (regime) e a energia térmica é estimada a partir
  de P×2 s (TO-220 sem dissipador, ~5,7 J máx — ΔTj desprezível no pulso).
- M11: as bancadas auto-geradas pela skill usam sintaxe `ngspice` para `.meas`;
  foram adaptadas para LTspice (Vsense + FIND/WHEN) e re-executadas nativamente.
- Limitações completas dos modelos no `../README.md`.
