// =============================================================================
//  Ignitor — parametros das caixas (OpenSCAD)
//  Fonte de verdade das cotas. Edite aqui e re-renderize.
// =============================================================================
$fn = 48;
EPS = 0.01;

// ---- Comum ---------------------------------------------------------------
WALL   = 3.5;   // parede lateral
FLOOR  = 4.0;   // fundo
RIM    = 6.0;   // largura do assento da gaxeta no topo
RAD    = 6.0;   // raio externo dos cantos
LID_T  = 3.5;   // espessura da tampa
GROOVE_W = 3.5; // canal da gaxeta
GROOVE_D = 1.9; // profundidade do canal (cordao 2.5 -> 24% compressao)
SCREW_D  = 7.0; // boss do parafuso M3
INSERT_D = 4.2; // furo do inserto de latao M3
INSERT_H = 7.0;
SCREW_HEAD_D = 7.0;
SCREW_HEAD_H = 3.5;

// ---- Placa 75 x 75 --------------------------------------------------------
BOARD_W = 75;
BOARD_D = 75;
BOARD_T = 1.6;
BOARD_HOLE_INSET = 4;     // furos M3 a 4 mm da borda -> 67 x 67
BOARD_STANDOFF_H = 20;    // comando: bateria 2P embaixo
BOARD_STANDOFF_H_IGN = 5; // ignicao: 3S2P embaixo, placa logo acima
BOARD_STANDOFF_D = 5.5;
BOARD_HOLE_D = 3.2;

// ---- Comando (console inclinado, frente a ~19°) --------------------------
CMD_W = 150;
CMD_D = 90;
CMD_H = 80;
CMD_BODY_H = CMD_H - LID_T;           // 76.5
CMD_R = 10;
CMD_SCREW_INSET = WALL + 8;           // 11.5 do lado externo
CMD_BOARD_POS = [10, 10, FLOOR + 18 + 2]; // placa à esquerda, sobre a 2P
CMD_BATT_POS = [15, 10, FLOOR];       // 2P sob a placa
CMD_DOOR = [12, 10, 80, 55];          // acesso à bateria, fundo-esquerda
CMD_DOOR_PLATE = [0, 0, 150, 90];     // tampa inferior completa
CMD_DOOR_SCREWS = [[8, 8], [142, 8], [8, 82], [142, 82]];

// frente inclinada: (Y=0,Z=4) -> (Y=25,Z=76.5)
CMD_SLOPE_BOTTOM_Z = 0;
CMD_SLOPE_TOP_Y = 25;
CMD_SLOPE_TOP_Z = CMD_BODY_H;
CMD_SLOPE_ANGLE = atan(CMD_SLOPE_TOP_Y / (CMD_SLOPE_TOP_Z - CMD_SLOPE_BOTTOM_Z));
CMD_SLOPE_NORMAL_ROT = 90 - CMD_SLOPE_ANGLE;

// controles na face inclinada: u = posição ao longo da rampa
CMD_OLED_U = 52;
CMD_OLED_X = 100;
CMD_OLED_W = 25;
CMD_OLED_H = 15;
CMD_LEDS_X = 143;
CMD_LEDS_U = [57, 47];
CMD_SPEAKER_X = 110;
CMD_SPEAKER_U = 22;
CMD_SPEAKER_D = 36;

// botão de hold (5 s) no topo-direita, com anel de guarda
CMD_BUTTON_TOP = [120, 60, 22];       // x, y, diâmetro
CMD_BUTTON_GUARD = 8;                 // largura do anel de guarda
CMD_SWITCH  = [30, 60, 12];           // switch mantido no topo-esquerda
CMD_USB     = [40, 35, 8, 3];         // lateral direita
CMD_CHARGE  = [65, 20, 9, 3];         // lateral direita
CMD_SMA     = [30, 45, 6.5];          // traseira esquerda
CMD_TRIPOD  = [130, 70];              // inserto 1/4"-20 no fundo
CMD_WRIST   = [145, 85, 40, 6];       // furo de cordão na traseira

// ---- Ignição -------------------------------------------------------------
IGN_W = 150;
IGN_D = 110;
IGN_H = 75;
IGN_BODY_H = IGN_H - LID_T;           // 81.5
IGN_SCREW_INSET = WALL + 8;
IGN_BOARD_POS = [13.5, 13.5, FLOOR + 18 + 2 + BOARD_STANDOFF_H_IGN];
IGN_3S2P_POS = [10, 45, FLOOR];       // pack dobrado 130 x 54 x 18
IGN_3S2P_SIZE = [130, 54, 18];
IGN_2P_POS = [65, 10, FLOOR];         // eletronica 65 x 36 x 18
IGN_2P_SIZE = [65, 36, 18];
IGN_RELAY_POS = [10, 10, FLOOR];      // modulo 2 reles 50 x 40 x 19, perto de J6/J9
IGN_RELAY_SIZE = [50, 40, 19];
IGN_ENDSTOP_POS = [75, 26, FLOOR + 18]; // reed NC do RBF, sobre a bateria 2P
IGN_ENDSTOP_SIZE = [20, 10, 5];
IGN_SPEAKER = [110, 80, 36, 12];
IGN_SWITCH  = [25, 85, 12];
IGN_RBF     = [75, 0, 20, 10, 5];     // x, y, w, d, profundidade (frente)
IGN_SMA     = [75, 45, 6.5];          // x, z, diametro (traseira)
IGN_VENT    = [55, 45, 12];           // y, z, diametro (lateral direita)
IGN_OUTPUT  = [20, 20];               // y, z, flange 30x30 (lateral esquerda)
IGN_POWER   = [130, 20];              // x, z, M12 (traseira)
IGN_CHARGE  = [80, 20];               // y, z, M12 (lateral direita)
IGN_DOOR    = [10, 10, 132, 88];      // x, y, w, d — 3S2P + 2P acesso
IGN_DOOR_PLATE = [0, 0, 150, 110];
IGN_DOOR_SCREWS = [[5, 5], [145, 5], [5, 105], [145, 105]];

// ---- Componentes fora da placa (envelopes) --------------------------------
BATT_2P = [65, 36, 18];
BATT_2S = [130, 18, 18];
BATT_3S2P = [130, 54, 18];
RELAY2 = [50, 40, 19];
ENDSTOP = [20, 10, 5];
SPEAKER_D = 36;
SPEAKER_H = 12;
OLED = [27, 27, 4];
BUTTON_D = 12;
BUTTON_H = 25;
SWITCH_D = 12;
SWITCH_H = 30;
FUSE = [20, 10, 10];
WAGO = [20, 10, 10];
BMS = [60, 30, 10];
SMA_D = 6.5;
VENT_D = 12;

// ---- Atuador 36:1 — NEMA 17 + rolamento de esferas 6 mm -------------------
//  Trem: 2 estagios planetarios simples em serie (anel fixo).
//  i = (1 + ZR/ZS)^2 = (1 + 75/15)^2 = 36,00
AT_M      = 0.8;                 // modulo
AT_ALPHA  = 20;                  // angulo de pressao (graus)
AT_BETA   = 15;                  // angulo de helice (graus)
AT_ZS     = 15;                  // dentes do sun
AT_ZP     = 30;                  // dentes do planeta
AT_ZR     = 75;                  // dentes do anel
AT_NP     = 3;                   // planetas por estagio
AT_BL     = 0.12;                // folga de flanco total (mm)
AT_HA     = 1.0;                 // coeficiente de adendo
AT_HF     = 1.25;                // coeficiente de dedendo

AT_A      = AT_M * (AT_ZS + AT_ZP) / 2;      // 18,0 distancia de centro
AT_R_S    = AT_M * AT_ZS / 2;                // 6,0  raio de referencia do sun
AT_R_P    = AT_M * AT_ZP / 2;                // 12,0 raio de referencia do planeta
AT_R_R    = AT_M * AT_ZR / 2;                // 30,0 raio de referencia do anel
AT_RA_S   = AT_R_S + AT_M * AT_HA;           // 6,8
AT_RA_P   = AT_R_P + AT_M * AT_HA;           // 12,8
AT_RA_R   = AT_R_R - AT_M * AT_HA;           // 29,2 ponta interna do anel
AT_RF_R   = AT_R_R + AT_M * AT_HF;           // 31,0 raiz do anel
AT_WG     = 6.6;                 // largura da face das engrenagens
AT_WR     = 7.0;                 // largura da face dos aneis (caixa)

// ---- caixa / rolamento -----------------------------------------------------
AT_OD      = 72;                 // corpo da caixa
AT_FLANGE  = 84;                 // flange superior (tampa da pista)
AT_PILOT_R = 30.5;               // raio do piloto radial da saida (Ø61)
AT_NECK_R  = 30.2;               // raio do colo da saida (0,3 de folga)
AT_R_BALL  = 35.5;               // raio da pista das esferas
AT_BALL    = 6.0;                // esfera de airsoft
AT_RG      = AT_BALL / 2 + 0.25; // raio do canal toroidal
AT_NBALL   = 30;
AT_CAGE_W  = 8.0;                // largura radial da gaiola
AT_CAGE_T  = 0.8;

// ---- cotas em Z (0 = face do motor) ---------------------------------------
AT_Z_S1    = 6.0;                // inicio do estagio 1
AT_Z_C1    = 13.0;               // prato do carrier 1
AT_Z_S2    = 16.0;               // inicio do estagio 2
AT_Z_C2    = 23.2;               // prato do carrier 2 (saida)
AT_Z_FLG   = 24.0;               // flange superior da caixa
AT_Z_RACE  = 28.0;               // tampa/pista das esferas
AT_Z_BALL  = 32.5;               // centro das esferas
AT_Z_OUT   = 33.5;               // face inferior do disco de saida
AT_Z_OUT_T = 38.0;               // topo do disco de saida (face plana)

// ---- parafusos -------------------------------------------------------------
AT_M3_CLR  = 3.4;                // passante M3
AT_M3_TAP  = 2.8;                // piloto para M3 autoatarrachante
AT_NEMA    = 15.5;               // +/- do padrao NEMA 17 (31 mm)
AT_INSERT_D = 4.6;               // inserto de latao M3
AT_INSERT_H = 6.0;

// ---- Helpers -------------------------------------------------------------
function screws(W, D, inset) = [
    [inset, inset], [W - inset, inset],
    [inset, D - inset], [W - inset, D - inset],
    [W / 2, inset], [W / 2, D - inset]
];

function screws8(W, D, inset) = concat(
    screws(W, D, inset),
    [[inset, D / 2], [W - inset, D / 2]]
);

function board_holes(pos) = [
    [pos[0] + BOARD_HOLE_INSET, pos[1] + BOARD_HOLE_INSET],
    [pos[0] + BOARD_W - BOARD_HOLE_INSET, pos[1] + BOARD_HOLE_INSET],
    [pos[0] + BOARD_HOLE_INSET, pos[1] + BOARD_D - BOARD_HOLE_INSET],
    [pos[0] + BOARD_W - BOARD_HOLE_INSET, pos[1] + BOARD_D - BOARD_HOLE_INSET]
];
