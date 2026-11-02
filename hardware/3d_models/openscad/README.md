# Caixas Ignitor — OpenSCAD

Modelo paramétrico das duas caixas. **Fonte de verdade:** os arquivos `.scad`.
Os `.stl` são derivados; não edite STL.

## Tamanhos

| Caixa | Externa (X × Y × Z) | Uso |
|---|---|---|
| **Comando** | **150 × 90 × 80 mm** | console com frente inclinada ~18°, 2× 18650 (2P) sob a placa à esquerda, OLED/LEDs/falante na rampa, botão de hold 22 mm no topo-direita, switch mantido no topo-esquerda, tripé |
| **Ignição** | **150 × 110 × 75 mm** | 3S2P (6× 18650) + 2P, módulo 2 relés, endstop/RBF, falante, saída de ignição |

A caixa de ignição assume o **pack 3S2P dobrado em 130 × 54 × 18 mm**.
Se o pack for um **suporte de 6 células (195 × 36 mm)**, a caixa cresce para
**205 × 105 × 75 mm**; o modelo está parametrizado para essa troca.

## Arquivos

| Arquivo | Função |
|---|---|
| `params.scad` | Todas as cotas, posições e envelopes. |
| `lib/case_lib.scad` | Corpo, tampa, gaxeta, bossos, painéis, componentes. |
| `comando.scad` | Caixa de comando. `part=0` assembly, `1` corpo, `2` tampa, `3` porta. |
| `ignicao.scad` | Caixa de ignição. Mesmos `part`. |
| `cupons.scad` | Cupom de gaxeta (`part=1,2`) e de inserto (`part=3`). |
| `atuador.scad` | Atuador 36:1 NEMA 17 (2 estágios planetários helicoidais + rolamento de esferas 6 mm). `part="assembly"` (0), `"corte"`, `"fatia"`, `"caixa"`, `"sun1"`, `"planeta"`, `"carrier1"`, `"saida"`, `"tampa"`, `"gaiola"`, `"boss"`, `"cupom"`. Ver `../atuador/README.md`. |
| `lib/gear_lib.scad` | Involuta externa/interna, helicoidal e pista de esferas. |
| `export.ps1` | Renderiza todos os STLs em `out/`. |
| `BOM.csv` | Lista mecânica/elétrica de compra. |

## Renderizar

```powershell
cd hardware/3d_models/openscad
powershell -ExecutionPolicy Bypass -File .\export.ps1
```

O script usa `D:\openscad\openscad.exe` (OpenSCAD 2021.01). Para render manual:

```powershell
& 'D:\openscad\openscad.exe' -o out\comando_body.stl -D 'part=1' comando.scad
& 'D:\openscad\openscad.exe' -o out\ignicao_lid.stl -D 'part=2' ignicao.scad
```

## Impressão

- **Corpo:** topo para cima, sem suportes, brim 5 mm.
- **Tampa:** inverter (lado de fora para baixo), com o lip para cima; sem suportes.
- **Porta:** lado de dentro para cima; o canal da gaxeta fica acessível.
- **Cupons:** imprimir **antes** das caixas.
- **Perfil:** 0,4 mm; camada 0,2 mm; 5 perímetros; 35% infill; 5 camadas topo/base;
  brim 5 mm; sem suportes; costura na traseira.
- **Material:** PETG no protótipo; ASA no final (precisa de enclosure/ventilação).
  Sem enclosure, ficar no PETG + verniz UV.
- **Impressoras:** Kobra 4 Combo para o corpo da ignição; Ender 3 V3 SE
  (220 × 220 × 250) para o comando, tampas, portas e cupons.

## Montagem

1. **Cupom de gaxeta** primeiro: cordão de silicone Ø2,5 mm no canal 3,5 × 1,9 mm;
   compressão de 24%; testar com água antes de imprimir a caixa.
2. **Cupom de inserto:** inserto de latão M3 × 5 × 6; furo Ø4,2 × 7; conferir o
   arrancamento antes de montar.
3. **Insertos** com ferro de solda a ~250 °C; não furar passante.
4. **Gaxeta** contínua, emenda em um canto, silicone grease; parafusos em cruz,
   **0,4–0,5 N·m**.
5. **Arruelas de vedação M3** (Dowty) sob os parafusos da tampa e da porta.
6. **RBF:** ímã na flag vermelha; reed **NC** dentro; RBF inserido = seguro,
   removido = armado. Sem furo passante.
7. **Baterias:** 2P sob a placa (comando e ignição); 3S2P no compartimento da
   porta da ignição, com BMS 3S, fusível 10 A, XT90 e respiro.
8. **Relé:** módulo 2 canais em **standoffs de nylon**; o GND do módulo é
   chaveado pelo Q2 — suporte metálico burla o interlock.
9. **J6/J9:** soldar **16 AWG direto nos pads**; não usar os headers 2,54 mm
   para a corrente de disparo.
10. **Falante:** 36 mm 8 Ω no J10/Q3 (PWM no GPIO14) ou com PAM8403; na ignição,
    membrana acústica Gore no lugar da grade.

## Pontos ainda abertos

- **2P × 2S:** o modelo usa 2P (65 × 36 × 18) sob a placa. 2S (130 × 18) não
  cabe sob a placa de 75 mm; exigiria berço lateral.
- **3S2P dobrado × suporte 6 células:** o modelo usa 130 × 54 × 18.
- **Relé 2 canais:** definir se os dois contatos são 2 polos do SKIB ou um é
  reserva; IN2 e jumper JD-VCC.
- **Falante:** drive direto pelo Q3 ou amp; o firmware precisa de PWM para tom.
- **J6/J9:** confirmar o laço `BAT+ → relé → J6 → Q1 → J9 → ignitor → BAT−`.
  Se for esse, o Q1 (IRLZ44N, N-channel) fica no lado alto com gate de 3,3 V e
  não satura; revisar antes do teste de 8 A.
- **3S2P disconnect:** o switch da imagem corta a 2 células antes do regulador;
  a 3S2P precisa de XT90/key separado.

## Legado

Os arquivos em `hardware/3d_models/comando/` e `hardware/3d_models/ignicao/`
(STEP e o `ignitorserra.3mf`) têm envelope de **200–390 mm** e **não**
correspondem à placa de 75 mm. Não imprimir. Ver `docs/ENCLOSURES.md`.
