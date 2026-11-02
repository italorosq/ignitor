#!/usr/bin/env python3
"""Gera o pacote de fabricação JLCPCB no formato do Fabrication Toolkit (bennymeg),
usando o kicad-cli. Reproduz:

  jlcpcb/gerber/<nome>-CuTop.gbr, CuBottom, MaskTop/Bottom, PasteTop/Bottom,
              SilkTop/Bottom, EdgeCuts, PTH.drl, NPTH.drl, PTH/NPTH-drl_map.pdf
  jlcpcb/production_files/GERBER-<nome>.zip
  jlcpcb/production_files/BOM-<nome>.csv e CPL-<nome>.csv   (com --skip-bom-cpl: não)

Uso:
  python gen_jlc_package.py <projeto_dir> [--skip-bom-cpl]

<projeto_dir> é a pasta que contém <nome>.kicad_pro/.kicad_pcb/.kicad_sch.
Backup do pacote antigo em %TEMP%\\opencode antes de sobrescrever.
"""
import argparse
import csv
import re
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KICAD_CLI = r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe"
LAYERS = "F.Cu,B.Cu,F.Mask,B.Mask,F.Silkscreen,B.Silkscreen,F.Paste,B.Paste,Edge.Cuts"
GERBER_MAP = {  # token do kicad-cli -> nome do toolkit
    "F_Cu": "CuTop", "B_Cu": "CuBottom",
    "F_Mask": "MaskTop", "B_Mask": "MaskBottom",
    "F_Paste": "PasteTop", "B_Paste": "PasteBottom",
    "F_Silkscreen": "SilkTop", "B_Silkscreen": "SilkBottom",
    "Edge_Cuts": "EdgeCuts",
}


def run(args):
    p = subprocess.run(args, capture_output=True, text=True)
    if p.returncode != 0:
        print("FALHA:", " ".join(args))
        print(p.stdout[-2000:])
        print(p.stderr[-2000:])
        sys.exit(1)
    return p.stdout


def parse_symbols(sch: Path):
    """Instâncias de símbolo (não-power, in_bom) de um .kicad_sch."""
    lines = sch.read_text(encoding="utf-8").split("\n")
    out = []
    sheets = []
    i = 0
    while i < len(lines):
        ln = lines[i]
        if ln == "\t(symbol":
            j = i + 1
            while lines[j] != "\t)":
                j += 1
            blk = "\n".join(lines[i:j + 1])
            ref = re.search(r'\(property "Reference" "([^"]+)"', blk)
            if ref and not ref.group(1).startswith("#") and "(in_bom yes)" in blk:
                val = re.search(r'\(property "Value" "([^"]*)"', blk)
                fp = re.search(r'\(property "Footprint" "([^"]*)"', blk)
                lcsc = re.search(r'\(property "LCSC Part" "([^"]*)"', blk)
                dnp = "(dnp yes)" in blk
                if not dnp:
                    out.append((ref.group(1), val.group(1) if val else "", fp.group(1) if fp else "", lcsc.group(1) if lcsc else ""))
            i = j + 1
        else:
            if ln.strip().startswith('(property "Sheetfile"'):
                m = re.search(r'"([^"]+\.kicad_sch)"', ln)
                if m:
                    sheets.append(m.group(1))
            i += 1
    return out, sheets


def bom_rows(proj: Path, name: str):
    comps = {}
    seen = set()

    def walk(fn):
        if fn in seen:
            return
        seen.add(fn)
        syms, sheets = parse_symbols(proj / fn)
        for ref, val, fp, lcsc in syms:
            comps[ref] = (val, fp, lcsc)
        for s in sheets:
            walk(s)

    walk(f"{name}.kicad_sch")
    groups = {}
    for ref, (val, fp, lcsc) in comps.items():
        groups.setdefault((val, fp.split(":")[-1], lcsc), []).append(ref)

    def natkey(r):
        m = re.match(r"([A-Za-z]+)(\d+)", r)
        return (m.group(1), int(m.group(2))) if m else (r, 0)

    rows = []
    for (val, fp, lcsc), refs in sorted(groups.items()):
        if lcsc:
            # peças do JLC: agrupadas por (comment, footprint, LCSC)
            rows.append([val, ",".join(sorted(refs, key=natkey)), fp, lcsc, str(len(refs))])
        else:
            # peças sem LCSC: uma linha por designador (convenção do toolkit)
            for ref in sorted(refs, key=natkey):
                rows.append([val, ref, fp, "", "1"])
    rows.sort(key=lambda r: (r[0], natkey(r[1].split(",")[0])))
    return rows


def fmt(v, dec):
    s = f"{v:.{dec}f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s


def pad_centers(pcb: Path):
    """Centro da bbox dos pads (convenção do toolkit JLC) por referência.

    O CPL do toolkit usa o centro do retângulo que envolve os pads, não a âncora
    do footprint (ex.: A1 = âncora + (12.7, 17.78)). Validado contra os CPLs
    gerados pelo toolkit real (A1, Q1/Q2, D3, R9).
    """
    import math
    txt = pcb.read_text(encoding="utf-8")
    centers = {}
    lines = txt.split("\n")
    i = 0
    while i < len(lines):
        if lines[i].startswith("\t(footprint "):
            j = i + 1
            while lines[j] != "\t)":
                j += 1
            blk = "\n".join(lines[i:j + 1])
            ref = re.search(r'\(property "Reference" "([^"]+)"', blk)
            at = re.search(r"\(at ([\d.-]+) ([\d.-]+)(?: ([\d.-]+))?\)", blk)
            if ref and at:
                X, Y = float(at.group(1)), float(at.group(2))
                R = math.radians(float(at.group(3) or 0.0))
                xs, ys = [], []
                for pm in re.finditer(
                        r'\(pad "?[^"()]*"?\s+\w+\s+\w+\s+\(at ([\d.-]+) ([\d.-]+)(?: ([\d.-]+))?\)\s*\(size ([\d.]+) ([\d.]+)\)',
                        blk):
                    dx, dy = float(pm.group(1)), float(pm.group(2))
                    dr = float(pm.group(3) or 0.0)
                    w, h = float(pm.group(4)), float(pm.group(5))
                    xb = X + dx * math.cos(R) + dy * math.sin(R)
                    yb = Y - dx * math.sin(R) + dy * math.cos(R)
                    t = math.radians(float(at.group(3) or 0.0) + dr)
                    hx = 0.5 * (abs(w * math.cos(t)) + abs(h * math.sin(t)))
                    hy = 0.5 * (abs(w * math.sin(t)) + abs(h * math.cos(t)))
                    xs += [xb - hx, xb + hx]
                    ys += [yb - hy, yb + hy]
                if xs:
                    centers[ref.group(1)] = ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2)
                else:
                    centers[ref.group(1)] = (X, Y)  # fallback: âncora
            i = j + 1
        else:
            i += 1
    return centers


def cpl_rows(proj: Path, name: str, tmp: Path):
    out_csv = tmp / "pos.csv"
    run([KICAD_CLI, "pcb", "export", "pos", "--format", "csv", "--units", "mm",
         "--side", "both", "-o", str(out_csv), str(proj / f"{name}.kicad_pcb")])
    centers = pad_centers(proj / f"{name}.kicad_pcb")
    rows = []
    with open(out_csv, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            cx, cy = centers.get(r["Ref"], (float(r["PosX"]), -float(r["PosY"])))
            rot = float(r["Rot"])
            rows.append([r["Ref"], r["Val"], r["Package"], fmt(cx, 4), fmt(-cy, 4),
                         f"{rot:.1f}", r["Side"].lower()])
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("project")
    ap.add_argument("--skip-bom-cpl", action="store_true")
    a = ap.parse_args()
    proj = Path(a.project).resolve()
    pcb = next(proj.glob("*.kicad_pcb"))
    name = pcb.stem
    jlc = proj / "jlcpcb"
    ger = jlc / "gerber"
    prod = jlc / "production_files"
    tmp = Path(tempfile.mkdtemp(prefix="jlc_pkg_"))
    ger.mkdir(parents=True, exist_ok=True)
    prod.mkdir(parents=True, exist_ok=True)

    ts = time.strftime("%H%M%S")
    bk = Path(tempfile.gettempdir()) / f"opencode/jlcpcb_bk_{name}_{ts}"
    if jlc.exists():
        shutil.copytree(jlc, bk)
        print(f"backup do pacote antigo: {bk}")

    # gerbers
    run([KICAD_CLI, "pcb", "export", "gerbers", "--layers", LAYERS, "-o", str(tmp), str(pcb)])
    final = {}
    for f in tmp.iterdir():
        if f.suffix == ".gbrjob":
            continue
        for token, tgt in GERBER_MAP.items():
            if f.name.startswith(f"{name}-{token}."):
                final[f"{name}-{tgt}.gbr"] = f

    # drill + maps
    run([KICAD_CLI, "pcb", "export", "drill", "--format", "excellon",
         "--drill-origin", "absolute", "--excellon-zeros-format", "decimal",
         "--excellon-units", "in", "--excellon-separate-th",
         "--generate-map", "--map-format", "pdf", "-o", str(tmp), str(pcb)])
    for f in tmp.iterdir():
        n = f.name
        if n.endswith(".drl"):
            which = "NPTH" if "NPTH" in n else "PTH"
            final[f"{name}-{which}.drl"] = f
        elif n.endswith(".pdf"):
            which = "NPTH" if "NPTH" in n else "PTH"
            final[f"{name}-{which}-drl_map.pdf"] = f

    missing = [t for t in ("CuTop", "CuBottom", "MaskTop", "MaskBottom", "PasteTop",
                           "PasteBottom", "SilkTop", "SilkBottom", "EdgeCuts", "PTH", "NPTH")
               if f"{name}-{t}.gbr" not in final and f"{name}-{t}.drl" not in final]
    assert not missing, f"faltando no export: {missing}"

    # limpa a pasta gerber e grava os 13 arquivos
    for f in ger.iterdir():
        f.unlink()
    for tgt, src in sorted(final.items()):
        shutil.copy2(src, ger / tgt)
    print(f"gerber/: {len(final)} arquivos")

    # zip flat
    zpath = prod / f"GERBER-{name}.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for tgt in sorted(final):
            z.write(ger / tgt, tgt)
    print(f"zip: {zpath.name} ({len(final)} entradas)")

    # BOM / CPL
    if not a.skip_bom_cpl:
        rows = bom_rows(proj, name)
        with open(prod / f"BOM-{name}.csv", "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["Comment", "Designator", "Footprint", "LCSC", "Quantity"])
            w.writerows(rows)
        print(f"BOM: {len(rows)} linhas, {sum(int(r[4]) for r in rows)} componentes")

        cpl = cpl_rows(proj, name, tmp)
        with open(prod / f"CPL-{name}.csv", "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["Designator", "Val", "Package", "Mid X", "Mid Y", "Rotation", "Layer"])
            w.writerows(cpl)
        print(f"CPL: {len(cpl)} posições")

    print("OK")


if __name__ == "__main__":
    main()
