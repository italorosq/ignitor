Crie a arte de serigrafia (silkscreen, branca) de 3 PCBs da Serra Rocketry (projeto Ignitor, ignição remota de foguetes via LoRa). Tema: foguete experimental decolando de uma serra em meio a chuva de meteoros; rastros de meteoro são trilhas de PCB (linhas de 45° terminando em via) e estrelas-tack (cruzes de 4 pontas) + pontos.

Figma: 1 mm = 10 px; grid 0,5 mm. Frames: IGNICAO-SMD 750×750 px; IGNICAO-PTH 750×800; COMANDO 600×580. Camadas: REF (contorno, furos M3 nos cantos, keep-outs vermelho 15%, não exporta), SILK e TEXTOS.

Zonas livres (mm, origem canto superior esquerdo):
• SMD: rodapé x1–55/y57–74 (cena principal: foguete grande + serra + meteoros); canto superior esquerdo x7–27/y6–21 (tacks).
• PTH: canto inferior esquerdo x1–30/y56–78; canto superior esquerdo x1–29/y7–22.
• COMANDO: faixa central x20–44/y29–43 (antena de solo + meteoros); x45–58/y36–43.

Keep-outs (não colocar arte): SMD: ESP32 x27–49/y0–51; LoRa x2–26/y22–56; coluna direita x56–75. PTH: ESP32 x29–57/y0–51; LoRa x2–28/y22–56; coluna direita x57–75; fileira inferior x31–70/y52–75. COMANDO: Pico x0–20/y2–55; LoRa x23–58/y3–29; bloco x26–59/y28–60. Folga de 1 mm de bordas e furos.

Textos: "SERRA ROCKETRY" 3–4 mm, caixa alta, tracking aberto, serra como sublinhado; "IGNIÇÃO · SMD" / "IGNIÇÃO · PTH" / "COMANDO" + "REV 2" 1,5–2 mm; "github.com/Serra-Rocketry/ignitor" 1 mm.

Regras: monocromático #FFFFFF, fundo transparente; traço ≥0,2 mm; texto ≥1 mm; tudo preenchido (sem stroke); sem gradiente/sombra/raster.

Entregar: os 3 frames nomeados; SVG 1:1 só com SILK+TEXTOS (paths preenchidos); PNG 4× sobre máscara roxa #3A2A5A (SMD) e verde #1B5E20 (PTH e Comando).
