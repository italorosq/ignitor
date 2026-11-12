# Resultados

LTspice 26.1.1, 2026-11-04. Valores dos decks `smd/` e `pth/`; logs em
`results/`.

| Módulo | Métrica | SMD | PTH |
| --- | --- | --- | --- |
| M1 | V(vin) mínimo @5,0 V | 4,60 V | 4,65 V |
| M1 | D1: Vf / Pd | 0,373 V / 63 mW (SS34) | 0,312 V / 53 mW (1N5818) |
| M1 | V(3V3) | 3,30 V | 3,30 V |
| M2 | Corrente reversa | 0,2 µA | 31,7 µA |
| M3 | Q2: Ib / Ic / Vce | 11,5 mA / 51 mA / 43 mV | idem |
| M3 | Q2: fuga OFF | 5 pA | idem |
| M4 | GPIO32 afundando IN | 8,07 / 4,13 / 3,57 mA | idem |
| M5 | Q1 em 8,4 V | 8,04 A; Vds 0,353 V; 2,83 W | idem |
| M6 | LEDs | 6,03 mA por canal | idem |
| M7 | Q4: Ib / Ic / Vce | 5,47 mA / 20–62 mA / 15–45 mV | idem |
| M8 | tr I2C 2,2k/50p | 242 ns | idem |
| M8 | tr I2C 4,7k/50p | 516 ns | idem |
| M9 | dip 3V3 sem/100n/10u | 146 / 111 / 14 mV | idem |
| M10 | SPI 1 MHz | 3,518 V / −0,218 V | idem |

## Sistema completo da ignição

Deck `smd/m12_sistema_ignicao.cir`: Q2 liga em 1 s, contato do relé fecha em
2,005 s, Q1 liga em 2,01 s por 2 s, Q1 desliga em 4,01 s, contato abre em
4,025 s e Q2 desliga em 4,1 s.

| Métrica | Resultado |
| --- | --- |
| Corrente antes do disparo | 1 µA |
| Corrente durante a janela | **7,34 A** |
| Corrente depois do disparo | 1 µA |
| Vds do Q1 | 0,319 V |
| Dissipação do Q1 | 2,34 W |
| Corrente da bobina do relé | 69,2 mA |
| Vce do Q2 | 52,9 mV |
| Queda no rail 5 V | 7 mV |
| Pico de Vds no desligamento | 8,4 V |

A sequência do firmware (relé antes do Q1, Q1 antes de abrir o relé) não deixa
corrente passar antes da janela nem depois. O contato do relé foi modelado como
chave comportamental com 50 mΩ; a bobina e o flyback foram modelados como R+L.

## Pontos de atenção

- **M3**: o Q2 é S8050 (NPN), não MOSFET. O modelo antigo de IRLZ44N não vale.
- **M7**: o buzzer é chaveado pelo Q4 BC337. O GPIO14 fornece só 5,5 mA de base;
  o antigo problema de 41 mA no pino não existe.
- **M8**: a 400 kHz, só 2,2 k/50 pF passa. Com 4,7 k típico, use 100 kHz.
- **M9**: 10 µF + 100 nF perto do RA-02 derrubam o dip de 146 mV para 14 mV.
- **M5**: o Q1 tem de ficar no lado de baixo. Se a fiação colocar o source no
  lado alto, ele vira source-follower e a carga não recebe os 8 A.

## Limitações

- `irlz44n.lib` é um ajuste VDMOS ao datasheet, não o modelo oficial.
- `s8050.lib` e `bc337.lib` são modelos públicos.
- Relé e buzzer são equivalentes R/L.
- LDO é comportamental.
- Parasitários de I2C/SPI são estimados.
