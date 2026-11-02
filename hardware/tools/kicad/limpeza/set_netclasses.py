"""Escreve as netclasses nos .kicad_pro dos projetos do Ignitor.

Uso:
    python set_netclasses.py            # todos os projetos
    python set_netclasses.py pcbsmd     # so um projeto

pcbsmd (2 camadas, JLCPCB 1 oz):
    Default 0,2 mm / via 0,6-0,3 / clearance 0,2  (sinais)
    Power   0,8 mm / via 0,8-0,4 / clearance 0,25 (VIN, +5V_RELE, rele)
    IGN     2,5 mm / via 1,0-0,5 / clearance 0,3  (loop de ignicao 8 A, pulso)

pcbcnc (1 face B.Cu, fresagem caseira por isolamento, sem plano):
    Default 1,0 mm / via 1,4-0,8 / clearance 0,4  (toda a logica, GND incluso)
    IGN     2,5 mm / clearance 0,4                (loop de ignicao 8 A, pulso)
    Regras: min_track_width 0,6 (neck-downs curtos), anular 0,1 (TO-92);
    solder_mask_bridge ignorado (a placa caseira nao leva mascara) e
    pth_inside_courtyard ignorado (as ilhas de jumper JMPx ficam dentro dos
    courtyards dos modulos). As ligacoes que nao fecham viram fio jumper.

THT (pcbignicao/pcbcomando) mantem os valores historicos.
"""

import json
import sys

THT = r"hardware\kicad\pcbignicao\pcbignicao\pcbignicao.kicad_pro"
CMD = r"hardware\kicad\pcbignicao\pcbcomando\pcbcomando.kicad_pro"
SMD = r"hardware\kicad\pcbignicao\pcbignicao_smd\pcbsmd\pcbsmd.kicad_pro"
CNC = (r"hardware\kicad\pcbignicao\pcbignicao_CNC\pcbcnc"
       r"\pcbcnc.kicad_pro")

BASE = {
    "bus_width": 12,
    "diff_pair_gap": 0.25,
    "diff_pair_via_gap": 0.25,
    "diff_pair_width": 0.2,
    "line_style": 0,
    "microvia_diameter": 0.3,
    "microvia_drill": 0.1,
    "pcb_color": "rgba(0, 0, 0, 0.000)",
    "schematic_color": "rgba(0, 0, 0, 0.000)",
    "tuning_profile": "",
    "wire_width": 6,
}


def cls(name, priority, track, clearance, via_d, via_drill):
    d = dict(BASE)
    d.update(
        {
            "name": name,
            "priority": priority,
            "track_width": track,
            "clearance": clearance,
            "via_diameter": via_d,
            "via_drill": via_drill,
        }
    )
    order = [
        "bus_width",
        "clearance",
        "diff_pair_gap",
        "diff_pair_via_gap",
        "diff_pair_width",
        "line_style",
        "microvia_diameter",
        "microvia_drill",
        "name",
        "pcb_color",
        "priority",
        "schematic_color",
        "track_width",
        "tuning_profile",
        "via_diameter",
        "via_drill",
        "wire_width",
    ]
    return {k: d[k] for k in order}


CLASSES_THT = [
    cls("Default", 2147483647, 0.2, 0.2, 0.6, 0.3),
    cls("Power", 1, 0.5, 0.25, 0.8, 0.4),
    cls("IGN", 2, 1.0, 0.3, 1.0, 0.5),
]
PATTERNS_THT = [
    {"netclass": "Power", "pattern": "VSYS"},
    {"netclass": "Power", "pattern": "EXT_5V"},
    {"netclass": "IGN", "pattern": "IGN_A"},
    {"netclass": "IGN", "pattern": "IGN_B"},
]

CLASSES_SMD = [
    cls("Default", 2147483647, 0.2, 0.2, 0.6, 0.3),
    cls("Power", 1, 0.8, 0.25, 0.8, 0.4),
    cls("IGN", 2, 2.5, 0.25, 1.0, 0.5),
]
PATTERNS_SMD = [
    {"netclass": "Power", "pattern": "VIN"},
    {"netclass": "Power", "pattern": "+5V_RELE"},
    {"netclass": "Power", "pattern": "5V_RELE_S"},
    {"netclass": "Power", "pattern": "/rele/GND_RELAY"},
    {"netclass": "IGN", "pattern": "*Q1-D*"},
]

CLASSES_CNC = [
    cls("Default", 2147483647, 1.0, 0.4, 1.4, 0.8),
    cls("GND", 0, 1.0, 0.4, 1.4, 0.8),
    cls("IGN", 2, 2.5, 0.4, 1.4, 0.8),
]
PATTERNS_CNC = [
    {"netclass": "GND", "pattern": "GND"},
    {"netclass": "IGN", "pattern": "*Q1-D*"},
    {"netclass": "IGN", "pattern": "*Q1-S*"},
]
RULES_CNC = {
    "min_clearance": 0.2,
    "min_track_width": 0.6,
    "min_via_diameter": 1.4,
    "min_via_annular_width": 0.1,
    "min_groove_width": 0.2,
}
SEVERITIES_CNC = {
    "solder_mask_bridge": "ignore",
    "pth_inside_courtyard": "ignore",
}

PROJECTS = {
    "pcbignicao": (THT, CLASSES_THT, PATTERNS_THT, None, None),
    "pcbcomando": (CMD, CLASSES_THT, PATTERNS_THT, None, None),
    "pcbsmd": (SMD, CLASSES_SMD, PATTERNS_SMD, None, None),
    "pcbcnc": (CNC, CLASSES_CNC, PATTERNS_CNC, RULES_CNC, SEVERITIES_CNC),
}

sel = sys.argv[1] if len(sys.argv) > 1 else "all"
if sel != "all" and sel not in PROJECTS:
    raise SystemExit("projeto desconhecido: %s (use %s)" % (sel, ", ".join(PROJECTS)))

for name, (p, classes, patterns, rules, severities) in PROJECTS.items():
    if sel not in ("all", name):
        continue
    with open(p, encoding="utf-8") as fh:
        d = json.load(fh)
    ns = d.setdefault("net_settings", {})
    old = [c.get("name") for c in ns.get("classes", [])]
    ns["classes"] = classes
    ns["netclass_patterns"] = patterns
    extra = ""
    if rules:
        dst = d["board"]["design_settings"]["rules"]
        old_rules = {k: dst.get(k) for k in rules}
        dst.update(rules)
        extra = ", rules %s -> %s" % (old_rules, rules)
    if severities:
        dst = d["board"]["design_settings"]["rule_severities"]
        dst.update(severities)
        extra += ", severidades %s" % severities
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(d, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print("%-42s classes %s -> %s, %d patterns%s"
          % (p.split("\\")[-1], old, [c["name"] for c in classes],
             len(patterns), extra))
