# Caixas

Duas caixas para a mesma PCB. A placa é comum; mudam a população e os furos de
painel.

| Caixa | Tamanho externo | Conteúdo |
| --- | --- | --- |
| Comando | 150 × 90 × 80 mm | placa, 2×18650, OLED, botão, LEDs, buzzer, SMA |
| Ignição | 150 × 110 × 75 mm | placa, 2×18650, relé, RBF, buzzer, saída de ignição, SMA |

## Placa

- SMD: 78,8 × 57,3 × 1,6 mm. **Sem furos M3** na revisão atual; a caixa precisa
  de suportes ou a placa precisa ganhar os furos.
- PTH: 75 × 80 × 1,6 mm, com quatro furos M3.
- Altura maior: Q1 (TO-220), cerca de 28 mm.

## Painéis

| Item | Comando | Ignição |
| --- | --- | --- |
| OLED J11 | sim | não |
| Botão J2/J3 | sim | não |
| LED do botão J4/J5 | sim | não |
| Relé J7/J8 | não | sim |
| Saída J12/J9 | não | sim |
| Buzzer J10 | sim | sim |
| SMA do LoRa | sim | sim |
| USB do DevKit | sim (micro-USB) | não |

## Ignição

- Bateria da eletrônica: 2×18650 em paralelo (1S) + boost 5 V.
- Bateria do laço: 2S (6,0 a 8,4 V), em compartimento separado.
- J8 é o RBF/ARM: feche os pinos 1–3 para alimentar a bobina do relé.
- A saída é J12 (SMD) ou J9 (PTH): dreno do Q1 e retorno para BAT−.
- O módulo relé fica em standoffs de nylon; o GND do módulo é chaveado pelo Q2.

## Comando

- Botão de hold de 10 s no topo.
- OLED na frente.
- LED do botão e LEDs de status no painel.
- USB micro do DevKit para programação; USB-C separado para carga.

## Impressão

- Corpo em PETG ou ABS.
- Paredes de 2,4 mm, 4 perímetros.
- Insertos M3 nas tampas.
- Junta de silicone nas tampas da ignição.
