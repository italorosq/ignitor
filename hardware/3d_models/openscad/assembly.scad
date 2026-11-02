// =============================================================================
//  Vista de conjunto — comando + ignicao lado a lado
// =============================================================================
include <params.scad>;

use <comando.scad>;
use <ignicao.scad>;

translate([0, 0, 0]) command_assembly();
translate([170, 0, 0]) ignition_assembly();
