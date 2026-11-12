# ignicao_smd — findings detalhados

## schematic.json
```json
{
 "total_components": 29,
 "unique_parts": 24,
 "dnp_parts": 0,
 "total_nets": 46,
 "total_wires": 54,
 "total_no_connects": 9,
 "component_types": {
  "transistor": 3,
  "resistor": 8,
  "connector": 10,
  "ic": 2,
  "led": 2,
  "capacitor": 3,
  "diode": 1
 },
 "power_rails": [
  {
   "name": "+3V3",
   "voltage": 3.3
  },
  {
   "name": "+5V_RELE",
   "voltage": 5.0
  },
  {
   "name": "5V_RELE_S",
   "voltage": 5.0
  },
  {
   "name": "GND",
   "voltage": null
  },
  {
   "name": "VIN",
   "voltage": null
  }
 ],
 "missing_mpn": [
  "Q1",
  "R6",
  "R4",
  "J7",
  "R5",
  "R2",
  "Q2",
  "J12",
  "J8",
  "Q4",
  "J10",
  "R3",
  "J3",
  "J5",
  "J2",
  "J4",
  "U1",
  "D3",
  "D4",
  "J11",
  "J1",
  "A1"
 ],
 "missing_footprint": []
}
```

### [info] CERT-001 — Wireless module detected: A1
```json
{
 "rule_id": "CERT-001",
 "severity": "info",
 "confidence": "heuristic",
 "detector": "suggest_certifications",
 "summary": "Wireless module detected: A1",
 "description": "FCC Part 15: Wireless module detected: A1",
 "evidence_source": "topology",
 "ctx.section": "Certifications"
}
```

### [info] DC-DET — Decoupling on +5V_RELE
```json
{
 "rule_id": "DC-DET",
 "severity": "info",
 "confidence": "deterministic",
 "detector": "detect_decoupling",
 "summary": "Decoupling on +5V_RELE",
 "description": "Decoupling capacitors on power rail +5V_RELE",
 "evidence_source": "topology",
 "ctx.section": "Decoupling"
}
```

### [info] DO-DET — IC A1 missing decoupling on +3V3, VIN
```json
{
 "rule_id": "DO-DET",
 "severity": "info",
 "confidence": "heuristic",
 "detector": "detect_design_observations",
 "summary": "IC A1 missing decoupling on +3V3, VIN",
 "description": "IC power pin(s) without decoupling capacitors",
 "evidence_source": "topology",
 "component": "A1",
 "ctx.section": "Design Observations"
}
```

### [info] DO-DET — Single-pin nets (7 nets)
```json
{
 "rule_id": "DO-DET",
 "severity": "info",
 "confidence": "heuristic",
 "detector": "detect_design_observations",
 "summary": "Single-pin nets (7 nets)",
 "description": "Signal nets connected to only one pin",
 "evidence_source": "topology",
 "ctx.section": "Design Observations"
}
```

### [info] DO-DET — Decoupling coverage on +5V_RELE
```json
{
 "rule_id": "DO-DET",
 "severity": "info",
 "confidence": "heuristic",
 "detector": "detect_design_observations",
 "summary": "Decoupling coverage on +5V_RELE",
 "description": "Decoupling frequency coverage for rail +5V_RELE",
 "evidence_source": "topology",
 "ctx.section": "Design Observations"
}
```

### [info] DO-DET — IC U1 missing decoupling on +3V3
```json
{
 "rule_id": "DO-DET",
 "severity": "info",
 "confidence": "heuristic",
 "detector": "detect_design_observations",
 "summary": "IC U1 missing decoupling on +3V3",
 "description": "IC power pin(s) without decoupling capacitors",
 "evidence_source": "topology",
 "component": "U1",
 "ctx.section": "Design Observations"
}
```

### [info] DO-DET — Reset pin on U1 (RESET)
```json
{
 "rule_id": "DO-DET",
 "severity": "info",
 "confidence": "heuristic",
 "detector": "detect_design_observations",
 "summary": "Reset pin on U1 (RESET)",
 "description": "Reset pin configuration for U1",
 "evidence_source": "topology",
 "net": "RESET",
 "component": "U1",
 "ctx.section": "Design Observations"
}
```

### [info] DS-003 — Datasheets present (8 files) but 19 of 24 unique BOM lines lack an MPN — those lines can't be cross-referenced.
```json
{
 "rule_id": "DS-003",
 "severity": "info",
 "confidence": "deterministic",
 "detector": "audit_datasheet_coverage",
 "summary": "Datasheets present (8 files) but 19 of 24 unique BOM lines lack an MPN — those lines can't be cross-referenced.",
 "recommendation": "Set the MPN field on the listed parts and re-sync datasheets so every BOM entry has manufacturer evidence.",
 "evidence_source": "bom",
 "ctx.section": "Datasheet Coverage",
 "ctx.impact": "Partial coverage: pin mapping and electrical claims for unmapped parts remain unverified."
}
```

### [info] EP-AUD — ESD audit J11 (generic): none coverage
```json
{
 "rule_id": "EP-AUD",
 "severity": "info",
 "confidence": "deterministic",
 "detector": "audit_esd_protection",
 "summary": "ESD audit J11 (generic): none coverage",
 "description": "ESD protection audit for generic connector J11: none coverage.",
 "evidence_source": "topology",
 "ctx.section": "ESD Protection"
}
```

### [info] EP-AUD — ESD audit J12 (generic): none coverage
```json
{
 "rule_id": "EP-AUD",
 "severity": "info",
 "confidence": "deterministic",
 "detector": "audit_esd_protection",
 "summary": "ESD audit J12 (generic): none coverage",
 "description": "ESD protection audit for generic connector J12: none coverage.",
 "evidence_source": "topology",
 "ctx.section": "ESD Protection"
}
```

### [info] EP-AUD — ESD audit J3 (header): none coverage
```json
{
 "rule_id": "EP-AUD",
 "severity": "info",
 "confidence": "deterministic",
 "detector": "audit_esd_protection",
 "summary": "ESD audit J3 (header): none coverage",
 "description": "ESD protection audit for header connector J3: none coverage.",
 "evidence_source": "topology",
 "ctx.section": "ESD Protection"
}
```

### [info] EP-AUD — ESD audit J4 (header): none coverage
```json
{
 "rule_id": "EP-AUD",
 "severity": "info",
 "confidence": "deterministic",
 "detector": "audit_esd_protection",
 "summary": "ESD audit J4 (header): none coverage",
 "description": "ESD protection audit for header connector J4: none coverage.",
 "evidence_source": "topology",
 "ctx.section": "ESD Protection"
}
```

### [info] EP-AUD — ESD audit J7 (generic): none coverage
```json
{
 "rule_id": "EP-AUD",
 "severity": "info",
 "confidence": "deterministic",
 "detector": "audit_esd_protection",
 "summary": "ESD audit J7 (generic): none coverage",
 "description": "ESD protection audit for generic connector J7: none coverage.",
 "evidence_source": "topology",
 "ctx.section": "ESD Protection"
}
```

### [info] EP-AUD — ESD audit J8 (generic): none coverage
```json
{
 "rule_id": "EP-AUD",
 "severity": "info",
 "confidence": "deterministic",
 "detector": "audit_esd_protection",
 "summary": "ESD audit J8 (generic): none coverage",
 "description": "ESD protection audit for generic connector J8: none coverage.",
 "evidence_source": "topology",
 "ctx.section": "ESD Protection"
}
```

### [info] LA-AUD — LED D3 (LED) [resistor_limited]
```json
{
 "rule_id": "LA-AUD",
 "severity": "info",
 "confidence": "deterministic",
 "detector": "audit_led_circuits",
 "summary": "LED D3 (LED) [resistor_limited]",
 "description": "LED audit: D3 using resistor_limited drive method.",
 "evidence_source": "topology",
 "ctx.section": "LED Audit"
}
```

### [info] LA-AUD — LED D4 (LED) [resistor_limited]
```json
{
 "rule_id": "LA-AUD",
 "severity": "info",
 "confidence": "deterministic",
 "detector": "audit_led_circuits",
 "summary": "LED D4 (LED) [resistor_limited]",
 "description": "LED audit: D4 using resistor_limited drive method.",
 "evidence_source": "topology",
 "ctx.section": "LED Audit"
}
```

### [warning] NT-001 — Single-pin net: ADC1 only connects to A1.19 (ADC1_CH6/D34) (bidirectional)
```json
{
 "rule_id": "NT-001",
 "severity": "warning",
 "confidence": "deterministic",
 "detector": "analyze_connectivity",
 "summary": "Single-pin net: ADC1 only connects to A1.19 (ADC1_CH6/D34) (bidirectional)",
 "description": "Net 'ADC1' has exactly one pin: A1.19 (ADC1_CH6/D34), pin_type='bidirectional'. Verify the intended target — if this pin should connect somewhere, the wire/label is missing.",
 "recommendation": "Check the schematic at the referenced pin — add the missing wire or place a no-connect marker if the pin is intentionally floating.",
 "evidence_source": "topology",
 "ctx.section": "Connectivity",
 "ctx.impact": "Likely unfinished wiring: a driven or powered pin has no counterpart."
}
```

### [warning] NT-001 — Single-pin net: ADC2 only connects to A1.20 (ADC1_CH7/D35) (bidirectional)
```json
{
 "rule_id": "NT-001",
 "severity": "warning",
 "confidence": "deterministic",
 "detector": "analyze_connectivity",
 "summary": "Single-pin net: ADC2 only connects to A1.20 (ADC1_CH7/D35) (bidirectional)",
 "description": "Net 'ADC2' has exactly one pin: A1.20 (ADC1_CH7/D35), pin_type='bidirectional'. Verify the intended target — if this pin should connect somewhere, the wire/label is missing.",
 "recommendation": "Check the schematic at the referenced pin — add the missing wire or place a no-connect marker if the pin is intentionally floating.",
 "evidence_source": "topology",
 "ctx.section": "Connectivity",
 "ctx.impact": "Likely unfinished wiring: a driven or powered pin has no counterpart."
}
```

### [warning] NT-001 — Single-pin net: EXP1 only connects to A1.17 (ADC1_CH0/VP) (bidirectional)
```json
{
 "rule_id": "NT-001",
 "severity": "warning",
 "confidence": "deterministic",
 "detector": "analyze_connectivity",
 "summary": "Single-pin net: EXP1 only connects to A1.17 (ADC1_CH0/VP) (bidirectional)",
 "description": "Net 'EXP1' has exactly one pin: A1.17 (ADC1_CH0/VP), pin_type='bidirectional'. Verify the intended target — if this pin should connect somewhere, the wire/label is missing.",
 "recommendation": "Check the schematic at the referenced pin — add the missing wire or place a no-connect marker if the pin is intentionally floating.",
 "evidence_source": "topology",
 "ctx.section": "Connectivity",
 "ctx.impact": "Likely unfinished wiring: a driven or powered pin has no counterpart."
}
```

### [warning] NT-001 — Single-pin net: EXP2 only connects to A1.18 (ADC1_CH3/VN) (bidirectional)
```json
{
 "rule_id": "NT-001",
 "severity": "warning",
 "confidence": "deterministic",
 "detector": "analyze_connectivity",
 "summary": "Single-pin net: EXP2 only connects to A1.18 (ADC1_CH3/VN) (bidirectional)",
 "description": "Net 'EXP2' has exactly one pin: A1.18 (ADC1_CH3/VN), pin_type='bidirectional'. Verify the intended target — if this pin should connect somewhere, the wire/label is missing.",
 "recommendation": "Check the schematic at the referenced pin — add the missing wire or place a no-connect marker if the pin is intentionally floating.",
 "evidence_source": "topology",
 "ctx.section": "Connectivity",
 "ctx.impact": "Likely unfinished wiring: a driven or powered pin has no counterpart."
}
```

### [warning] NT-001 — Single-pin net: EXP_A only connects to A1.4 (D2/ADC2_CH2) (bidirectional)
```json
{
 "rule_id": "NT-001",
 "severity": "warning",
 "confidence": "deterministic",
 "detector": "analyze_connectivity",
 "summary": "Single-pin net: EXP_A only connects to A1.4 (D2/ADC2_CH2) (bidirectional)",
 "description": "Net 'EXP_A' has exactly one pin: A1.4 (D2/ADC2_CH2), pin_type='bidirectional'. Verify the intended target — if this pin should connect somewhere, the wire/label is missing.",
 "recommendation": "Check the schematic at the referenced pin — add the missing wire or place a no-connect marker if the pin is intentionally floating.",
 "evidence_source": "topology",
 "ctx.section": "Connectivity",
 "ctx.impact": "Likely unfinished wiring: a driven or powered pin has no counterpart."
}
```

### [warning] NT-001 — Single-pin net: EXP_B only connects to A1.8 (D5) (bidirectional)
```json
{
 "rule_id": "NT-001",
 "severity": "warning",
 "confidence": "deterministic",
 "detector": "analyze_connectivity",
 "summary": "Single-pin net: EXP_B only connects to A1.8 (D5) (bidirectional)",
 "description": "Net 'EXP_B' has exactly one pin: A1.8 (D5), pin_type='bidirectional'. Verify the intended target — if this pin should connect somewhere, the wire/label is missing.",
 "recommendation": "Check the schematic at the referenced pin — add the missing wire or place a no-connect marker if the pin is intentionally floating.",
 "evidence_source": "topology",
 "ctx.section": "Connectivity",
 "ctx.impact": "Likely unfinished wiring: a driven or powered pin has no counterpart."
}
```

### [warning] NT-001 — Single-pin net: EXP_C only connects to A1.3 (D15/ADC2_CH3) (bidirectional)
```json
{
 "rule_id": "NT-001",
 "severity": "warning",
 "confidence": "deterministic",
 "detector": "analyze_connectivity",
 "summary": "Single-pin net: EXP_C only connects to A1.3 (D15/ADC2_CH3) (bidirectional)",
 "description": "Net 'EXP_C' has exactly one pin: A1.3 (D15/ADC2_CH3), pin_type='bidirectional'. Verify the intended target — if this pin should connect somewhere, the wire/label is missing.",
 "recommendation": "Check the schematic at the referenced pin — add the missing wire or place a no-connect marker if the pin is intentionally floating.",
 "evidence_source": "topology",
 "ctx.section": "Connectivity",
 "ctx.impact": "Likely unfinished wiring: a driven or powered pin has no counterpart."
}
```

### [warning] PU-001 — A1 pin D22/SCL (OLED_SCL) missing pull-up resistor
```json
{
 "rule_id": "PU-001",
 "severity": "warning",
 "confidence": "heuristic",
 "detector": "validate_pullups",
 "summary": "A1 pin D22/SCL (OLED_SCL) missing pull-up resistor",
 "description": "Pin D22/SCL on A1 (ESP32) is connected to net OLED_SCL but has no pull-up resistor. This pin type typically requires an external pull-up to a power rail for correct operation.",
 "recommendation": "Add a 4.7k-10k pull-up resistor from OLED_SCL to the appropriate power rail.",
 "evidence_source": "topology",
 "ctx.section": "Signal Integrity",
 "ctx.impact": "Pin may float or bus may not function without pull-up"
}
```

### [warning] PU-001 — A1 pin D21/SDA (OLED_SDA) missing pull-up resistor
```json
{
 "rule_id": "PU-001",
 "severity": "warning",
 "confidence": "heuristic",
 "detector": "validate_pullups",
 "summary": "A1 pin D21/SDA (OLED_SDA) missing pull-up resistor",
 "description": "Pin D21/SDA on A1 (ESP32) is connected to net OLED_SDA but has no pull-up resistor. This pin type typically requires an external pull-up to a power rail for correct operation.",
 "recommendation": "Add a 4.7k-10k pull-up resistor from OLED_SDA to the appropriate power rail.",
 "evidence_source": "topology",
 "ctx.section": "Signal Integrity",
 "ctx.impact": "Pin may float or bus may not function without pull-up"
}
```

### [warning] PU-001 — A1 pin EN (__unnamed_15) missing pull-up resistor
```json
{
 "rule_id": "PU-001",
 "severity": "warning",
 "confidence": "heuristic",
 "detector": "validate_pullups",
 "summary": "A1 pin EN (__unnamed_15) missing pull-up resistor",
 "description": "Pin EN on A1 (ESP32) is connected to net __unnamed_15 but has no pull-up resistor. This pin type typically requires an external pull-up to a power rail for correct operation.",
 "recommendation": "Add a 4.7k-10k pull-up resistor from __unnamed_15 to the appropriate power rail.",
 "evidence_source": "topology",
 "ctx.section": "Signal Integrity",
 "ctx.impact": "Pin may float or bus may not function without pull-up"
}
```

### [warning] RS-001 — +5V_RELE has no declared source
```json
{
 "rule_id": "RS-001",
 "severity": "warning",
 "confidence": "deterministic",
 "detector": "audit_rail_sources",
 "summary": "+5V_RELE has no declared source",
 "description": "Net +5V_RELE carries power_in pins but has no power_out pin, no PWR_FLAG, no regulator output mapping, and no bridged solder jumper path to a sourced net.",
 "recommendation": "Add a PWR_FLAG to declare the rail as externally powered (e.g. from a connector) or trace the rail back to a regulator output. If the source lives on another sheet, promote the net name to a global label.",
 "evidence_source": "topology",
 "ctx.section": "Power — Rail Sources",
 "ctx.impact": "Rail has no source visible to the analyser; likely a wiring gap or missing PWR_FLAG."
}
```

### [warning] RS-001 — 5V_RELE_S has no declared source
```json
{
 "rule_id": "RS-001",
 "severity": "warning",
 "confidence": "deterministic",
 "detector": "audit_rail_sources",
 "summary": "5V_RELE_S has no declared source",
 "description": "Net 5V_RELE_S carries power_in pins but has no power_out pin, no PWR_FLAG, no regulator output mapping, and no bridged solder jumper path to a sourced net.",
 "recommendation": "Add a PWR_FLAG to declare the rail as externally powered (e.g. from a connector) or trace the rail back to a regulator output. If the source lives on another sheet, promote the net name to a global label.",
 "evidence_source": "topology",
 "ctx.section": "Power — Rail Sources",
 "ctx.impact": "Rail has no source visible to the analyser; likely a wiring gap or missing PWR_FLAG."
}
```

### [error] SS-001 — Sourcing blocker: BOM has <50% MPN coverage (5/24 unique parts). Board is not pre-fab ready.
```json
{
 "rule_id": "SS-001",
 "severity": "error",
 "confidence": "deterministic",
 "detector": "audit_sourcing_gate",
 "summary": "Sourcing blocker: BOM has <50% MPN coverage (5/24 unique parts). Board is not pre-fab ready.",
 "description": "Sourcing audit: 5 of 24 unique BOM lines (grouped by value + footprint) carry a manufacturer part number (20.8%). Pre-fab readiness requires 100% coverage; production assembly requires all parts sourceable via one of the supported distributors.",
 "recommendation": "Populate the MPN field on the listed refs (use the digikey / mouser / lcsc / element14 skill to search by value/footprint when the MPN isn't already known).",
 "evidence_source": "bom",
 "ctx.section": "Sourcing",
 "ctx.impact": "Pre-fab gate: board cannot be ordered until MPN coverage reaches 100%."
}
```

### [info] TR-DET — Transistor Q1 mosfet
```json
{
 "rule_id": "TR-DET",
 "severity": "info",
 "confidence": "deterministic",
 "detector": "detect_transistor_circuits",
 "summary": "Transistor Q1 mosfet",
 "description": "Transistor circuit (mosfet) detected",
 "evidence_source": "topology",
 "reference": "Q1",
 "ctx.section": "Discrete Semiconductors"
}
```

### [info] TR-DET — Transistor Q2 bjt
```json
{
 "rule_id": "TR-DET",
 "severity": "info",
 "confidence": "deterministic",
 "detector": "detect_transistor_circuits",
 "summary": "Transistor Q2 bjt",
 "description": "BJT transistor circuit detected",
 "evidence_source": "topology",
 "reference": "Q2",
 "ctx.section": "Discrete Semiconductors"
}
```

### [info] TR-DET — Transistor Q4 bjt
```json
{
 "rule_id": "TR-DET",
 "severity": "info",
 "confidence": "deterministic",
 "detector": "detect_transistor_circuits",
 "summary": "Transistor Q4 bjt",
 "description": "BJT transistor circuit detected",
 "evidence_source": "topology",
 "reference": "Q4",
 "ctx.section": "Discrete Semiconductors"
}
```

### [info] WL-001 — wifi/ble module A1 (ESP32)
```json
{
 "rule_id": "WL-001",
 "severity": "info",
 "confidence": "deterministic",
 "detector": "detect_wireless_modules",
 "summary": "wifi/ble module A1 (ESP32)",
 "description": "Detected wifi_ble wireless module A1 (ESP32).",
 "evidence_source": "topology",
 "reference": "A1",
 "ctx.section": "Wireless"
}
```

### [info] LC-007 — Lifecycle audit not run — --lifecycle flag not passed
```json
{
 "rule_id": "LC-007",
 "severity": "info",
 "confidence": "deterministic",
 "detector": "audit_lifecycle_skipped",
 "summary": "Lifecycle audit not run — --lifecycle flag not passed",
 "description": "Component lifecycle / obsolescence audit was not run this session. Reason: --lifecycle flag not passed (run with --lifecycle to query DigiKey / Mouser / LCSC / element14 for obsolescence + operating-temp coverage; requires network + API keys). The review cannot report active / NRND / EOL / obsolete status, last-time-buy windows, or operating-temperature coverage for any BOM part. Treat the lifecycle section of the report as 'not performed'.",
 "recommendation": "Run with --lifecycle (requires DIGIKEY_CLIENT_ID / MOUSER_SEARCH_API_KEY / ELEMENT14_API_KEY env vars; LCSC needs no auth) to populate this section. If intentionally skipped, note it explicitly in the report's 'Not Performed' section.",
 "evidence_source": "topology",
 "ctx.section": "Component Lifecycle",
 "ctx.impact": "No obsolescence / temperature-grade evidence available."
}
```

## pcb.json
```json
{
 "footprint_count": 30,
 "front_side": 29,
 "back_side": 1,
 "smd_count": 13,
 "tht_count": 16,
 "copper_layers_used": 2,
 "copper_layer_names": [
  "B.Cu",
  "F.Cu"
 ],
 "track_segments": 161,
 "via_count": 10,
 "zone_count": 1,
 "total_track_length_mm": 796.13,
 "board_width_mm": 78.82,
 "board_height_mm": 57.25,
 "board_area_mm2": 4512.4,
 "net_count": 46,
 "routing_complete": true,
 "unrouted_net_count": 0
}
```

### [info] CC-DET — Power net +3V3: 0.5mm min trace
```json
{
 "rule_id": "CC-DET",
 "severity": "info",
 "confidence": "deterministic",
 "detector": "analyze_current_capacity",
 "summary": "Power net +3V3: 0.5mm min trace",
 "description": "Power/ground net +3V3: min trace 0.5mm, max 1.0mm, 7 segments.",
 "evidence_source": "topology",
 "net": "+3V3",
 "ctx.section": "Current Capacity",
 "ctx.impact": "Power delivery",
 "ctx.standard_ref": "IPC-2221"
}
```

### [info] CC-DET — Power net +5V_RELE: 0.8mm min trace
```json
{
 "rule_id": "CC-DET",
 "severity": "info",
 "confidence": "deterministic",
 "detector": "analyze_current_capacity",
 "summary": "Power net +5V_RELE: 0.8mm min trace",
 "description": "Power/ground net +5V_RELE: min trace 0.8mm, max 0.8mm, 10 segments.",
 "evidence_source": "topology",
 "net": "+5V_RELE",
 "ctx.section": "Current Capacity",
 "ctx.impact": "Power delivery",
 "ctx.standard_ref": "IPC-2221"
}
```

### [info] CC-DET — Power net /rele/GND_RELAY: 0.8mm min trace
```json
{
 "rule_id": "CC-DET",
 "severity": "info",
 "confidence": "deterministic",
 "detector": "analyze_current_capacity",
 "summary": "Power net /rele/GND_RELAY: 0.8mm min trace",
 "description": "Power/ground net /rele/GND_RELAY: min trace 0.8mm, max 0.8mm, 4 segments.",
 "evidence_source": "topology",
 "net": "/rele/GND_RELAY",
 "ctx.section": "Current Capacity",
 "ctx.impact": "Power delivery",
 "ctx.standard_ref": "IPC-2221"
}
```

### [info] CC-DET — Power net 5V_RELE_S: 0.8mm min trace
```json
{
 "rule_id": "CC-DET",
 "severity": "info",
 "confidence": "deterministic",
 "detector": "analyze_current_capacity",
 "summary": "Power net 5V_RELE_S: 0.8mm min trace",
 "description": "Power/ground net 5V_RELE_S: min trace 0.8mm, max 0.8mm, 1 segments.",
 "evidence_source": "topology",
 "net": "5V_RELE_S",
 "ctx.section": "Current Capacity",
 "ctx.impact": "Power delivery",
 "ctx.standard_ref": "IPC-2221"
}
```

### [info] CC-DET — Power net GNDBUZZ: 0.5mm min trace
```json
{
 "rule_id": "CC-DET",
 "severity": "info",
 "confidence": "deterministic",
 "detector": "analyze_current_capacity",
 "summary": "Power net GNDBUZZ: 0.5mm min trace",
 "description": "Power/ground net GNDBUZZ: min trace 0.5mm, max 0.5mm, 2 segments.",
 "evidence_source": "topology",
 "net": "GNDBUZZ",
 "ctx.section": "Current Capacity",
 "ctx.impact": "Power delivery",
 "ctx.standard_ref": "IPC-2221"
}
```

### [info] CC-DET — Power net VIN: 0.8mm min trace
```json
{
 "rule_id": "CC-DET",
 "severity": "info",
 "confidence": "deterministic",
 "detector": "analyze_current_capacity",
 "summary": "Power net VIN: 0.8mm min trace",
 "description": "Power/ground net VIN: min trace 0.8mm, max 0.8mm, 4 segments.",
 "evidence_source": "topology",
 "net": "VIN",
 "ctx.section": "Current Capacity",
 "ctx.impact": "Power delivery",
 "ctx.standard_ref": "IPC-2221"
}
```

### [info] CP-002 — No opposite-layer copper under J10
```json
{
 "rule_id": "CP-002",
 "severity": "info",
 "confidence": "deterministic",
 "detector": "analyze_copper_presence",
 "summary": "No opposite-layer copper under J10",
 "description": "Component J10 has no copper zone on the opposite layer.",
 "evidence_source": "geometry",
 "component": "J10",
 "ctx.section": "Copper Integrity",
 "ctx.impact": "Return path / shielding"
}
```

### [info] CP-002 — No opposite-layer copper under J3
```json
{
 "rule_id": "CP-002",
 "severity": "info",
 "confidence": "deterministic",
 "detector": "analyze_copper_presence",
 "summary": "No opposite-layer copper under J3",
 "description": "Component J3 has no copper zone on the opposite layer.",
 "evidence_source": "geometry",
 "component": "J3",
 "ctx.section": "Copper Integrity",
 "ctx.impact": "Return path / shielding"
}
```

### [info] CP-002 — No opposite-layer copper under J4
```json
{
 "rule_id": "CP-002",
 "severity": "info",
 "confidence": "deterministic",
 "detector": "analyze_copper_presence",
 "summary": "No opposite-layer copper under J4",
 "description": "Component J4 has no copper zone on the opposite layer.",
 "evidence_source": "geometry",
 "component": "J4",
 "ctx.section": "Copper Integrity",
 "ctx.impact": "Return path / shielding"
}
```

### [info] CP-002 — No opposite-layer copper under J7
```json
{
 "rule_id": "CP-002",
 "severity": "info",
 "confidence": "deterministic",
 "detector": "analyze_copper_presence",
 "summary": "No opposite-layer copper under J7",
 "description": "Component J7 has no copper zone on the opposite layer.",
 "evidence_source": "geometry",
 "component": "J7",
 "ctx.section": "Copper Integrity",
 "ctx.impact": "Return path / shielding"
}
```

### [info] CP-002 — No opposite-layer copper under J8
```json
{
 "rule_id": "CP-002",
 "severity": "info",
 "confidence": "deterministic",
 "detector": "analyze_copper_presence",
 "summary": "No opposite-layer copper under J8",
 "description": "Component J8 has no copper zone on the opposite layer.",
 "evidence_source": "geometry",
 "component": "J8",
 "ctx.section": "Copper Integrity",
 "ctx.impact": "Return path / shielding"
}
```

### [info] FD-001 — No fiducials on F.Cu (12 SMD components) (finest pad dim 1.13mm — coarse pitch only)
```json
{
 "rule_id": "FD-001",
 "severity": "info",
 "confidence": "deterministic",
 "detector": "analyze_fiducials",
 "summary": "No fiducials on F.Cu (12 SMD components) (finest pad dim 1.13mm — coarse pitch only)",
 "description": "F.Cu has 0 fiducial(s) but 12 SMD components. Assembly machines need >= 3 fiducials for accurate placement.",
 "recommendation": "Add fiducial markers for pick-and-place alignment (3 per side with SMD).",
 "evidence_source": "topology",
 "ctx.section": "Assembly",
 "ctx.impact": "Pick-and-place alignment",
 "ctx.standard_ref": "IPC-7351"
}
```

### [info] PM-001 — Courtyard overlap between D1 and A1 (11.232mm²) (courtyard includes RF keepout — verify neighbor is outside the antenna keepout, not a body collision)
```json
{
 "rule_id": "PM-001",
 "severity": "info",
 "confidence": "deterministic",
 "detector": "analyze_placement",
 "summary": "Courtyard overlap between D1 and A1 (11.232mm²) (courtyard includes RF keepout — verify neighbor is outside the antenna keepout, not a body collision)",
 "description": "Components D1 and A1 have overlapping courtyards on F.Cu (11.232mm² overlap area). Threshold: ≥1.0mm² = error, else warning; RF-module overlaps demote to info (courtyard encodes RF keepout).",
 "recommendation": "Resolve courtyard overlap between D1 and A1 — move components apart or adjust courtyard geometry",
 "evidence_source": "topology",
 "ctx.section": "Placement",
 "ctx.impact": "assembly"
}
```

### [info] PM-001 — Courtyard overlap between D3 and A1 (41.281mm²) (courtyard includes RF keepout — verify neighbor is outside the antenna keepout, not a body collision)
```json
{
 "rule_id": "PM-001",
 "severity": "info",
 "confidence": "deterministic",
 "detector": "analyze_placement",
 "summary": "Courtyard overlap between D3 and A1 (41.281mm²) (courtyard includes RF keepout — verify neighbor is outside the antenna keepout, not a body collision)",
 "description": "Components D3 and A1 have overlapping courtyards on F.Cu (41.281mm² overlap area). Threshold: ≥1.0mm² = error, else warning; RF-module overlaps demote to info (courtyard encodes RF keepout).",
 "recommendation": "Resolve courtyard overlap between D3 and A1 — move components apart or adjust courtyard geometry",
 "evidence_source": "topology",
 "ctx.section": "Placement",
 "ctx.impact": "assembly"
}
```

### [info] PM-001 — Courtyard overlap between D4 and A1 (41.281mm²) (courtyard includes RF keepout — verify neighbor is outside the antenna keepout, not a body collision)
```json
{
 "rule_id": "PM-001",
 "severity": "info",
 "confidence": "deterministic",
 "detector": "analyze_placement",
 "summary": "Courtyard overlap between D4 and A1 (41.281mm²) (courtyard includes RF keepout — verify neighbor is outside the antenna keepout, not a body collision)",
 "description": "Components D4 and A1 have overlapping courtyards on F.Cu (41.281mm² overlap area). Threshold: ≥1.0mm² = error, else warning; RF-module overlaps demote to info (courtyard encodes RF keepout).",
 "recommendation": "Resolve courtyard overlap between D4 and A1 — move components apart or adjust courtyard geometry",
 "evidence_source": "topology",
 "ctx.section": "Placement",
 "ctx.impact": "assembly"
}
```

### [info] PM-001 — Courtyard overlap between R1 and A1 (2.56mm²) (courtyard includes RF keepout — verify neighbor is outside the antenna keepout, not a body collision)
```json
{
 "rule_id": "PM-001",
 "severity": "info",
 "confidence": "deterministic",
 "detector": "analyze_placement",
 "summary": "Courtyard overlap between R1 and A1 (2.56mm²) (courtyard includes RF keepout — verify neighbor is outside the antenna keepout, not a body collision)",
 "description": "Components R1 and A1 have overlapping courtyards on F.Cu (2.56mm² overlap area). Threshold: ≥1.0mm² = error, else warning; RF-module overlaps demote to info (courtyard encodes RF keepout).",
 "recommendation": "Resolve courtyard overlap between R1 and A1 — move components apart or adjust courtyard geometry",
 "evidence_source": "topology",
 "ctx.section": "Placement",
 "ctx.impact": "assembly"
}
```

### [info] PM-001 — Courtyard overlap between R3 and A1 (2.56mm²) (courtyard includes RF keepout — verify neighbor is outside the antenna keepout, not a body collision)
```json
{
 "rule_id": "PM-001",
 "severity": "info",
 "confidence": "deterministic",
 "detector": "analyze_placement",
 "summary": "Courtyard overlap between R3 and A1 (2.56mm²) (courtyard includes RF keepout — verify neighbor is outside the antenna keepout, not a body collision)",
 "description": "Components R3 and A1 have overlapping courtyards on F.Cu (2.56mm² overlap area). Threshold: ≥1.0mm² = error, else warning; RF-module overlaps demote to info (courtyard encodes RF keepout).",
 "recommendation": "Resolve courtyard overlap between R3 and A1 — move components apart or adjust courtyard geometry",
 "evidence_source": "topology",
 "ctx.section": "Placement",
 "ctx.impact": "assembly"
}
```

### [info] PM-001 — Courtyard overlap between R7 and A1 (2.56mm²) (courtyard includes RF keepout — verify neighbor is outside the antenna keepout, not a body collision)
```json
{
 "rule_id": "PM-001",
 "severity": "info",
 "confidence": "deterministic",
 "detector": "analyze_placement",
 "summary": "Courtyard overlap between R7 and A1 (2.56mm²) (courtyard includes RF keepout — verify neighbor is outside the antenna keepout, not a body collision)",
 "description": "Components R7 and A1 have overlapping courtyards on F.Cu (2.56mm² overlap area). Threshold: ≥1.0mm² = error, else warning; RF-module overlaps demote to info (courtyard encodes RF keepout).",
 "recommendation": "Resolve courtyard overlap between R7 and A1 — move components apart or adjust courtyard geometry",
 "evidence_source": "topology",
 "ctx.section": "Placement",
 "ctx.impact": "assembly"
}
```

### [info] PM-001 — Courtyard overlap between R8 and A1 (2.56mm²) (courtyard includes RF keepout — verify neighbor is outside the antenna keepout, not a body collision)
```json
{
 "rule_id": "PM-001",
 "severity": "info",
 "confidence": "deterministic",
 "detector": "analyze_placement",
 "summary": "Courtyard overlap between R8 and A1 (2.56mm²) (courtyard includes RF keepout — verify neighbor is outside the antenna keepout, not a body collision)",
 "description": "Components R8 and A1 have overlapping courtyards on F.Cu (2.56mm² overlap area). Threshold: ≥1.0mm² = error, else warning; RF-module overlaps demote to info (courtyard encodes RF keepout).",
 "recommendation": "Resolve courtyard overlap between R8 and A1 — move components apart or adjust courtyard geometry",
 "evidence_source": "topology",
 "ctx.section": "Placement",
 "ctx.impact": "assembly"
}
```

### [info] PM-002 — J12 courtyard overhangs board edge by 0.44mm
```json
{
 "rule_id": "PM-002",
 "severity": "info",
 "confidence": "deterministic",
 "detector": "analyze_placement",
 "summary": "J12 courtyard overhangs board edge by 0.44mm",
 "description": "Component J12 on F.Cu has a courtyard extending 0.44mm past the board outline. If not intentional (castellated or edge-mount part), it will collide with the edge.",
 "recommendation": "Verify the overhang on J12 is intentional; if not, place it inside the outline.",
 "evidence_source": "topology",
 "component": "J12",
 "ctx.section": "Placement",
 "ctx.impact": "manufacturability"
}
```

### [warning] TE-001 — Test point coverage: 0/42 nets (0%)
```json
{
 "rule_id": "TE-001",
 "severity": "warning",
 "confidence": "deterministic",
 "detector": "analyze_test_point_coverage",
 "summary": "Test point coverage: 0/42 nets (0%)",
 "description": "0 of 42 signal nets have test points (0% coverage).",
 "recommendation": "Add test points to improve ICT/flying probe coverage.",
 "evidence_source": "topology",
 "ctx.section": "Testability",
 "ctx.impact": "ICT accessibility"
}
```

## cross_analysis.json

### [warning] VS-002 — No ground stitching vias found
```json
{
 "rule_id": "VS-002",
 "severity": "warning",
 "confidence": "deterministic",
 "detector": "check_via_stitching_density",
 "summary": "No ground stitching vias found",
 "description": "The board has no ground vias. Ground stitching vias are important for EMC.",
 "recommendation": "Add ground stitching vias at <= 73mm spacing.",
 "evidence_source": "topology",
 "ctx.section": "Via Stitching",
 "ctx.impact": "Poor ground plane connectivity between layers"
}
```

## emc.json

### [error] GP-001 — Signal has major reference plane gap
```json
{
 "rule_id": "GP-001",
 "severity": "error",
 "confidence": "heuristic",
 "detector": "emc_ground_plane",
 "summary": "Signal has major reference plane gap",
 "description": "Net RELE_IN has 33% reference plane coverage over 20.5mm of routing. Return current must detour around the gap, creating a loop antenna.",
 "recommendation": "Route this signal to avoid ground plane gaps, or fill the void. If a split is intentional, add a bridge capacitor across the gap.",
 "evidence_source": "heuristic_rule",
 "ctx.section": "Ground Plane"
}
```

### [error] GP-001 — Signal has significant reference plane gap
```json
{
 "rule_id": "GP-001",
 "severity": "error",
 "confidence": "heuristic",
 "detector": "emc_ground_plane",
 "summary": "Signal has significant reference plane gap",
 "description": "Net Net-(Q2-B) has 59% reference plane coverage over 13.9mm of routing. Return current must detour around the gap, creating a loop antenna.",
 "recommendation": "Route this signal to avoid ground plane gaps, or fill the void. If a split is intentional, add a bridge capacitor across the gap.",
 "evidence_source": "heuristic_rule",
 "ctx.section": "Ground Plane"
}
```

### [error] GP-001 — Signal has significant reference plane gap
```json
{
 "rule_id": "GP-001",
 "severity": "error",
 "confidence": "heuristic",
 "detector": "emc_ground_plane",
 "summary": "Signal has significant reference plane gap",
 "description": "Net Net-(D4-Pad2) has 70% reference plane coverage over 10.6mm of routing. Return current must detour around the gap, creating a loop antenna.",
 "recommendation": "Route this signal to avoid ground plane gaps, or fill the void. If a split is intentional, add a bridge capacitor across the gap.",
 "evidence_source": "heuristic_rule",
 "ctx.section": "Ground Plane"
}
```

### [error] GP-001 — Signal has significant reference plane gap
```json
{
 "rule_id": "GP-001",
 "severity": "error",
 "confidence": "heuristic",
 "detector": "emc_ground_plane",
 "summary": "Signal has significant reference plane gap",
 "description": "Net MISO has 70% reference plane coverage over 18.2mm of routing. Return current must detour around the gap, creating a loop antenna.",
 "recommendation": "Route this signal to avoid ground plane gaps, or fill the void. If a split is intentional, add a bridge capacitor across the gap.",
 "evidence_source": "heuristic_rule",
 "ctx.section": "Ground Plane"
}
```

### [error] GP-001 — Signal has significant reference plane gap
```json
{
 "rule_id": "GP-001",
 "severity": "error",
 "confidence": "heuristic",
 "detector": "emc_ground_plane",
 "summary": "Signal has significant reference plane gap",
 "description": "Net SCK has 75% reference plane coverage over 21.8mm of routing. Return current must detour around the gap, creating a loop antenna.",
 "recommendation": "Route this signal to avoid ground plane gaps, or fill the void. If a split is intentional, add a bridge capacitor across the gap.",
 "evidence_source": "heuristic_rule",
 "ctx.section": "Ground Plane"
}
```

### [error] GP-001 — Signal has significant reference plane gap
```json
{
 "rule_id": "GP-001",
 "severity": "error",
 "confidence": "heuristic",
 "detector": "emc_ground_plane",
 "summary": "Signal has significant reference plane gap",
 "description": "Net NSS has 75% reference plane coverage over 26.3mm of routing. Return current must detour around the gap, creating a loop antenna.",
 "recommendation": "Route this signal to avoid ground plane gaps, or fill the void. If a split is intentional, add a bridge capacitor across the gap.",
 "evidence_source": "heuristic_rule",
 "ctx.section": "Ground Plane"
}
```

### [error] GP-001 — Signal has significant reference plane gap
```json
{
 "rule_id": "GP-001",
 "severity": "error",
 "confidence": "heuristic",
 "detector": "emc_ground_plane",
 "summary": "Signal has significant reference plane gap",
 "description": "Net DIO0 has 79% reference plane coverage over 25.3mm of routing. Return current must detour around the gap, creating a loop antenna.",
 "recommendation": "Route this signal to avoid ground plane gaps, or fill the void. If a split is intentional, add a bridge capacitor across the gap.",
 "evidence_source": "heuristic_rule",
 "ctx.section": "Ground Plane"
}
```

### [warning] GP-001 — Signal has partial reference plane gap
```json
{
 "rule_id": "GP-001",
 "severity": "warning",
 "confidence": "heuristic",
 "detector": "emc_ground_plane",
 "summary": "Signal has partial reference plane gap",
 "description": "Net Net-(D3-Pad2) has 83% reference plane coverage over 8.6mm of routing. Return current must detour around the gap, creating a loop antenna.",
 "recommendation": "Route this signal to avoid ground plane gaps, or fill the void. If a split is intentional, add a bridge capacitor across the gap.",
 "evidence_source": "heuristic_rule",
 "ctx.section": "Ground Plane"
}
```

### [warning] GP-001 — Signal has partial reference plane gap
```json
{
 "rule_id": "GP-001",
 "severity": "warning",
 "confidence": "heuristic",
 "detector": "emc_ground_plane",
 "summary": "Signal has partial reference plane gap",
 "description": "Net RESET has 83% reference plane coverage over 21.7mm of routing. Return current must detour around the gap, creating a loop antenna.",
 "recommendation": "Route this signal to avoid ground plane gaps, or fill the void. If a split is intentional, add a bridge capacitor across the gap.",
 "evidence_source": "heuristic_rule",
 "ctx.section": "Ground Plane"
}
```

### [warning] GP-001 — Signal has partial reference plane gap
```json
{
 "rule_id": "GP-001",
 "severity": "warning",
 "confidence": "heuristic",
 "detector": "emc_ground_plane",
 "summary": "Signal has partial reference plane gap",
 "description": "Net BUZZ has 83% reference plane coverage over 23.9mm of routing. Return current must detour around the gap, creating a loop antenna.",
 "recommendation": "Route this signal to avoid ground plane gaps, or fill the void. If a split is intentional, add a bridge capacitor across the gap.",
 "evidence_source": "heuristic_rule",
 "ctx.section": "Ground Plane"
}
```

### [warning] GP-001 — Signal has partial reference plane gap
```json
{
 "rule_id": "GP-001",
 "severity": "warning",
 "confidence": "heuristic",
 "detector": "emc_ground_plane",
 "summary": "Signal has partial reference plane gap",
 "description": "Net GATE_1 has 85% reference plane coverage over 16.9mm of routing. Return current must detour around the gap, creating a loop antenna.",
 "recommendation": "Route this signal to avoid ground plane gaps, or fill the void. If a split is intentional, add a bridge capacitor across the gap.",
 "evidence_source": "heuristic_rule",
 "ctx.section": "Ground Plane"
}
```

### [warning] GP-001 — Signal has partial reference plane gap
```json
{
 "rule_id": "GP-001",
 "severity": "warning",
 "confidence": "heuristic",
 "detector": "emc_ground_plane",
 "summary": "Signal has partial reference plane gap",
 "description": "Net MOSI has 86% reference plane coverage over 21.1mm of routing. Return current must detour around the gap, creating a loop antenna.",
 "recommendation": "Route this signal to avoid ground plane gaps, or fill the void. If a split is intentional, add a bridge capacitor across the gap.",
 "evidence_source": "heuristic_rule",
 "ctx.section": "Ground Plane"
}
```

### [warning] GP-001 — Signal has partial reference plane gap
```json
{
 "rule_id": "GP-001",
 "severity": "warning",
 "confidence": "heuristic",
 "detector": "emc_ground_plane",
 "summary": "Signal has partial reference plane gap",
 "description": "Net OLED_SCL has 89% reference plane coverage over 51.7mm of routing. Return current must detour around the gap, creating a loop antenna.",
 "recommendation": "Route this signal to avoid ground plane gaps, or fill the void. If a split is intentional, add a bridge capacitor across the gap.",
 "evidence_source": "heuristic_rule",
 "ctx.section": "Ground Plane"
}
```

### [warning] GP-001 — Signal has partial reference plane gap
```json
{
 "rule_id": "GP-001",
 "severity": "warning",
 "confidence": "heuristic",
 "detector": "emc_ground_plane",
 "summary": "Signal has partial reference plane gap",
 "description": "Net BTN has 90% reference plane coverage over 62.8mm of routing. Return current must detour around the gap, creating a loop antenna.",
 "recommendation": "Route this signal to avoid ground plane gaps, or fill the void. If a split is intentional, add a bridge capacitor across the gap.",
 "evidence_source": "heuristic_rule",
 "ctx.section": "Ground Plane"
}
```

### [warning] GP-001 — Signal has partial reference plane gap
```json
{
 "rule_id": "GP-001",
 "severity": "warning",
 "confidence": "heuristic",
 "detector": "emc_ground_plane",
 "summary": "Signal has partial reference plane gap",
 "description": "Net GATE_2 has 90% reference plane coverage over 11.3mm of routing. Return current must detour around the gap, creating a loop antenna.",
 "recommendation": "Route this signal to avoid ground plane gaps, or fill the void. If a split is intentional, add a bridge capacitor across the gap.",
 "evidence_source": "heuristic_rule",
 "ctx.section": "Ground Plane"
}
```

### [warning] GP-001 — Signal has partial reference plane gap
```json
{
 "rule_id": "GP-001",
 "severity": "warning",
 "confidence": "heuristic",
 "detector": "emc_ground_plane",
 "summary": "Signal has partial reference plane gap",
 "description": "Net Net-(Q1-D) has 92% reference plane coverage over 46.7mm of routing. Return current must detour around the gap, creating a loop antenna.",
 "recommendation": "Route this signal to avoid ground plane gaps, or fill the void. If a split is intentional, add a bridge capacitor across the gap.",
 "evidence_source": "heuristic_rule",
 "ctx.section": "Ground Plane"
}
```

### [warning] GP-001 — Signal has partial reference plane gap
```json
{
 "rule_id": "GP-001",
 "severity": "warning",
 "confidence": "heuristic",
 "detector": "emc_ground_plane",
 "summary": "Signal has partial reference plane gap",
 "description": "Net STATUS has 93% reference plane coverage over 47.0mm of routing. Return current must detour around the gap, creating a loop antenna.",
 "recommendation": "Route this signal to avoid ground plane gaps, or fill the void. If a split is intentional, add a bridge capacitor across the gap.",
 "evidence_source": "heuristic_rule",
 "ctx.section": "Ground Plane"
}
```

### [warning] GP-001 — Signal has partial reference plane gap
```json
{
 "rule_id": "GP-001",
 "severity": "warning",
 "confidence": "heuristic",
 "detector": "emc_ground_plane",
 "summary": "Signal has partial reference plane gap",
 "description": "Net LED_COUNT has 93% reference plane coverage over 20.3mm of routing. Return current must detour around the gap, creating a loop antenna.",
 "recommendation": "Route this signal to avoid ground plane gaps, or fill the void. If a split is intentional, add a bridge capacitor across the gap.",
 "evidence_source": "heuristic_rule",
 "ctx.section": "Ground Plane"
}
```

### [warning] GP-001 — Signal has partial reference plane gap
```json
{
 "rule_id": "GP-001",
 "severity": "warning",
 "confidence": "heuristic",
 "detector": "emc_ground_plane",
 "summary": "Signal has partial reference plane gap",
 "description": "Net OLED_SDA has 93% reference plane coverage over 50.0mm of routing. Return current must detour around the gap, creating a loop antenna.",
 "recommendation": "Route this signal to avoid ground plane gaps, or fill the void. If a split is intentional, add a bridge capacitor across the gap.",
 "evidence_source": "heuristic_rule",
 "ctx.section": "Ground Plane"
}
```

### [warning] GP-001 — Signal has partial reference plane gap
```json
{
 "rule_id": "GP-001",
 "severity": "warning",
 "confidence": "heuristic",
 "detector": "emc_ground_plane",
 "summary": "Signal has partial reference plane gap",
 "description": "Net Net-(Q1-G) has 94% reference plane coverage over 9.3mm of routing. Return current must detour around the gap, creating a loop antenna.",
 "recommendation": "Route this signal to avoid ground plane gaps, or fill the void. If a split is intentional, add a bridge capacitor across the gap.",
 "evidence_source": "heuristic_rule",
 "ctx.section": "Ground Plane"
}
```

### [warning] GP-005 — 3 ground domains detected
```json
{
 "rule_id": "GP-005",
 "severity": "warning",
 "confidence": "deterministic",
 "detector": "emc_ground_plane",
 "summary": "3 ground domains detected",
 "description": "Board has 3 separate ground domains: ?, ?, ?. Multiple ground domains require careful single-point connection to avoid ground loops and EMI.",
 "recommendation": "Verify ground domains connect at a single, intentional point (typically near the ADC for analog/digital split). Ensure no signal traces cross the domain boundary.",
 "evidence_source": "topology",
 "ctx.section": "Ground Plane"
}
```

### [error] DC-002 — No decoupling cap found near U1
```json
{
 "rule_id": "DC-002",
 "severity": "error",
 "confidence": "heuristic",
 "detector": "emc_decoupling",
 "summary": "No decoupling cap found near U1",
 "description": "U1 (Ra-02) has no capacitor within 10mm. Every IC with power pins needs at least one decoupling capacitor.",
 "recommendation": "Add 100nF X7R 0402 + 1µF X5R 0603 close to U1 power pins. For high-speed ICs, add 10nF C0G for high-frequency decoupling. Place caps on the same side as U1 with short, wide traces to vias.",
 "evidence_source": "heuristic_rule",
 "ctx.section": "Decoupling"
}
```

### [info] IO-001 — No EMC filtering near J2
```json
{
 "rule_id": "IO-001",
 "severity": "info",
 "confidence": "heuristic",
 "detector": "emc_io_filtering",
 "summary": "No EMC filtering near J2",
 "description": "Connector J2 (COM_BT) has no ferrite bead, CM choke, or ESD protection within 25mm. Unfiltered I/O cables are the dominant source of radiated emissions — common-mode current as low as 5 µA can exceed FCC Class B.",
 "recommendation": "J2 appears to be a power-only connector (all pins are power/ground rails). A board-level ferrite bead would saturate at typical power-supply currents. If radiated EMI is a concern on the cable, add a system-level common-mode choke or use shielded cable with chassis termination.",
 "evidence_source": "heuristic_rule",
 "ctx.section": "Io Filtering"
}
```

### [info] IO-001 — No EMC filtering near J11
```json
{
 "rule_id": "IO-001",
 "severity": "info",
 "confidence": "heuristic",
 "detector": "emc_io_filtering",
 "summary": "No EMC filtering near J11",
 "description": "Connector J11 (OLED) has no ferrite bead, CM choke, or ESD protection within 25mm. Unfiltered I/O cables are the dominant source of radiated emissions — common-mode current as low as 5 µA can exceed FCC Class B.",
 "recommendation": "Add a ferrite bead (e.g., BLM18AG601SN1D, 600Ω@100MHz) on signal lines near J11. Add ESD/TVS protection for external interfaces.",
 "evidence_source": "heuristic_rule",
 "ctx.section": "Io Filtering"
}
```

### [info] IO-001 — No EMC filtering near J7
```json
{
 "rule_id": "IO-001",
 "severity": "info",
 "confidence": "heuristic",
 "detector": "emc_io_filtering",
 "summary": "No EMC filtering near J7",
 "description": "Connector J7 (RELAY) has no ferrite bead, CM choke, or ESD protection within 25mm. Unfiltered I/O cables are the dominant source of radiated emissions — common-mode current as low as 5 µA can exceed FCC Class B.",
 "recommendation": "Add a ferrite bead (e.g., BLM18AG601SN1D, 600Ω@100MHz) on signal lines near J7. Add ESD/TVS protection for external interfaces.",
 "evidence_source": "heuristic_rule",
 "ctx.section": "Io Filtering"
}
```

### [info] IO-001 — No EMC filtering near J5
```json
{
 "rule_id": "IO-001",
 "severity": "info",
 "confidence": "heuristic",
 "detector": "emc_io_filtering",
 "summary": "No EMC filtering near J5",
 "description": "Connector J5 (LED_BUTTON-) has no ferrite bead, CM choke, or ESD protection within 25mm. Unfiltered I/O cables are the dominant source of radiated emissions — common-mode current as low as 5 µA can exceed FCC Class B.",
 "recommendation": "J5 appears to be a power-only connector (all pins are power/ground rails). A board-level ferrite bead would saturate at typical power-supply currents. If radiated EMI is a concern on the cable, add a system-level common-mode choke or use shielded cable with chassis termination.",
 "evidence_source": "heuristic_rule",
 "ctx.section": "Io Filtering"
}
```

### [info] IO-001 — No EMC filtering near J1
```json
{
 "rule_id": "IO-001",
 "severity": "info",
 "confidence": "heuristic",
 "detector": "emc_io_filtering",
 "summary": "No EMC filtering near J1",
 "description": "Connector J1 (5v_BUCK) has no ferrite bead, CM choke, or ESD protection within 25mm. Unfiltered I/O cables are the dominant source of radiated emissions — common-mode current as low as 5 µA can exceed FCC Class B.",
 "recommendation": "J1 appears to be a power-only connector (all pins are power/ground rails). A board-level ferrite bead would saturate at typical power-supply currents. If radiated EMI is a concern on the cable, add a system-level common-mode choke or use shielded cable with chassis termination.",
 "evidence_source": "heuristic_rule",
 "ctx.section": "Io Filtering"
}
```

### [error] IO-001 — No EMC filtering near J12
```json
{
 "rule_id": "IO-001",
 "severity": "error",
 "confidence": "heuristic",
 "detector": "emc_io_filtering",
 "summary": "No EMC filtering near J12",
 "description": "Connector J12 (Screw_Terminal_2_P3.50mm) has no ferrite bead, CM choke, or ESD protection within 25mm. Unfiltered I/O cables are the dominant source of radiated emissions — common-mode current as low as 5 µA can exceed FCC Class B.",
 "recommendation": "Add a ferrite bead (e.g., BLM18AG601SN1D, 600Ω@100MHz) on signal lines near J12. Add ESD/TVS protection for external interfaces.",
 "evidence_source": "heuristic_rule",
 "ctx.section": "Io Filtering"
}
```

### [info] IO-001 — No EMC filtering near J3
```json
{
 "rule_id": "IO-001",
 "severity": "info",
 "confidence": "heuristic",
 "detector": "emc_io_filtering",
 "summary": "No EMC filtering near J3",
 "description": "Connector J3 (NO_BT) has no ferrite bead, CM choke, or ESD protection within 25mm. Unfiltered I/O cables are the dominant source of radiated emissions — common-mode current as low as 5 µA can exceed FCC Class B.",
 "recommendation": "Add a ferrite bead (e.g., BLM18AG601SN1D, 600Ω@100MHz) on signal lines near J3. Add ESD/TVS protection for external interfaces.",
 "evidence_source": "heuristic_rule",
 "ctx.section": "Io Filtering"
}
```

### [info] IO-001 — No EMC filtering near J4
```json
{
 "rule_id": "IO-001",
 "severity": "info",
 "confidence": "heuristic",
 "detector": "emc_io_filtering",
 "summary": "No EMC filtering near J4",
 "description": "Connector J4 (LED_BUTTON+) has no ferrite bead, CM choke, or ESD protection within 25mm. Unfiltered I/O cables are the dominant source of radiated emissions — common-mode current as low as 5 µA can exceed FCC Class B.",
 "recommendation": "Add a ferrite bead (e.g., BLM18AG601SN1D, 600Ω@100MHz) on signal lines near J4. Add ESD/TVS protection for external interfaces.",
 "evidence_source": "heuristic_rule",
 "ctx.section": "Io Filtering"
}
```

### [info] IO-001 — No EMC filtering near J10
```json
{
 "rule_id": "IO-001",
 "severity": "info",
 "confidence": "heuristic",
 "detector": "emc_io_filtering",
 "summary": "No EMC filtering near J10",
 "description": "Connector J10 (BUZZER) has no ferrite bead, CM choke, or ESD protection within 25mm. Unfiltered I/O cables are the dominant source of radiated emissions — common-mode current as low as 5 µA can exceed FCC Class B.",
 "recommendation": "Add a ferrite bead (e.g., BLM18AG601SN1D, 600Ω@100MHz) on signal lines near J10. Add ESD/TVS protection for external interfaces.",
 "evidence_source": "heuristic_rule",
 "ctx.section": "Io Filtering"
}
```

### [info] IO-001 — No EMC filtering near J8
```json
{
 "rule_id": "IO-001",
 "severity": "info",
 "confidence": "heuristic",
 "detector": "emc_io_filtering",
 "summary": "No EMC filtering near J8",
 "description": "Connector J8 (ENDSTOP/SW) has no ferrite bead, CM choke, or ESD protection within 25mm. Unfiltered I/O cables are the dominant source of radiated emissions — common-mode current as low as 5 µA can exceed FCC Class B.",
 "recommendation": "Add a ferrite bead (e.g., BLM18AG601SN1D, 600Ω@100MHz) on signal lines near J8. Add ESD/TVS protection for external interfaces.",
 "evidence_source": "heuristic_rule",
 "ctx.section": "Io Filtering"
}
```

### [info] SU-001 — Adjacent signal layers: F.Cu, B.Cu
```json
{
 "rule_id": "SU-001",
 "severity": "info",
 "confidence": "deterministic",
 "detector": "emc_stackup",
 "summary": "Adjacent signal layers: F.Cu, B.Cu",
 "description": "Signal layers F.Cu and B.Cu are adjacent without a reference plane between them. This causes high crosstalk and poor return path control for signals on both layers.",
 "recommendation": "Consider a 4-layer stackup with internal reference planes for the next revision if signal integrity or EMC issues arise.",
 "evidence_source": "topology",
 "ctx.section": "Stackup"
}
```

### [info] EE-001 — Board cavity resonance frequencies
```json
{
 "rule_id": "EE-001",
 "severity": "info",
 "confidence": "heuristic",
 "detector": "emc_emission_estimate",
 "summary": "Board cavity resonance frequencies",
 "description": "Board (79×57mm, εr=4.5) cavity resonances: (1,0) at 897 MHz; (0,1) at 1234 MHz; (1,1) at 1526 MHz; (2,0) at 1793 MHz; (2,1) at 2177 MHz. PDN impedance spikes at these frequencies. Ensure adequate decoupling at and around these frequencies.",
 "recommendation": "Add decoupling capacitors with SRF near these frequencies.",
 "evidence_source": "heuristic_rule",
 "ctx.section": "Emission Estimate"
}
```

## thermal.json

## gerber.json
```json
{
 "gerber_files": 9,
 "drill_files": 2,
 "total_holes": 89,
 "total_flashes": 590,
 "total_draws": 24807
}
```

### [warning] GR-004 — F paste layer: 24 flashes vs 113 copper (21%)
```json
{
 "rule_id": "GR-004",
 "severity": "warning",
 "confidence": "heuristic",
 "detector": "analyze_gerbers",
 "summary": "F paste layer: 24 flashes vs 113 copper (21%)",
 "description": "F-side paste layer has significantly fewer flashes (24) than copper layer (113). This may indicate missing solder paste apertures.",
 "recommendation": "Check solder paste aperture generation — missing apertures cause assembly defects.",
 "evidence_source": "topology",
 "ctx.section": "Gerber Completeness",
 "ctx.impact": "Assembly solder joint quality"
}
```

## spice.json
