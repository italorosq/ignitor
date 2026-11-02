// =============================================================================
//  Ignitor — biblioteca OpenSCAD das caixas
//  Depende de ../params.scad
// =============================================================================
include <../params.scad>;

// ---- 2D / 3D primitives ---------------------------------------------------
module rrect(w, d, r) {
    rr = min(r, min(w, d) / 2 - 0.01);
    hull() {
        translate([rr, rr]) circle(r = rr);
        translate([w - rr, rr]) circle(r = rr);
        translate([rr, d - rr]) circle(r = rr);
        translate([w - rr, d - rr]) circle(r = rr);
    }
}

module rbox(w, d, h, r) {
    linear_extrude(height = h) rrect(w, d, r);
}

module ring2d(w, d, r, t) {
    difference() {
        rrect(w, d, r);
        rrect(w - 2 * t, d - 2 * t, r - t);
    }
}

// ---- Body shell -----------------------------------------------------------
module body_shell(W, D, H, wall, floor, rim, r) {
    difference() {
        rbox(W, D, H, r);
        translate([wall, wall, floor])
            rbox(W - 2 * wall, D - 2 * wall, H, r - wall);
    }
    // assento da gaxeta: rebaixo interno de 2.5 mm no topo
    translate([0, 0, H - 2.5])
        difference() {
            rbox(W - 2 * wall, D - 2 * wall, 2.5, r - wall);
            translate([rim - wall, rim - wall, -EPS])
                rbox(W - 2 * rim, D - 2 * rim, 2.5 + 2 * EPS, r - rim);
        }
}

module groove_cut(W, D, wall, r, H, gd) {
    translate([0, 0, H - gd])
        difference() {
            linear_extrude(height = gd + EPS)
                rrect(W - 2 * (wall + 0.75), D - 2 * (wall + 0.75), r - wall - 0.75);
            translate([0, 0, -EPS])
                linear_extrude(height = gd + 2 * EPS)
                    rrect(W - 2 * (wall + 4.25), D - 2 * (wall + 4.25), r - wall - 4.25);
        }
}

// ---- Fixacao ---------------------------------------------------------------
module screw_bosses(W, D, H, inset, list) {
    for (p = list)
        translate([p[0], p[1], 0])
            difference() {
                cylinder(h = H, d = SCREW_D);
                translate([0, 0, H - INSERT_H])
                    cylinder(h = INSERT_H + EPS, d = INSERT_D);
            }
}

module board_standoffs(pos, h, holes) {
    for (p = holes)
        translate([p[0], p[1], FLOOR])
            difference() {
                cylinder(h = h, d = BOARD_STANDOFF_D);
                translate([0, 0, h - 5])
                    cylinder(h = 5 + EPS, d = BOARD_HOLE_D);
            }
}

module bottom_door_bosses(W, D, list) {
    for (p = list)
        translate([p[0], p[1], 0])
            difference() {
                cylinder(h = 6, d = SCREW_D);
                translate([0, 0, -EPS])
                    cylinder(h = 6 + 2 * EPS, d = INSERT_D);
            }
}

// ---- Lid -----------------------------------------------------------------
module lid_plate(W, D, t, r, lip_outer, lip_inner, lip_h, screws_list) {
    union() {
        difference() {
            rbox(W, D, t, r);
            for (p = screws_list)
                translate([p[0], p[1], t - SCREW_HEAD_H])
                    cylinder(h = SCREW_HEAD_H + EPS, d = SCREW_HEAD_D);
        }
        // lip que entra no corpo
        translate([lip_outer, lip_outer, -lip_h])
            difference() {
                rbox(W - 2 * lip_outer, D - 2 * lip_outer, lip_h, r - lip_outer);
                translate([lip_inner - lip_outer, lip_inner - lip_outer, -EPS])
                    rbox(W - 2 * lip_inner, D - 2 * lip_inner, lip_h + 2 * EPS,
                         r - lip_inner);
            }
    }
}

module speaker_grille(cx, cy, z, d, hole_d, pitch, n) {
    for (i = [-n : n])
        for (j = [-n : n])
            if (i * i + j * j <= n * n)
                translate([cx + i * pitch, cy + j * pitch, z])
                    cylinder(h = LID_T + 2 * EPS, d = hole_d);
}

// ---- Cutouts -------------------------------------------------------------
module front_cut(x, z, w, h, wall) {
    translate([x, -EPS, z]) cube([w, wall + 2 * EPS, h]);
}

module right_cut(y, z, w, h, W, wall) {
    translate([W - wall - EPS, y, z]) cube([wall + 2 * EPS, w, h]);
}

module left_cut(y, z, w, h, wall) {
    translate([-EPS, y, z]) cube([wall + 2 * EPS, w, h]);
}

module back_hole(x, z, d, D, wall) {
    translate([x, D + EPS, z]) rotate([90, 0, 0])
        cylinder(h = wall + 2 * EPS, d = d);
}

module bottom_hole(x, y, d) {
    translate([x, y, -EPS]) cylinder(h = FLOOR + 2 * EPS, d = d);
}

module bottom_rect(x, y, w, d) {
    translate([x, y, -EPS]) rbox(w, d, FLOOR + 2 * EPS, 3);
}

// ---- Board / components (envelopes) --------------------------------------
module board_model(pos) {
    color("ForestGreen")
        translate(pos)
            difference() {
                cube([BOARD_W, BOARD_D, BOARD_T]);
                for (p = board_holes(pos))
                    translate([p[0] - pos[0], p[1] - pos[1], -EPS])
                        cylinder(h = BOARD_T + 2 * EPS, d = BOARD_HOLE_D);
            }
    // Q1 TO-220
    color("DimGray")
        translate([pos[0] + 56.5, pos[1] + 15.5, pos[2] + BOARD_T])
            cube([10, 5, 28.5]);
    // ESP32 DevKit (USB na borda de +Y local)
    color("RoyalBlue")
        translate([pos[0] + 18, pos[1] + 26.5, pos[2] + BOARD_T])
            cube([25.4, 48.5, 18]);
    // LoRa RA-02
    color("Purple")
        translate([pos[0] + 11, pos[1] + 28, pos[2] + BOARD_T])
            cube([33, 24, 3]);
    // conectores da borda direita
    for (y = [45, 49, 53, 56, 60, 65, 28, 16])
        color("Orange")
            translate([pos[0] + 71, pos[1] + y, pos[2] + BOARD_T])
                cube([4, 3, 7]);
    // J6 / J9 (borda inferior local)
    for (x = [61, 65])
        color("Orange")
            translate([pos[0] + x, pos[1] + 0.5, pos[2] + BOARD_T])
                cube([2.5, 2.5, 7]);
    // J11 OLED
    color("Orange")
        translate([pos[0] + 3, pos[1] + 62, pos[2] + BOARD_T])
        cube([5, 5, 7]);
}

module battery_2p(pos, size) {
    color("DarkOrange")
        translate(pos) cube(size);
}

module battery_3s2p(pos, size) {
    color("FireBrick")
        translate(pos) cube(size);
}

module relay2(pos, size) {
    color("SteelBlue")
        translate(pos) cube(size);
}

module endstop_mod(pos, size) {
    color("Goldenrod")
        translate(pos) cube(size);
}

module speaker_mod(pos, d, h) {
    color("Black")
        translate(pos)
            cylinder(h = h, d = d);
}

module oled_mod(pos, size) {
    color("MidnightBlue")
        translate(pos) cube(size);
}

module button_mod(pos, d, h) {
    color("Crimson")
        translate(pos) rotate([-90, 0, 0]) cylinder(h = h, d = d);
}

module guarded_switch(pos) {
    color("Red")
        translate(pos) cube([30, 30, 45]);
}

module rbf_flag(pos, size) {
    color("Red")
        translate(pos) cube(size);
}

module sma_mod(pos) {
    color("Silver")
        translate(pos) rotate([90, 0, 0]) cylinder(h = 12, d = 9);
}

module vent_mod(pos) {
    color("LightGray")
        translate(pos) rotate([0, 90, 0]) cylinder(h = 12, d = 12);
}

module fuse_wago(pos) {
    color("DarkGreen")
        translate(pos) cube([20, 30, 10]);
}

module bms_mod(pos, size) {
    color("DarkSlateGray")
        translate(pos) cube(size);
}
