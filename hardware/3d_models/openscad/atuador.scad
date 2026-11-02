// =============================================================================
//  Atuador 36:1 — caixa planetaria helicoidal de 2 estagios
//  NEMA 17 · rolamento de esferas 6 mm (airsoft) · saida flange 4x M3 (rebaixo Ø22)
//
//  i = (1 + ZR/ZS)^2 = (1 + 75/15)^2 = 36,00
//
//  part = assembly | corte | transp | fatia | caixa | sun1 | planeta |
//         carrier1 | saida | tampa | gaiola | boss | cupom
//
//  Impressao:
//    caixa ....... em pe, prato do motor na mesa          (sem suporte)
//    sun1 ........ cubo para baixo                        (sem suporte)
//    planeta ..... deitado                                (sem suporte)
//    carrier1 .... sun2 para baixo                        (SUPORTE sob o prato)
//    saida ....... disco na mesa, face de saida para baixo (sem suporte)
//    tampa ....... canal para cima                        (sem suporte)
//    gaiola ...... deitada                                (sem suporte)
//    boss ........ spigot para baixo                      (sem suporte)
// =============================================================================
include <params.scad>;
include <lib/gear_lib.scad>;

part = "assembly";
FATIA_Z = 19.3;

// ---- constantes derivadas ---------------------------------------------------
_RING_PHASE = 180 / AT_ZR;          // deixa um DENTE do anel no eixo +X
_PLANET_PH  = 180 / AT_ZP;          // meia espessura de passo do planeta
_ZG1        = AT_Z_S1 + 0.2;        // z do sun/planetas do estagio 1
_ZG2        = AT_Z_S2 + 0.2;        // z das engrenagens do estagio 2

// =============================================================================
//  PECAS
// =============================================================================

// ---- caixa: prato do motor + 2 aneis internos + flange + piloto -------------
module caixa() {
    difference() {
        union() {
            // prato do motor (0..6)
            cylinder(h = AT_Z_S1, r = AT_OD / 2, $fn = 160);

            // corpo (6..24) — macico, a cavidade e cortada no difference de fora
            translate([0, 0, AT_Z_S1])
                cylinder(h = AT_Z_FLG - AT_Z_S1, r = AT_OD / 2, $fn = 160);

            // flange superior (24..28)
            translate([0, 0, AT_Z_FLG])
                cylinder(h = AT_Z_RACE - AT_Z_FLG, r = AT_FLANGE / 2, $fn = 160);

            // piloto radial (24..28): Ø61 para o colo da saida
            translate([0, 0, AT_Z_FLG])
                cylinder(h = AT_Z_RACE - AT_Z_FLG, r = AT_RF_R, $fn = 160);
        }

        // cavidade escalonada (coordenadas absolutas):
        //   raio dos pes dos dentes nas zonas de engrenamento,
        //   raio maior nas zonas dos carriers
        translate([0, 0, AT_Z_S1 - EPS])
            cylinder(h = AT_Z_C1 - AT_Z_S1 + 2 * EPS, r = AT_RA_R + 0.05, $fn = 160);
        translate([0, 0, AT_Z_C1])
            cylinder(h = AT_Z_S2 - AT_Z_C1, r = AT_RF_R + 0.2, $fn = 160);
        translate([0, 0, AT_Z_S2])
            cylinder(h = AT_Z_C2 - AT_Z_S2, r = AT_RA_R + 0.05, $fn = 160);
        translate([0, 0, AT_Z_C2])
            cylinder(h = AT_Z_FLG - AT_Z_C2 + EPS, r = AT_RF_R + 0.2, $fn = 160);

        // anel do estagio 1 e do estagio 2
        translate([0, 0, AT_Z_S1])
            ring_cut(AT_M, AT_ZR, AT_ALPHA, AT_BETA, AT_WR, -1, AT_BL,
                     phase = _RING_PHASE);
        translate([0, 0, AT_Z_S2])
            ring_cut(AT_M, AT_ZR, AT_ALPHA, AT_BETA, AT_WR, -1, AT_BL,
                     phase = _RING_PHASE);

        // furo de Ø61 (piloto da saida) no flange e no anel de piloto
        translate([0, 0, AT_Z_FLG - EPS])
            cylinder(h = AT_Z_RACE - AT_Z_FLG + 2 * EPS, r = AT_PILOT_R, $fn = 160);

        // furo central (passagem do cubo do sun1 / boss do motor)
        translate([0, 0, -EPS]) cylinder(h = AT_Z_S1 + 2 * EPS, d = 24, $fn = 96);
        // rebaixo do boss do motor (Ø22,4 x 2,2)
        translate([0, 0, -EPS]) cylinder(h = 2.2 + EPS, d = 22.4, $fn = 96);

        // padrao NEMA 17 + rebaixo da cabeca
        for (sx = [-1, 1], sy = [-1, 1])
            translate([sx * AT_NEMA, sy * AT_NEMA, -EPS]) {
                cylinder(h = AT_Z_S1 + 2 * EPS, d = AT_M3_CLR, $fn = 32);
                translate([0, 0, 2.2]) cylinder(h = 2.2, d = 6.2, $fn = 32);
            }

        // 8x M3 autoatarrachante da tampa (r=39,5) — parafuso vem por baixo
        for (i = [0 : 7]) rotate([0, 0, i * 45 + 22.5])
            translate([39.5, 0, AT_Z_FLG]) cylinder(h = 4.1, d = AT_M3_TAP, $fn = 32);
        // rebaixo da cabeca por baixo do flange
        for (i = [0 : 7]) rotate([0, 0, i * 45 + 22.5])
            translate([39.5, 0, AT_Z_FLG - 2]) cylinder(h = 2.1, d = 6.2, $fn = 32);
    }
}

// ---- sun 1 (entrada, eixo 5 mm do motor) ------------------------------------
module sun1() {
    difference() {
        union() {
            gear_ext(AT_M, AT_ZS, AT_ALPHA, AT_BETA, AT_WG, +1, bl = AT_BL);
            // cubo ABAIXO da engrenagem (o eixo do motor entra por baixo)
            translate([0, 0, -3.2]) cylinder(h = 3.4, d = 9.6, $fn = 64);
        }
        // furo do eixo 5 mm
        translate([0, 0, -12]) cylinder(h = 32, d = 5.1, $fn = 48);
        // grub screw M3 — furo radial curto, so na parede do cubo
        translate([1.8, 0, -1.6]) rotate([0, 90, 0]) cylinder(h = 3.4, d = 2.6, $fn = 24);
    }
}

// ---- planeta ----------------------------------------------------------------
module planeta() {
    difference() {
        gear_ext(AT_M, AT_ZP, AT_ALPHA, AT_BETA, AT_WG, -1, bl = AT_BL);
        translate([0, 0, -EPS]) cylinder(h = AT_WG + 2 * EPS, d = 5.2, $fn = 48);
    }
}

// ---- carrier 1 + sun 2 (peca unica) ----------------------------------------
module carrier1() {
    difference() {
        union() {
            // prato
            translate([0, 0, AT_Z_C1])
                cylinder(h = AT_Z_S2 - AT_Z_C1, r = 29.9, $fn = 160);
            // sun do estagio 2 (fase do dente 0 no +X, igual ao sun1)
            translate([0, 0, _ZG2 - 0.0])
                gear_ext(AT_M, AT_ZS, AT_ALPHA, AT_BETA, AT_WG, +1, bl = AT_BL);
            // 3 pinos Ø5 (bucha impressa; aceita varão de 5 mm se alargar)
            for (i = [0 : AT_NP - 1])
                rotate([0, 0, i * 360 / AT_NP])
                    translate([AT_A, 0, AT_Z_S1])
                        cylinder(h = AT_Z_C1 - AT_Z_S1, d = 5.0, $fn = 48);
        }
        // passagem do eixo do motor
        translate([0, 0, -10]) cylinder(h = 40, d = 5.8, $fn = 48);
    }
}

// ---- saida: carrier 2 + corpo + disco + flange -----------------------------
// Face de saida PLANA com rebaixo de centragem Ø22 x 3 (imprime sem suporte).
// O boss saliente e a peca opcional `boss`, que encaixa no rebaixo.
module saida() {
    difference() {
        union() {
            // corpo macico (prato + colo)
            translate([0, 0, AT_Z_C2])
                cylinder(h = AT_Z_OUT - AT_Z_C2, r = AT_NECK_R, $fn = 160);
            // disco de saida
            translate([0, 0, AT_Z_OUT])
                cylinder(h = AT_Z_OUT_T - AT_Z_OUT, r = 40, $fn = 160);
            // 3 pinos do estagio 2
            for (i = [0 : AT_NP - 1])
                rotate([0, 0, i * 360 / AT_NP])
                    translate([AT_A, 0, _ZG2 - 0.2])
                        cylinder(h = AT_Z_C2 - _ZG2 + 0.2, d = 5.0, $fn = 48);
        }
        // canal toroidal das esferas na face inferior do disco
        translate([0, 0, AT_Z_BALL]) ball_groove(AT_R_BALL, AT_RG, 0);
        // furo central passante (ponta do eixo do motor)
        translate([0, 0, AT_Z_C2 - 1]) cylinder(h = 30, d = 8, $fn = 48);
        // rebaixo de centragem Ø22 x 3
        translate([0, 0, AT_Z_OUT_T - 3])
            cylinder(h = 3 + EPS, d = 22, $fn = 96);
        // 4x M3 (inserto) a r=15
        for (sx = [-1, 1], sy = [-1, 1])
            translate([sx * 10.6066, sy * 10.6066, AT_Z_OUT_T - AT_INSERT_H])
                cylinder(h = AT_INSERT_H + 1, d = AT_INSERT_D, $fn = 32);
    }
}

// ---- boss opcional Ø22 (entra no rebaixo da saida) -------------------------
module boss() {
    difference() {
        union() {
            translate([0, 0, 3.0]) cylinder(h = 4.0, d = 22, $fn = 96);
            cylinder(h = 3.2, d = 21.6, $fn = 96);       // spigot no rebaixo
        }
        translate([0, 0, -1]) cylinder(h = 10, d = 8, $fn = 48);
    }
}

// ---- tampa / pista das esferas ---------------------------------------------
module tampa() {
    difference() {
        translate([0, 0, AT_Z_RACE])
            cylinder(h = AT_Z_BALL - AT_Z_RACE, r = AT_FLANGE / 2, $fn = 160);
        // furo central
        translate([0, 0, AT_Z_RACE - EPS])
            cylinder(h = AT_Z_BALL - AT_Z_RACE + 2 * EPS, r = AT_PILOT_R, $fn = 160);
        // pista toroidal
        translate([0, 0, AT_Z_BALL]) ball_groove(AT_R_BALL, AT_RG, 0);
        // 8x M3 passante (parafuso vem por baixo)
        for (i = [0 : 7]) rotate([0, 0, i * 45 + 22.5])
            translate([39.5, 0, AT_Z_RACE - EPS])
                cylinder(h = AT_Z_BALL - AT_Z_RACE + 2 * EPS, d = AT_M3_CLR, $fn = 32);
    }
}

// ---- gaiola das esferas -----------------------------------------------------
module gaiola() {
    r0 = AT_R_BALL - AT_CAGE_W / 2;
    n  = AT_NBALL;
    zc = (AT_Z_BALL + AT_Z_OUT) / 2;              // centro do vao (1,0 mm)
    difference() {
        translate([0, 0, zc - AT_CAGE_T / 2])
            difference() {
                cylinder(h = AT_CAGE_T, r = AT_R_BALL + AT_CAGE_W / 2, $fn = 160);
                translate([0, 0, -EPS])
                    cylinder(h = AT_CAGE_T + 2 * EPS, r = r0, $fn = 160);
            }
        for (i = [0 : n - 1]) rotate([0, 0, i * 360 / n])
            translate([AT_R_BALL, 0, zc - 2])
                cylinder(h = 4, d = AT_BALL + 0.4, $fn = 32);
    }
}

// ---- cupom de folga (sun + planeta engrenados, imprime no lugar) -----------
module cupom() {
    z1 = 3.0;                                  // espessura da base
    difference() {
        union() {
            // base tipo "palito" sob os dois eixos
            hull() {
                translate([0, 0, 0]) cylinder(h = z1, r = 10, $fn = 64);
                translate([AT_A, 0, 0]) cylinder(h = z1, r = 15, $fn = 64);
            }
            // pinos
            translate([0, 0, z1]) cylinder(h = AT_WG, d = 4.95, $fn = 48);
            translate([AT_A, 0, z1]) cylinder(h = AT_WG, d = 4.95, $fn = 48);
        }
        // alivio central (nao precisa de material sob o sun)
        translate([0, 0, -1]) cylinder(h = z1 + 2, r = 4.0, $fn = 48);
    }
    // sun (folga de 0,3 no pino e 0,3 acima da base)
    translate([0, 0, z1 + 0.3])
        difference() {
            gear_ext(AT_M, AT_ZS, AT_ALPHA, AT_BETA, AT_WG, +1, bl = AT_BL);
            translate([0, 0, -EPS]) cylinder(h = AT_WG + 2 * EPS, d = 5.1, $fn = 48);
        }
    // planeta engrenado
    translate([AT_A, 0, z1 + 0.3]) rotate([0, 0, _PLANET_PH])
        difference() {
            gear_ext(AT_M, AT_ZP, AT_ALPHA, AT_BETA, AT_WG, -1, bl = AT_BL);
            translate([0, 0, -EPS]) cylinder(h = AT_WG + 2 * EPS, d = 5.2, $fn = 48);
        }
}

// =============================================================================
//  MONTAGEM
// =============================================================================
module estagio(z0, sun_first = true) {
    translate([0, 0, z0]) {
        if (sun_first)
            gear_ext(AT_M, AT_ZS, AT_ALPHA, AT_BETA, AT_WG, +1, bl = AT_BL);
        for (i = [0 : AT_NP - 1])
            rotate([0, 0, i * 360 / AT_NP])
                translate([AT_A, 0, 0]) rotate([0, 0, _PLANET_PH])
                    gear_ext(AT_M, AT_ZP, AT_ALPHA, AT_BETA, AT_WG, -1, bl = AT_BL);
    }
}

module assembly() {
    color("Gainsboro") caixa();
    color("WhiteSmoke") tampa();
    color("Orange", 0.9) gaiola();
    color("Silver") ball_ring(AT_R_BALL, AT_BALL, AT_NBALL, AT_Z_BALL);

    // estagio 1
    color("SteelBlue") translate([0, 0, _ZG1]) sun1();
    for (i = [0 : AT_NP - 1])
        rotate([0, 0, i * 360 / AT_NP])
            translate([AT_A, 0, _ZG1]) rotate([0, 0, _PLANET_PH]) planeta();

    // carrier 1 + sun 2
    color("DarkOrange") carrier1();

    // estagio 2
    for (i = [0 : AT_NP - 1])
        rotate([0, 0, i * 360 / AT_NP])
            translate([AT_A, 0, _ZG2]) rotate([0, 0, _PLANET_PH]) planeta();

    // saida
    color("Firebrick") saida();

    // pinos 5 mm (opcional, so para conferir)
    for (i = [0 : AT_NP - 1]) rotate([0, 0, i * 360 / AT_NP]) {
        color("Silver") translate([AT_A, 0, AT_Z_S1 - 0.5]) cylinder(h = 7.2, d = 5.0, $fn = 24);
        color("Silver") translate([AT_A, 0, _ZG2 - 0.4]) cylinder(h = 7.2, d = 5.0, $fn = 24);
    }
}

// =============================================================================
//  SELETOR
// =============================================================================
if (part == "caixa") caixa();
else if (part == "sun1") sun1();
else if (part == "planeta") planeta();
else if (part == "carrier1") translate([0, 0, AT_Z_S1 + AT_Z_S2 + AT_WG + 0.2])
        rotate([180, 0, 0]) carrier1();
else if (part == "saida") translate([0, 0, AT_Z_OUT_T])
        rotate([180, 0, 0]) saida();
else if (part == "boss") boss();
else if (part == "tampa") tampa();
else if (part == "gaiola") gaiola();
else if (part == "cupom") cupom();
// posicoes de montagem (usadas na checagem de interferencia)
else if (part == "asm_caixa") caixa();
else if (part == "asm_sun1") translate([0, 0, _ZG1]) sun1();
else if (part == "asm_carrier1") carrier1();
else if (part == "asm_saida") saida();
else if (part == "asm_tampa") tampa();
else if (part == "asm_planeta1") translate([AT_A, 0, _ZG1]) rotate([0, 0, _PLANET_PH]) planeta();
else if (part == "asm_planeta2") translate([AT_A, 0, _ZG2]) rotate([0, 0, _PLANET_PH]) planeta();
else if (part == "asm_gaiola") gaiola();
else if (part == "transp") {
    // vista com a carcaça translúcida (imagem de divulgação)
    %caixa();
    %tampa();
    %gaiola();
    %ball_ring(AT_R_BALL, AT_BALL, AT_NBALL, AT_Z_BALL);
    color("SteelBlue") translate([0, 0, _ZG1]) sun1();
    for (i = [0 : AT_NP - 1])
        color("SteelBlue") rotate([0, 0, i * 360 / AT_NP])
            translate([AT_A, 0, _ZG1]) rotate([0, 0, _PLANET_PH]) planeta();
    color("DarkOrange") carrier1();
    for (i = [0 : AT_NP - 1])
        color("SteelBlue") rotate([0, 0, i * 360 / AT_NP])
            translate([AT_A, 0, _ZG2]) rotate([0, 0, _PLANET_PH]) planeta();
    color("Firebrick") saida();
}
else if (part == "fatia") intersection() {
    assembly();
    translate([-100, -100, FATIA_Z]) cube([200, 200, 0.4]);
}
else if (part == "corte") {
    // corte individual por peca: preserva as cores na vista em secao
    difference() { color("Gainsboro") caixa();  translate([-200, -200, -50]) cube([400, 200, 200]); }
    difference() { color("WhiteSmoke") tampa(); translate([-200, -200, -50]) cube([400, 200, 200]); }
    difference() { color("Orange") gaiola();    translate([-200, -200, -50]) cube([400, 200, 200]); }
    difference() { color("Silver") ball_ring(AT_R_BALL, AT_BALL, AT_NBALL, AT_Z_BALL);
                   translate([-200, -200, -50]) cube([400, 200, 200]); }
    difference() { color("SteelBlue") translate([0, 0, _ZG1]) sun1();
                   translate([-200, -200, -50]) cube([400, 200, 200]); }
    difference() { color("SteelBlue") translate([AT_A, 0, _ZG1]) rotate([0, 0, _PLANET_PH]) planeta();
                   translate([-200, -200, -50]) cube([400, 200, 200]); }
    difference() { color("DarkOrange") carrier1();
                   translate([-200, -200, -50]) cube([400, 200, 200]); }
    difference() { color("SteelBlue") translate([AT_A, 0, _ZG2]) rotate([0, 0, _PLANET_PH]) planeta();
                   translate([-200, -200, -50]) cube([400, 200, 200]); }
    difference() { color("Firebrick") saida();
                   translate([-200, -200, -50]) cube([400, 200, 200]); }
}
else assembly();
