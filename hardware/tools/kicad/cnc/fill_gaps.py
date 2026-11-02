"""Fecha as ligacoes que o Freerouting deixa em aberto numa placa de 1 face.

Roda o DRC (kicad-cli) na placa, le a lista de itens desconectados e liga cada
par com um A* numa grade de 0,1 mm, com a largura da pista pedida (1 mm) e o
isolamento da netclass (0,4 mm). Foi feito para o pcbcnc (1 face B.Cu, sem
plano de terra, fresagem caseira por isolamento), onde o autorouter empaca nas
"ultimas milhas" - as travessias longas no meio do modulo ESP32.

Uso:
    & "C:\\Program Files\\KiCad\\10.0\\bin\\python.exe" -u fill_gaps.py ^
        placa.kicad_pcb placa_cheia.kicad_pcb [--clearance 0.4] [--width 1.0] ^
        [--grid 0.1] [--passes 4]

Sempre use -u (sem buffer, senao o processo morre sem imprimir nada).
O roteador e deterministico e so ADICIONA trilhas; nada existente e removido.
"""

import argparse
import heapq
import json
import math
import os
import shutil
import subprocess
import sys

import numpy as np
import pcbnew

MM = 1e6  # nm por mm
SQ2 = math.sqrt(2.0)
DIRS = [
    (-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0),
    (-1, -1, SQ2), (-1, 1, SQ2), (1, -1, SQ2), (1, 1, SQ2),
]
IGN_NETS = ("Net-(Q1-D)", "Net-(Q1-S)")


def kicad_cli():
    exe = shutil.which("kicad-cli")
    if exe:
        return exe
    for cand in (r"C:\Program Files\KiCad\10.0\bin\kicad-cli.exe",
                 r"C:\Program Files\KiCad\9.0\bin\kicad-cli.exe"):
        if os.path.exists(cand):
            return cand
    raise SystemExit("kicad-cli nao encontrado no PATH")


def run_drc(board_path, report_path):
    subprocess.run(
        [kicad_cli(), "pcb", "drc", "--format", "json",
         "-o", report_path, board_path],
        capture_output=True, text=True, check=False,
    )
    with open(report_path, encoding="utf-8") as fh:
        return json.load(fh)


def net_of(desc):
    if "[" in desc and "]" in desc:
        return desc.split("[")[1].split("]")[0]
    return ""


class Grid:
    """Grade regular sobre a placa; X e Y em mm por celula."""

    def __init__(self, board, step):
        bb = board.GetBoardEdgesBoundingBox()
        self.step = step
        self.left = pcbnew.ToMM(bb.GetLeft())
        self.top = pcbnew.ToMM(bb.GetTop())
        self.right = pcbnew.ToMM(bb.GetRight())
        self.bottom = pcbnew.ToMM(bb.GetBottom())
        self.x0 = self.left - 2.0
        self.y0 = self.top - 2.0
        self.w = int((self.right - self.left + 4.0) / step) + 2
        self.h = int((self.bottom - self.top + 4.0) / step) + 2
        xs = self.x0 + np.arange(self.w) * step
        ys = self.y0 + np.arange(self.h) * step
        self.X, self.Y = np.meshgrid(xs, ys)

    def idx(self, x_mm, y_mm):
        return (int(round((y_mm - self.y0) / self.step)),
                int(round((x_mm - self.x0) / self.step)))

    def pt(self, r, c):
        return (self.x0 + c * self.step, self.y0 + r * self.step)

    def seg_mask(self, x1, y1, x2, y2, radius):
        """Celulas dentro de `radius` mm do segmento (1,2)-(3,4)."""
        lo_r = max(0, int((min(y1, y2) - radius - self.y0) / self.step) - 1)
        hi_r = min(self.h, int((max(y1, y2) + radius - self.y0) / self.step) + 2)
        lo_c = max(0, int((min(x1, x2) - radius - self.x0) / self.step) - 1)
        hi_c = min(self.w, int((max(x1, x2) + radius - self.x0) / self.step) + 2)
        if lo_r >= hi_r or lo_c >= hi_c:
            return np.zeros((self.h, self.w), bool)
        x = self.X[lo_r:hi_r, lo_c:hi_c]
        y = self.Y[lo_r:hi_r, lo_c:hi_c]
        dx, dy = x2 - x1, y2 - y1
        ln2 = dx * dx + dy * dy
        if ln2 < 1e-12:
            d2 = (x - x1) ** 2 + (y - y1) ** 2
        else:
            t = ((x - x1) * dx + (y - y1) * dy) / ln2
            t = np.clip(t, 0.0, 1.0)
            d2 = (x - (x1 + t * dx)) ** 2 + (y - (y1 + t * dy)) ** 2
        out = np.zeros((self.h, self.w), bool)
        out[lo_r:hi_r, lo_c:hi_c] = d2 <= radius * radius
        return out

    def rect_mask(self, x1, y1, x2, y2):
        return (self.X >= min(x1, x2)) & (self.X <= max(x1, x2)) & \
               (self.Y >= min(y1, y2)) & (self.Y <= max(y1, y2))


def copper_masks(board, grid, layer):
    """copper[net] com o cobre de cada rede NA CAMADA `layer`; '' = sem rede.
    Pads PTH aparecem nas duas faces; vias tambem. Trilhas so contam na propria
    face (em 2 faces, uma trilha de F.Cu nao bloqueia o B.Cu)."""
    masks = {}

    def add(net, mask):
        masks[net] = masks.get(net, np.zeros((grid.h, grid.w), bool)) | mask

    for t in board.GetTracks():
        net = str(t.GetNetname())
        if t.GetClass() == "PCB_TRACK":
            if t.GetLayer() != layer:
                continue
            a, b = t.GetStart(), t.GetEnd()
            m = grid.seg_mask(pcbnew.ToMM(a.x), pcbnew.ToMM(a.y),
                              pcbnew.ToMM(b.x), pcbnew.ToMM(b.y),
                              pcbnew.ToMM(t.GetWidth()) / 2)
            add(net, m)
        elif t.GetClass() == "PCB_VIA":
            p = t.GetPosition()
            rad = pcbnew.ToMM(t.GetWidth(pcbnew.B_Cu)) / 2
            add(net, grid.seg_mask(pcbnew.ToMM(p.x), pcbnew.ToMM(p.y),
                                   pcbnew.ToMM(p.x), pcbnew.ToMM(p.y), rad))
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            bb = pad.GetBoundingBox()
            add(str(pad.GetNetname()),
                grid.rect_mask(pcbnew.ToMM(bb.GetLeft()),
                               pcbnew.ToMM(bb.GetTop()),
                               pcbnew.ToMM(bb.GetRight()),
                               pcbnew.ToMM(bb.GetBottom())))
    return masks


def edge_block(board, grid, radius):
    block = (grid.X < grid.left) | (grid.X > grid.right) | \
            (grid.Y < grid.top) | (grid.Y > grid.bottom)
    for dr in board.GetDrawings():
        if board.GetLayerName(dr.GetLayer()) != "Edge.Cuts":
            continue
        shape = dr.GetShape()
        if shape == pcbnew.SHAPE_T_SEGMENT:
            a, b = dr.GetStart(), dr.GetEnd()
            block |= grid.seg_mask(pcbnew.ToMM(a.x), pcbnew.ToMM(a.y),
                                   pcbnew.ToMM(b.x), pcbnew.ToMM(b.y), radius)
        elif shape == pcbnew.SHAPE_T_CIRCLE:
            c = dr.GetCenter()
            r = pcbnew.ToMM(dr.GetRadius())
            cx, cy = pcbnew.ToMM(c.x), pcbnew.ToMM(c.y)
            block |= grid.seg_mask(cx, cy, cx, cy, r + radius) & \
                ~grid.seg_mask(cx, cy, cx, cy, max(r - radius, 0.0))
        elif shape == pcbnew.SHAPE_T_ARC:
            c = dr.GetCenter()
            cx, cy = pcbnew.ToMM(c.x), pcbnew.ToMM(c.y)
            r = pcbnew.ToMM(dr.GetRadius())
            block |= grid.seg_mask(cx, cy, cx, cy, r + radius) & \
                ~grid.seg_mask(cx, cy, cx, cy, max(r - radius, 0.0))
    return block


def dilate(mask, cells):
    """Dilatacao em 8 direcoes por `cells` celulas."""
    for _ in range(int(cells)):
        m = mask
        mask = (m | np.roll(m, 1, 0) | np.roll(m, -1, 0) |
                np.roll(m, 1, 1) | np.roll(m, -1, 1) |
                np.roll(np.roll(m, 1, 0), 1, 1) | np.roll(np.roll(m, 1, 0), -1, 1) |
                np.roll(np.roll(m, -1, 0), 1, 1) | np.roll(np.roll(m, -1, 0), -1, 1))
    return mask


def astar(blocked, start, goal, step, mult=None, best_effort=False, max_pops=None):
    """A* de grade. Com best_effort=True, quando o goal e inalcancavel devolve o
    caminho ate a celula visitada mais proxima dele (para puxar a trilha o mais
    perto possivel do alvo). Retorna (caminho, chegou_ao_goal) ou (None, False)."""
    h, w = blocked.shape
    inf = float("inf")
    g = np.full((h, w), inf)
    parent = np.full((h, w), -1, np.int64)
    gr, gc = goal
    pops = 0

    def heur(r, c):
        dr, dc = abs(r - gr), abs(c - gc)
        return (max(dr, dc) + (SQ2 - 1.0) * min(dr, dc)) * step

    def m(r, c):
        return 1.0 if mult is None else float(mult[r, c])

    g[start] = 0.0
    pq = [(heur(*start), start[0] * w + start[1])]
    best_idx, best_h = start[0] * w + start[1], heur(*start)
    reached = False
    while pq:
        f, idx = heapq.heappop(pq)
        pops += 1
        if max_pops is not None and pops > max_pops and best_effort:
            break
        r, c = divmod(idx, w)
        cur = g[r, c]
        hh = heur(r, c)
        if hh < best_h:
            best_h, best_idx = hh, idx
        if (r, c) == goal:
            reached = True
            break
        if f > cur + hh + 1e-9:
            continue
        for dr, dc, cost in DIRS:
            nr, nc = r + dr, c + dc
            if nr < 0 or nr >= h or nc < 0 or nc >= w or blocked[nr, nc]:
                continue
            if dr and dc and (blocked[r, nc] or blocked[nr, c]):
                continue
            ng = cur + cost * step * m(nr, nc)
            if ng + 1e-9 < g[nr, nc]:
                g[nr, nc] = ng
                parent[nr, nc] = idx
                heapq.heappush(pq, (ng + heur(nr, nc), nr * w + nc))
    end_idx = goal[0] * w + goal[1] if reached else best_idx
    if g.ravel()[end_idx] == inf and end_idx != start[0] * w + start[1]:
        return None, False
    path = []
    cur = end_idx
    while cur != -1:
        r, c = divmod(cur, w)
        path.append((r, c))
        if (r, c) == start:
            break
        cur = parent[r, c]
    path.reverse()
    return path, reached


def distance_to_obstacle(blocked, max_cells=25):
    """Distancia (em celulas) de cada celula livre ate o bloqueio mais proximo."""
    dist = np.zeros(blocked.shape, np.int16)
    m = blocked.copy()
    for r in range(1, max_cells + 1):
        m2 = (m | np.roll(m, 1, 0) | np.roll(m, -1, 0) |
              np.roll(m, 1, 1) | np.roll(m, -1, 1) |
              np.roll(np.roll(m, 1, 0), 1, 1) |
              np.roll(np.roll(m, 1, 0), -1, 1) |
              np.roll(np.roll(m, -1, 0), 1, 1) |
              np.roll(np.roll(m, -1, 0), -1, 1))
        new = m2 & ~m
        dist[new] = r
        m = m2
    dist[~m] = max_cells
    dist[blocked] = 0
    return dist


def congestion_multiplier(blocked, keep=1.5):
    """Multiplicador de custo: maior perto do bloqueio (trilha busca o centro)."""
    d = distance_to_obstacle(blocked)
    return 1.0 + keep / (d + 0.5)


def flood_reaches(blocked, start, goal, max_iter=3000):
    """O goal e alcancavel a partir do start? (diagnostico, grade 2x mais grossa)"""
    b = blocked[::2, ::2]
    s = (start[0] // 2, start[1] // 2)
    g = (goal[0] // 2, goal[1] // 2)
    m = np.zeros(b.shape, bool)
    m[s] = True
    for _ in range(max_iter):
        m2 = (m | np.roll(m, 1, 0) | np.roll(m, -1, 0) |
              np.roll(m, 1, 1) | np.roll(m, -1, 1) |
              np.roll(np.roll(m, 1, 0), 1, 1) |
              np.roll(np.roll(m, 1, 0), -1, 1) |
              np.roll(np.roll(m, -1, 0), 1, 1) |
              np.roll(np.roll(m, -1, 0), -1, 1)) & ~b
        if m2[g]:
            return m2.sum()
        if np.array_equal(m2, m):
            return 0
        m = m2
    return 0


def line_free(blocked, a, b, step):
    """Linha reta livre? Checa as celulas amostradas e evita cortar esquina
    (o par ortogonal de cada passo diagonal tambem precisa estar livre)."""
    ax, ay = a
    bx, by = b
    dist = math.hypot(bx - ax, by - ay)
    n = max(2, int(dist / (step / 2)) + 1)
    prev = None
    for i in range(n + 1):
        t = i / n
        c = int(round((ax + (bx - ax) * t - blocked.x0) / step))
        r = int(round((ay + (by - ay) * t - blocked.y0) / step))
        if r < 0 or r >= blocked.h or c < 0 or c >= blocked.w:
            return False
        if blocked.block[r, c]:
            return False
        if prev is not None:
            pr, pc = prev
            if pr != r and pc != c:
                if blocked.block[pr, c] or blocked.block[r, pc]:
                    return False
        prev = (r, c)
    return True


class MaskCtx:
    def __init__(self, grid, block):
        self.x0 = grid.x0
        self.y0 = grid.y0
        self.h, self.w = grid.h, grid.w
        self.block = block


def simplify(grid, blocked, path, step):
    pts = [grid.pt(r, c) for r, c in path]
    out = [pts[0]]
    i = 0
    while i < len(pts) - 1:
        j = len(pts) - 1
        while j > i + 1 and not line_free(blocked, pts[i], pts[j], step):
            j -= 1
        out.append(pts[j])
        i = j
    return out


def add_track(board, net, p1, p2, width_mm, layer):
    t = pcbnew.PCB_TRACK(board)
    t.SetStart(pcbnew.VECTOR2I(int(round(p1[0] * MM)), int(round(p1[1] * MM))))
    t.SetEnd(pcbnew.VECTOR2I(int(round(p2[0] * MM)), int(round(p2[1] * MM))))
    t.SetWidth(int(round(width_mm * MM)))
    t.SetLayer(layer)
    netinfo = board.FindNet(net)
    if netinfo is None:
        raise SystemExit("rede %r nao existe na placa" % net)
    t.SetNet(netinfo)
    board.Add(t)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("board")
    ap.add_argument("out")
    ap.add_argument("--clearance", type=float, default=0.4)
    ap.add_argument("--margin", type=float, default=0.06,
                    help="folga extra na grade para a quantizacao nao furar o clearance")
    ap.add_argument("--width", type=float, default=1.0)
    ap.add_argument("--fallback", default="0.8,0.6,0.5",
                    help="larguras de neck-down tentadas quando 1 mm nao passa")
    ap.add_argument("--grid", type=float, default=0.1)
    ap.add_argument("--layer", default="B.Cu")
    ap.add_argument("--order", choices=["drc", "short", "long"], default="short",
                    help="ordem de roteamento: comprimento crescente (short, "
                         "evita que trilhas longas emparedem as curtas)")
    ap.add_argument("--keep-cost", type=float, default=1.5,
                    help="peso do custo de afastamento das paredes (0 desliga)")
    args = ap.parse_args()
    args.fallback = [float(v) for v in args.fallback.split(",") if v]

    tmp = os.path.join(os.environ.get("TEMP", "."), "fill_gaps_drc.json")
    board = pcbnew.LoadBoard(args.board)
    layer = pcbnew.B_Cu if args.layer == "B.Cu" else pcbnew.F_Cu

    drc = run_drc(args.board, tmp)
    pairs = [(u["items"][0], u["items"][1])
             for u in drc.get("unconnected_items", [])
             if len(u.get("items", [])) >= 2]

    def dist_of(pair):
        (a, b) = pair
        return math.hypot(a["pos"]["x"] - b["pos"]["x"],
                          a["pos"]["y"] - b["pos"]["y"])

    if args.order == "short":
        pairs.sort(key=dist_of)
    elif args.order == "long":
        pairs.sort(key=dist_of, reverse=True)
    print("desconectados: %d (ordem: %s)" % (len(pairs), args.order))
    if not pairs:
        print("nada a fazer.")
        return 0

    grid = Grid(board, args.grid)
    masks = copper_masks(board, grid, layer)
    everything = np.zeros((grid.h, grid.w), bool)
    for m in masks.values():
        everything |= m
    edge = edge_block(board, grid, 0.5 + args.width / 2 + 0.05)
    empty = np.zeros((grid.h, grid.w), bool)

    ok = fail = 0
    neck = 0
    for pa, pb in pairs:
        na, nb = net_of(pa["description"]), net_of(pb["description"])
        if na != nb or not na:
            print("  par de redes diferentes: %s x %s" % (na or "?", nb or "?"))
            fail += 1
            continue
        base_width = 1.9 if na in IGN_NETS else args.width
        widths = [base_width]
        if base_width == args.width:
            widths += [w for w in args.fallback if w < base_width]
        own = masks.get(na, empty)
        other = everything & ~own

        chosen = None
        for width in widths:
            r_cells = int(math.ceil((args.clearance + width / 2 + args.margin)
                                    / args.grid))
            blocked = dilate(other, r_cells) | edge
            ctx = MaskCtx(grid, blocked)
            start = grid.idx(pa["pos"]["x"], pa["pos"]["y"])
            goal = grid.idx(pb["pos"]["x"], pb["pos"]["y"])
            blocked[start] = False
            blocked[goal] = False
            mult = congestion_multiplier(blocked, args.keep_cost) \
                if args.keep_cost > 0 else None
            path, _ = astar(blocked, start, goal, args.grid, mult)
            if path:
                chosen = (width, ctx, path)
                break
        if chosen is None:
            reach = flood_reaches(blocked, start, goal)
            print("  SEM CAMINHO: %s (%s -> %s)%s"
                  % (na, pa["description"][:40], pb["description"][:40],
                     "" if reach else "  [espaco fechado]"))
            fail += 1
            continue

        width, ctx, path = chosen
        pts = simplify(grid, ctx, path, args.grid)
        newmask = np.zeros((grid.h, grid.w), bool)
        for p1, p2 in zip(pts, pts[1:]):
            if p1 != p2:
                add_track(board, na, p1, p2, width, layer)
            newmask |= grid.seg_mask(p1[0], p1[1], p2[0], p2[1], width / 2)
        masks[na] = masks.get(na, empty) | newmask
        everything |= newmask
        length = sum(math.hypot(b[0] - a[0], b[1] - a[1])
                     for a, b in zip(pts, pts[1:]))
        if width < base_width:
            neck += 1
        print("  %-18s %5.1f mm, %d segmento(s), %s mm%s"
              % (na, length, len(pts) - 1, width,
                 "  <- neck-down" if width < base_width else ""))
        ok += 1

    board.BuildListOfNets()
    board.Save(args.out)
    print("ligados: %d (com neck-down: %d), sem solucao: %d -> %s"
          % (ok, neck, fail, args.out))
    drc2 = run_drc(args.out, tmp)
    print("desconectados apos esta passada: %d"
          % len(drc2.get("unconnected_items", [])))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())


if __name__ == "__main__":
    sys.exit(main())
