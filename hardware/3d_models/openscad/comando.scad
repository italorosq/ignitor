// =============================================================================
//  Caixa da Estacao de Comando — console inclinado 150 x 90 x 80
//  Frente a ~19°, controles na rampa, switch no topo-direito.
//  part = 0 assembly | 1 body | 2 lid | 3 door
// =============================================================================
include <lib/case_lib.scad>;

part = 0;

// 8 parafusos da tampa no topo (Y=25..90)
CMD_SCREWS = [
    [11.5, 34], [75, 34], [138.5, 34],
    [11.5, 75], [138.5, 75],
    [11.5, 84], [75, 84], [138.5, 84]
];
// mesma lista, em coordenadas locais da tampa (Y local = Y - 25)
CMD_LID_SCREWS = [
    [11.5, 9], [75, 9], [138.5, 9],
    [11.5, 50], [138.5, 50],
    [11.5, 59], [75, 59], [138.5, 59]
];
CMD_BOARD_HOLES = board_holes(CMD_BOARD_POS);
CMD_DOOR_SCREWS = [[8, 8], [142, 8], [8, 82], [142, 82]];

function slope_y(u) = u * sin(CMD_SLOPE_ANGLE);
function slope_z(u) = CMD_SLOPE_BOTTOM_Z + u * cos(CMD_SLOPE_ANGLE);

module slope_point(x, u) {
    translate([x, slope_y(u), slope_z(u)])
        rotate([CMD_SLOPE_NORMAL_ROT, 0, 0])
            children();
}

module slope_window(x, u, w, h, depth) {
    slope_point(x, u)
        cube([w, h, depth], center = true);
}

module slope_hole(x, u, d, depth) {
    slope_point(x, u)
        cylinder(h = depth, d = d, center = true);
}

module slope_grille(cx, u, hole_d, pitch, n) {
    for (i = [-n : n])
        for (j = [-n : n])
            if (i * i + j * j <= n * n)
                slope_hole(cx + i * pitch, u + j * pitch, hole_d, WALL + 2);
}

// ---- Corpo: hull de dois blocos, com a frente inclinada -------------------
module cmd_outer() {
    intersection() {
        hull() {
            translate([0, 0, 0])
                cube([CMD_W, CMD_D, 1]);
            translate([0, CMD_SLOPE_TOP_Y, CMD_BODY_H - 1])
                cube([CMD_W, CMD_D - CMD_SLOPE_TOP_Y, 1]);
        }
        linear_extrude(height = CMD_H) rrect(CMD_W, CMD_D, CMD_R);
    }
}

module cmd_inner() {
    intersection() {
        hull() {
            translate([WALL, WALL, FLOOR])
                cube([CMD_W - 2 * WALL, CMD_D - 2 * WALL, 1]);
            translate([WALL, 31, CMD_BODY_H - 3.5 - 1])
                cube([CMD_W - 2 * WALL, CMD_D - 31 - WALL, 1]);
        }
        linear_extrude(height = CMD_H + EPS)
            rrect(CMD_W - 2 * WALL, CMD_D - 2 * WALL, CMD_R - WALL);
    }
}

module command_body() {
    difference() {
        union() {
            difference() {
                cmd_outer();
                cmd_inner();
            }
            screw_bosses(CMD_W, CMD_D, CMD_BODY_H, CMD_SCREW_INSET, CMD_SCREWS);
            board_standoffs(CMD_BOARD_POS, BOARD_STANDOFF_H, CMD_BOARD_HOLES);
            bottom_door_bosses(CMD_W, CMD_D, CMD_DOOR_SCREWS);
            // inserto de tripé 1/4"-20
            translate([CMD_TRIPOD[0], CMD_TRIPOD[1], 0])
                difference() {
                    cylinder(h = 12, d = 14);
                    translate([0, 0, -EPS])
                        cylinder(h = 12 + 2 * EPS, d = 6.5);
                }
        }

        // canal da gaxeta no topo (Y=25..90)
        translate([0, 0, CMD_BODY_H - GROOVE_D])
            linear_extrude(height = GROOVE_D + EPS)
                difference() {
                    translate([0.75, CMD_SLOPE_TOP_Y + 0.75])
                        rrect(CMD_W - 1.5, CMD_D - CMD_SLOPE_TOP_Y - 1.5, CMD_R - 0.75);
                    translate([4.25, CMD_SLOPE_TOP_Y + 4.25])
                        rrect(CMD_W - 8.5, CMD_D - CMD_SLOPE_TOP_Y - 8.5, CMD_R - 4.25);
                }

        // controles na rampa
        slope_window(CMD_OLED_X, CMD_OLED_U, CMD_OLED_W, CMD_OLED_H, WALL + 2);
        for (u = CMD_LEDS_U)
            slope_hole(CMD_LEDS_X, u, 5, WALL + 2);
        slope_grille(CMD_SPEAKER_X, CMD_SPEAKER_U, 3, 6, 2);

        // lateral direita
        right_cut(CMD_USB[0] - CMD_USB[2] / 2, CMD_USB[1] - CMD_USB[3] / 2,
                  CMD_USB[2], CMD_USB[3], CMD_W, WALL);
        right_cut(CMD_CHARGE[0] - CMD_CHARGE[2] / 2, CMD_CHARGE[1] - CMD_CHARGE[3] / 2,
                  CMD_CHARGE[2], CMD_CHARGE[3], CMD_W, WALL);

        // traseira
        back_hole(CMD_SMA[0], CMD_SMA[1], CMD_SMA[2], CMD_D, WALL);
        translate([CMD_W + EPS, CMD_WRIST[1], CMD_WRIST[2]])
            rotate([0, 90, 0])
                cylinder(h = WALL + 2 * EPS, d = CMD_WRIST[3]);

        // fundo
        bottom_rect(CMD_DOOR[0], CMD_DOOR[1], CMD_DOOR[2], CMD_DOOR[3]);
    }
}

module command_lid() {
    union() {
        difference() {
            rbox(CMD_W, CMD_D - CMD_SLOPE_TOP_Y, LID_T, CMD_R);
            for (p = CMD_LID_SCREWS) {
                translate([p[0], p[1], -EPS])
                    cylinder(h = LID_T + 2 * EPS, d = 3.4);
                translate([p[0], p[1], LID_T - 3.5])
                    cylinder(h = 3.5 + EPS, d = 7);
            }
            // switch mantido
            translate([CMD_SWITCH[0], CMD_SWITCH[1] - CMD_SLOPE_TOP_Y, -EPS])
                cylinder(h = LID_T + 2 * EPS, d = CMD_SWITCH[2]);
            // botão de hold
            translate([CMD_BUTTON_TOP[0], CMD_BUTTON_TOP[1] - CMD_SLOPE_TOP_Y, -EPS])
                cylinder(h = LID_T + 2 * EPS, d = CMD_BUTTON_TOP[2] + 0.5);
        }
        // anel de guarda do botão de hold
        translate([CMD_BUTTON_TOP[0], CMD_BUTTON_TOP[1] - CMD_SLOPE_TOP_Y, LID_T])
            difference() {
                cylinder(h = 4, d = CMD_BUTTON_TOP[2] + 2 * CMD_BUTTON_GUARD);
                translate([0, 0, -EPS])
                    cylinder(h = 4 + 2 * EPS, d = CMD_BUTTON_TOP[2] + 0.5);
            }
    }
}

module command_door() {
    difference() {
        rbox(CMD_DOOR_PLATE[2], CMD_DOOR_PLATE[3], 3, 4);
        for (p = CMD_DOOR_SCREWS)
            translate([p[0], p[1], -EPS])
                cylinder(h = 3 + 2 * EPS, d = 3.4);
        translate([2, 2, 3 - 1.5])
            difference() {
                linear_extrude(height = 1.5 + EPS) rrect(146, 86, 4);
                translate([4, 4, -EPS])
                    linear_extrude(height = 1.5 + 2 * EPS) rrect(138, 78, 3);
            }
    }
}

module command_assembly() {
    color("WhiteSmoke", 0.30) command_body();
    color("Gainsboro", 0.30) translate([0, CMD_SLOPE_TOP_Y, CMD_BODY_H]) command_lid();
    color("Silver", 0.55) command_door();

    board_model(CMD_BOARD_POS);
    battery_2p(CMD_BATT_POS, BATT_2P);

    // OLED atrás da janela
    slope_point(CMD_OLED_X, CMD_OLED_U)
        translate([0, 0, -4])
            color("MidnightBlue") cube([27, 27, 4], center = true);
    // botão de hold no topo (22 mm)
    color("Crimson")
        translate([CMD_BUTTON_TOP[0], CMD_BUTTON_TOP[1], CMD_H - 2])
            cylinder(h = 6, d = CMD_BUTTON_TOP[2]);
    // LEDs
    for (u = CMD_LEDS_U)
        slope_point(CMD_LEDS_X, u)
            translate([0, 0, -5])
                color("Lime") cylinder(h = 5, d = 5, center = true);
    // falante
    slope_point(CMD_SPEAKER_X, CMD_SPEAKER_U)
        translate([0, 0, -12])
            color("Black") cylinder(h = 12, d = 36, center = true);

    guarded_switch([CMD_SWITCH[0] - 15, CMD_SWITCH[1] - 15, CMD_H + 4]);
    sma_mod([CMD_SMA[0], CMD_D - 1, CMD_SMA[1]]);

    color("Black") translate([CMD_W - 2, CMD_USB[0] - 4, CMD_USB[1] - 1.5])
        cube([4, 8, 3]);
    color("Black") translate([CMD_W - 2, CMD_CHARGE[0] - 4.5, CMD_CHARGE[1] - 1.5])
        cube([4, 9, 3]);
    color("Goldenrod") translate([CMD_TRIPOD[0], CMD_TRIPOD[1], -3])
        cylinder(h = 3, d = 12);
}

if (part == 1) command_body();
else if (part == 2) command_lid();
else if (part == 3) command_door();
else command_assembly();
