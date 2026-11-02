// =============================================================================
//  Cupons de ensaio — gaxeta e inserto M3
//  part = 0 assembly | 1 gasket frame | 2 gasket lid | 3 insert coupon
// =============================================================================
include <lib/case_lib.scad>;

part = 0;

COUPON_SCREWS = [[20, 20], [80, 20], [20, 80], [80, 80]];

module gasket_frame() {
    difference() {
        union() {
            body_shell(100, 100, 12, 10, 4, 15, 6);
            screw_bosses(100, 100, 12, 20, COUPON_SCREWS);
        }
        groove_cut(100, 100, 10, 6, 12, GROOVE_D);
    }
}

module gasket_lid() {
    difference() {
        rbox(100, 100, 3.5, 6);
        for (p = COUPON_SCREWS)
            translate([p[0], p[1], -EPS])
                cylinder(h = 3.5 + 2 * EPS, d = 3.4);
    }
}

module insert_coupon() {
    difference() {
        union() {
            rbox(70, 20, 5, 3);
            for (x = [15, 35, 55])
                translate([x, 10, 0]) cylinder(h = 10, d = 7);
        }
        for (x = [15, 35, 55])
            translate([x, 10, 3]) cylinder(h = 7 + EPS, d = 4.2);
    }
}

module assembly() {
    color("WhiteSmoke", 0.5) gasket_frame();
    color("Gainsboro", 0.5) translate([0, 0, 12]) gasket_lid();
    color("SteelBlue", 0.5) translate([15, 0, 0]) insert_coupon();
}

if (part == 1) gasket_frame();
else if (part == 2) gasket_lid();
else if (part == 3) insert_coupon();
else assembly();
