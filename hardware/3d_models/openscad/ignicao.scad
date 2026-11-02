// =============================================================================
//  Caixa da Estacao de Ignicao — 150 x 110 x 85
//  part = 0 assembly | 1 body | 2 lid | 3 door
// =============================================================================
include <lib/case_lib.scad>;

part = 0;

IGN_SCREWS = screws8(IGN_W, IGN_D, IGN_SCREW_INSET);
IGN_BOARD_HOLES = board_holes(IGN_BOARD_POS);
IGN_DOOR_SCREWS = [[5, 5], [145, 5], [5, 105], [145, 105]];
IGN_DOOR_PLATE = [0, 0, 150, 110];

module ignition_body() {
    difference() {
        union() {
            body_shell(IGN_W, IGN_D, IGN_BODY_H, WALL, FLOOR, RIM, RAD);
            screw_bosses(IGN_W, IGN_D, IGN_BODY_H, IGN_SCREW_INSET, IGN_SCREWS);
            board_standoffs(IGN_BOARD_POS, BOARD_STANDOFF_H_IGN, IGN_BOARD_HOLES);
            bottom_door_bosses(IGN_W, IGN_D, IGN_DOOR_SCREWS);
        }

        groove_cut(IGN_W, IGN_D, WALL, RAD, IGN_BODY_H, GROOVE_D);

        // frente: bolsao cego do RBF (sem furo passante)
        translate([IGN_RBF[0] - IGN_RBF[2] / 2, -EPS, 40])
            cube([IGN_RBF[2], 2.0, IGN_RBF[3]]);

        // lateral esquerda: saida de ignicao (flange Deutsch)
        translate([-EPS, IGN_OUTPUT[0] - 11, IGN_OUTPUT[1] - 11])
            cube([WALL + 2 * EPS, 22, 22]);
        for (z = [IGN_OUTPUT[1] - 8, IGN_OUTPUT[1] + 8])
            translate([0, IGN_OUTPUT[0], z])
                rotate([0, 90, 0])
                    difference() {
                        cylinder(h = 7, d = 6);
                        translate([0, 0, -EPS])
                            cylinder(h = 7 + 2 * EPS, d = 4.2);
                    }

        // lateral direita: respiro ePTFE e carga M12
        translate([IGN_W - WALL - EPS, IGN_VENT[0], IGN_VENT[1]])
            rotate([0, 90, 0])
                cylinder(h = WALL + 2 * EPS, d = IGN_VENT[2]);
        translate([IGN_W - WALL - EPS, IGN_CHARGE[0], IGN_CHARGE[1]])
            rotate([0, 90, 0])
                cylinder(h = WALL + 2 * EPS, d = 12);

        // traseira: SMA e power M12
        back_hole(IGN_SMA[0], IGN_SMA[1], IGN_SMA[2], IGN_D, WALL);
        back_hole(IGN_POWER[0], IGN_POWER[1], 12, IGN_D, WALL);

        // fundo: porta da bateria 3S2P + 2P
        bottom_rect(IGN_DOOR[0], IGN_DOOR[1], IGN_DOOR[2], IGN_DOOR[3]);
    }
}

module ignition_lid() {
    difference() {
        lid_plate(IGN_W, IGN_D, LID_T, RAD, RIM + 0.2, RIM + 1.8, 4, IGN_SCREWS);

        // membrana acustica do alto-falante (Gore ou similar)
        translate([IGN_SPEAKER[0], IGN_SPEAKER[1], -EPS])
            cylinder(h = LID_T + 2 * EPS, d = 6);

        // switch da imagem
        translate([IGN_SWITCH[0], IGN_SWITCH[1], -EPS])
            cylinder(h = LID_T + 2 * EPS, d = IGN_SWITCH[2]);
    }
}

module ignition_door() {
    union() {
        difference() {
            rbox(IGN_DOOR_PLATE[2], IGN_DOOR_PLATE[3], 3, 4);
            for (p = IGN_DOOR_SCREWS)
                translate([p[0] - IGN_DOOR_PLATE[0], p[1] - IGN_DOOR_PLATE[1], -EPS])
                    cylinder(h = 3 + 2 * EPS, d = 3.4);
            translate([2, 2, 3 - 1.5])
                difference() {
                    linear_extrude(height = 1.5 + EPS) rrect(146, 106, 4);
                    translate([4, 4, -EPS])
                        linear_extrude(height = 1.5 + 2 * EPS) rrect(138, 98, 3);
                }
        }
        // parede do compartimento 3S2P, solidaria a tampa inferior
        difference() {
            translate([7, 43, 3])
                difference() {
                    rbox(136, 60, 22, 4);
                    translate([2, 2, -EPS])
                        rbox(132, 56, 22 + 2 * EPS, 2);
                }
            // rebaixo para o modulo de rele e a 2P encostarem no fundo
            translate([10, 43, 3]) cube([120, 7, 22 + 2 * EPS]);
        }
    }
}

module ignition_assembly() {
    color("WhiteSmoke", 0.30) ignition_body();
    color("Gainsboro", 0.30) translate([0, 0, IGN_BODY_H]) ignition_lid();
    color("Silver", 0.55) ignition_door();

    board_model(IGN_BOARD_POS);
    battery_3s2p(IGN_3S2P_POS, IGN_3S2P_SIZE);
    battery_2p(IGN_2P_POS, IGN_2P_SIZE);
    relay2(IGN_RELAY_POS, IGN_RELAY_SIZE);
    endstop_mod(IGN_ENDSTOP_POS, IGN_ENDSTOP_SIZE);

    speaker_mod([IGN_SPEAKER[0], IGN_SPEAKER[1], IGN_BODY_H - IGN_SPEAKER[3]],
                IGN_SPEAKER[2], IGN_SPEAKER[3]);
    guarded_switch([IGN_SWITCH[0] - 15, IGN_SWITCH[1] - 15, IGN_H]);
    rbf_flag([IGN_RBF[0] - IGN_RBF[2] / 2, -1, 40], [IGN_RBF[2], 4, IGN_RBF[3]]);
    sma_mod([IGN_SMA[0], IGN_D - 1, IGN_SMA[1]]);
    vent_mod([IGN_W - 1, IGN_VENT[0], IGN_VENT[1]]);

    // saida de ignicao na lateral esquerda
    color("Black")
        translate([-1, IGN_OUTPUT[0] - 15, IGN_OUTPUT[1] - 15])
            cube([4, 30, 30]);
    // power (traseira) e carga (lateral direita)
    color("DimGray")
        translate([IGN_POWER[0], IGN_D + 1, IGN_POWER[1]])
            rotate([90, 0, 0]) cylinder(h = 4, d = 14);
    color("DimGray")
        translate([IGN_W + 1, IGN_CHARGE[0], IGN_CHARGE[1]])
            rotate([0, 90, 0]) cylinder(h = 4, d = 14);
}

if (part == 1) ignition_body();
else if (part == 2) ignition_lid();
else if (part == 3) ignition_door();
else ignition_assembly();
