# Simulações SPICE

Decks por módulo das placas SMD e PTH, rodados no LTspice 26.1.1 em batch.

## Estrutura

```text
spice/
├── models/       irlz44n, ss34, 1n5818, s8050, bc337, led, ldo e relé
├── smd/          m1..m10
├── pth/          m1..m10
├── run_all.ps1   roda todos os decks de uma pasta
└── results/      logs e RESULTADOS.md
```

## Como rodar

```powershell
cd smd        # ou pth
powershell -ExecutionPolicy Bypass -File ..\run_all.ps1 -Dir .
```

Os resultados (`.meas`) ficam no `.log`.

## Decks

| Deck | Tema | Critério |
| --- | --- | --- |
| m1_pwr | 5 V + D1 + LDO do DevKit + cargas | V(3V3) ≥ 3,0 V |
| m2_backfeed | bloqueio USB → rail por D1 | I reversa ~0 |
| m3_relay_gnd | Q2 S8050 no GND do relé | Vce baixo, OFF seguro |
| m4_relay_in | IN do relé afundado pelo GPIO32 | ≤ 20 mA |
| m5_ignition | Q1 IRLZ44N, pulso de 2 s | ~8 A em 8,4 V |
| m6_leds | LEDs de status, contagem e botão | 2–8 mA por canal |
| m7_buzzer | Q4 BC337 no buzzer | GPIO ≤ 20 mA |
| m8_i2c | I2C do OLED (só comando) | tr ≤ 300 ns a 400 kHz ou 1000 ns a 100 kHz |
| m9_v3v3_droop | degrau de TX do RA-02 | dip < ~150 mV |
| m10_spi | SPI 1 MHz | dentro dos níveis do ESP32/RA-02 |
| m12_sistema_ignicao | base completa: Q2, relé, e-match e Q1 | sem corrente antes/depois; ~7,3 A por 2 s |

## Limitações

- `irlz44n.lib` é um ajuste VDMOS ao datasheet, não o modelo oficial da Infineon.
- `s8050.lib` e `bc337.lib` são modelos Gummel-Poon públicos.
- `1n5818.lib` é o modelo padrão do LTspice.
- Relé e buzzer são equivalentes R/L; não há eletromecânica.
- LDO é comportamental; as proteções do DevKit não estão no modelo.
- m8/m9/m10 usam parasitários estimados, não extraídos de field solver.
