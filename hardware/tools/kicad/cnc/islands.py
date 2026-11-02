"""Estende cada ligacao nao roteada o mais perto possivel uma da outra e deixa
uma ILHA DE SOLDA (footprint `ignitor:JUMPER_ILHA`, pad PTH 1,8 mm / furo 0,9)
em cada ponta, para o usuario fechar com um fio jumper.

Feito para o pcbcnc (1 face B.Cu): roda o DRC, le os itens desconectados e, para
cada par que o A* (modo best_effort) nao consegue ligar por completo, adiciona
as trilhas parciais nos dois lados e as ilhas nos pontos de parada. Se os dois
lados se encontrarem (sem parede no caminho), liga direto e nao cria ilha.

Uso:
    & "C:\\Program Files\\KiCad\\10.0\\bin\\python.exe" -u islands.py ^
        placa.kicad_pcb saida.kicad_pcb [--clearance 0.4] [--width 1.0] ^
        [--layer B.Cu] [--grid 0.1]

Sempre use -u. Deterministico; so ADICIONA trilhas e ilhas.
"""

import argparse
import math
import os
import sys

import numpy as np
import pcbnew

import fill_gaps as fg

LIB_DIR = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "..", "kicad", "shared", "lib", "ignitor.pretty"))
IGN_NETS = ("Net-(Q1-D)", "Net-(Q1-S)")
ISLAND_REF = "JMP"
ISLAND_R = 0.9  # raio do pad da ilha (1,8 mm)
# distancia minima (em celulas) entre a ilha e a borda do bloqueio: garante
# folga para o pad de 1,8 mm (0,9 + 0,4 = 1,3 mm do cobre alheio)
MIN_D_CELLS = 4
def short_label(desc):
    """'Ilha PTH 23 [STATUS] de A1' -> 'A1.23'; resto -> 'ponta de trilha'."""
    if desc.startswith("Ilha PTH "):
        try:
            return "%s.%s" % (desc.split(" de ")[1], desc.split()[2])
        except IndexError:
            return desc[:28]
    return "ponta de trilha"


NEAR_CELLS = 10  # se o fim do stub fica a <=10 celulas do alvo, liga direto
HOLE_GAP = 0.25  # folga minima furo-a-furo (DRC)


def make_island(board, net, x_mm, y_mm, ref):
    fp = pcbnew.FootprintLoad(LIB_DIR, "JUMPER_ILHA")
    if fp is None:
        raise SystemExit("nao achei ignitor:JUMPER_ILHA em %s" % LIB_DIR)
    fp.SetFPID(pcbnew.LIB_ID("ignitor", "JUMPER_ILHA"))
    fp.SetReference(ref)
    fp.SetPosition(pcbnew.VECTOR2I(int(round(x_mm * fg.MM)),
                                   int(round(y_mm * fg.MM))))
    for pad in fp.Pads():
        pad.SetNet(board.FindNet(net))
    try:
        fp.Reference().SetVisible(False)
        fp.Value().SetVisible(False)
    except AttributeError:
        pass
    fp.SetAttributes(fp.GetAttributes() | pcbnew.FP_BOARD_ONLY)
    board.Add(fp)
    return fp


def route_pair(board, grid, masks, everything, edge, net, anchor_a, anchor_b,
               args, counter, layer, pads, labels):
    """Liga (ou aproxima) um par. Retorna (linha_da_tabela, ligou_tudo)."""
    width = 1.9 if net in IGN_NETS else args.width
    r_cells = int(math.ceil((args.clearance + width / 2 + args.margin)
                            / args.grid))
    own = masks.get(net, np.zeros((grid.h, grid.w), bool))
    blocked = fg.dilate(everything & ~own, r_cells) | edge
    sa, sb = grid.idx(*anchor_a), grid.idx(*anchor_b)
    blocked[sa] = False
    blocked[sb] = False
    mult = fg.congestion_multiplier(blocked, args.keep_cost) \
        if args.keep_cost > 0 else None
    dmap = fg.distance_to_obstacle(blocked)

    path_a, reached = fg.astar(blocked, sa, sb, args.grid, mult,
                               best_effort=True, max_pops=args.max_pops)
    if reached:
        pts = fg.simplify(grid, fg.MaskCtx(grid, blocked), path_a, args.grid)
        for p1, p2 in zip(pts, pts[1:]):
            if p1 != p2:
                fg.add_track(board, net, p1, p2, width, layer)
        _update_masks(grid, masks, everything, net, pts, width)
        return ("%s: LIGADO pelo robo (%.1f mm)"
                % (net, _length(pts)), True)
    if not path_a:
        return ("%s: sem caminho no lado A" % net, False)
    # chegou "colado" no alvo (so a regra de canto impediu)? liga com um toco
    if max(abs(path_a[-1][0] - sb[0]), abs(path_a[-1][1] - sb[1])) <= NEAR_CELLS:
        p0 = grid.pt(*path_a[-1])
        fg.add_track(board, net, p0, anchor_b, width, layer)
        pts = fg.simplify(grid, fg.MaskCtx(grid, blocked), path_a, args.grid)
        for p1, p2 in zip(pts, pts[1:]):
            if p1 != p2:
                fg.add_track(board, net, p1, p2, width, layer)
        _update_masks(grid, masks, everything, net, pts + [p0, anchor_b],
                      width)
        return ("%s: LIGADO no alvo (%.1f mm)"
                % (net, _length(pts) + math.dist(p0, anchor_b)), True)
    # o lado B persegue o fim do stub do lado A: o fio fica curto
    end_a = path_a[-1]
    path_b, reached_b = fg.astar(blocked, sb, end_a, args.grid, mult,
                                 best_effort=True, max_pops=args.max_pops)
    if reached_b:
        pts_b = fg.simplify(grid, fg.MaskCtx(grid, blocked), path_b, args.grid)
        for p1, p2 in zip(pts_b, pts_b[1:]):
            if p1 != p2:
                fg.add_track(board, net, p1, p2, width, layer)
        pts_a = fg.simplify(grid, fg.MaskCtx(grid, blocked), path_a, args.grid)
        for p1, p2 in zip(pts_a, pts_a[1:]):
            if p1 != p2:
                fg.add_track(board, net, p1, p2, width, layer)
        _update_masks(grid, masks, everything, net, pts_a + pts_b, width)
        return ("%s: LIGADO por aproximacao (%.1f mm)"
                % (net, _length(pts_a) + _length(pts_b)), True)
    if not path_b:
        return ("%s: sem caminho no lado B" % net, False)

    end_b = path_b[-1]
    ctx = fg.MaskCtx(grid, blocked)
    if fg.line_free(ctx, grid.pt(*end_a), grid.pt(*end_b), args.grid):
        pts_b = fg.simplify(grid, ctx, path_b, args.grid)
        fg.add_track(board, net, grid.pt(*end_a), grid.pt(*end_b), width, layer)
        pts_a = fg.simplify(grid, ctx, path_a, args.grid)
        for p1, p2 in zip(pts_a, pts_a[1:]):
            if p1 != p2:
                fg.add_track(board, net, p1, p2, width, layer)
        for p1, p2 in zip(pts_b, pts_b[1:]):
            if p1 != p2:
                fg.add_track(board, net, p1, p2, width, layer)
        _update_masks(grid, masks, everything, net, pts_a + pts_b, width)
        return ("%s: LIGADO por aproximacao (%.1f mm)"
                % (net, _length(pts_a) + _length(pts_b)), True)

    parts = []
    ends = []
    for path, own_anchor, lab in ((path_a, anchor_a, labels[0]),
                                     (path_b, anchor_b, labels[1])):
        end_pt = grid.pt(*path[-1])
        if math.dist(end_pt, own_anchor) < 1.5:
            # o bolso esta colado no proprio pad: nao estende nem cria ilha,
            # o fio solda direto no pad do componente
            parts.append(short_label(lab))
            ends.append(own_anchor)
            continue
        cut = None
        for i in range(len(path) - 1, -1, -1):
            px, py = grid.pt(*path[i])
            if dmap[path[i]] < MIN_D_CELLS:
                continue
            # o furo da ilha nao pode encostar em outro furo
            if any(math.hypot(px - hx, py - hy) < hr + 0.45 + HOLE_GAP
                   for hx, hy, hr in pads):
                continue
            cut = i
            break
        path_use = path[:cut + 1] if cut is not None else path
        pts = fg.simplify(grid, ctx, path_use, args.grid)
        for p1, p2 in zip(pts, pts[1:]):
            if p1 != p2:
                fg.add_track(board, net, p1, p2, width, layer)
        _update_masks(grid, masks, everything, net, pts, width)
        if cut is not None:
            counter[0] += 1
            ref = "%s%d" % (ISLAND_REF, counter[0])
            px, py = grid.pt(*path_use[-1])
            make_island(board, net, px, py, ref)
            isl = grid.seg_mask(px, py, px, py, ISLAND_R)
            masks[net] = masks.get(net, np.zeros((grid.h, grid.w), bool)) | isl
            everything |= isl
            parts.append("%s @(%.1f,%.1f)" % (ref, px, py))
            ends.append((px, py))
        else:
            px, py = grid.pt(*path_use[-1])
            parts.append("ponta de trilha @(%.1f,%.1f)" % (px, py))
            ends.append((px, py))
    wire = math.hypot(ends[0][0] - ends[1][0], ends[0][1] - ends[1][1])
    return ("%s: %s <-> %s | fio %.1f mm" % (net, parts[0], parts[1], wire),
            False)


def _update_masks(grid, masks, everything, net, pts, width):
    new = np.zeros((grid.h, grid.w), bool)
    for p1, p2 in zip(pts, pts[1:]):
        new |= grid.seg_mask(p1[0], p1[1], p2[0], p2[1], width / 2)
    masks[net] = masks.get(net, np.zeros((grid.h, grid.w), bool)) | new
    everything |= new


def _length(pts):
    return sum(math.hypot(b[0] - a[0], b[1] - a[1])
               for a, b in zip(pts, pts[1:]))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("board")
    ap.add_argument("out")
    ap.add_argument("--clearance", type=float, default=0.4)
    ap.add_argument("--margin", type=float, default=0.06)
    ap.add_argument("--width", type=float, default=1.0)
    ap.add_argument("--layer", default="B.Cu")
    ap.add_argument("--grid", type=float, default=0.1)
    ap.add_argument("--keep-cost", type=float, default=1.5)
    ap.add_argument("--max-pops", type=int, default=250000)
    args = ap.parse_args()
    layer = pcbnew.B_Cu if args.layer == "B.Cu" else pcbnew.F_Cu

    tmp = os.path.join(os.environ.get("TEMP", "."), "islands_drc.json")
    board = pcbnew.LoadBoard(args.board)
    drc = fg.run_drc(args.board, tmp)
    pairs = [(u["items"][0], u["items"][1])
             for u in drc.get("unconnected_items", [])
             if len(u.get("items", [])) >= 2]
    print("desconectados: %d" % len(pairs))
    if not pairs:
        print("nada a fazer.")
        return 0

    grid = fg.Grid(board, args.grid)
    masks = fg.copper_masks(board, grid, layer)
    everything = np.zeros((grid.h, grid.w), bool)
    for m in masks.values():
        everything |= m
    edge = fg.edge_block(board, grid, 0.5 + ISLAND_R + 0.05)

    pads = []
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            dr = pad.GetDrillSize()
            if dr.x > 0:
                pos = pad.GetPosition()
                pads.append((pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y),
                             pcbnew.ToMM(max(dr.x, dr.y)) / 2))
    counter = [0]
    n_full = 0
    rows = []
    for pa, pb in pairs:
        na = fg.net_of(pa["description"])
        nb = fg.net_of(pb["description"])
        if na != nb or not na:
            rows.append("par de redes diferentes: %s x %s" % (na or "?", nb or "?"))
            continue
        row, full = route_pair(board, grid, masks, everything, edge, na,
                               (pa["pos"]["x"], pa["pos"]["y"]),
                               (pb["pos"]["x"], pb["pos"]["y"]),
                               args, counter, layer, pads,
                               (pa["description"], pb["description"]))
        rows.append(row)
        if full:
            n_full += 1
    board.BuildListOfNets()
    board.Save(args.out)
    print("\n".join(rows))
    print("ilhas criadas: %d | ligados pelo robo: %d -> %s"
          % (counter[0], n_full, args.out))
    drc2 = fg.run_drc(args.out, tmp)
    print("desconectados apos: %d" % len(drc2.get("unconnected_items", [])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
