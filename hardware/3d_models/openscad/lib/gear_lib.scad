// =============================================================================
//  Ignitor — biblioteca de engrenagens (OpenSCAD)
//  Involuta externa e interna, helicoidal (twist), trem planetario.
//  Todas as cotas vem por argumento (nao depende de params.scad).
//
//  Convencoes (ATENCAO: OpenSCAD usa GRAUS em toda a trigonometria):
//    - todos os angulos desta lib estao em GRAUS
//    - o dente 0 fica centrado no eixo +X (angulo 0)
//    - hand = +1 (direita) / -1 (esquerda): sun e planeta tem maos opostas,
//      anel e planeta tem a MESMA mao (engrenamento interno)
// =============================================================================

// ---- utilidades -------------------------------------------------------------
// funcao involuta com o angulo em graus (retorna graus)
function inv(a) = (tan(a) - a * PI / 180) * 180 / PI;
function flatten(l) = [for (x = l) for (y = x) y];
function rev(l) = [for (i = [0 : len(l) - 1]) l[len(l) - 1 - i]];

// Meia espessura angular do dente (graus) na circunferencia de referencia.
// bl = folga de flanco total (mm) — desconta metade em cada flanco.
function psi_pitch(m, z, alpha, x = 0, bl = 0) =
    ((PI / 2 + 2 * x * tan(alpha)) / z - bl / (m * z)) * 180 / PI;

// Angulo polar do flanco de involuta no raio rho (graus).
function th_inv(rho, rb, psi, alpha) =
    psi + inv(alpha) - inv(acos(min(1, max(-1, rb / rho))));

// Pontos [rho, theta_graus] de um flanco entre rho0 e rho1.
function flank_pts(rho0, rho1, rb, psi, alpha, n) =
    [for (i = [0 : n]) let (rho = rho0 + (rho1 - rho0) * i / n)
        [rho, th_inv(rho, rb, psi, alpha)]];

// Contorno 2D completo (poligono unico) de uma engrenagem externa.
// Abaixo da circunferencia de base o flanco e radial (aproximacao da trocoide).
function gear_outline(m, z, alpha, psi, ra, rf, nf = 7, nr = 3) =
    let (
        r  = m * z / 2,
        rb = r * cos(alpha),
        r0 = max(rf, rb),
        th_b = th_inv(r0, rb, psi, alpha),
        th_a = th_inv(ra, rb, psi, alpha),
        step = 360 / z,
        up = flank_pts(r0, ra, rb, psi, alpha, nf),      // raiz -> ponta, +theta
        lo = [for (p = up) [p[0], -p[1]]],               // raiz -> ponta, -theta
        tip = [for (i = [1 : nr]) let (t = -th_a + 2 * th_a * i / (nr + 1)) [ra, t]],
        tooth = concat([[rf, -th_b]], lo, tip, rev(up), [[rf, th_b]])
    )
    flatten([
        for (i = [0 : z - 1]) let (off = i * step)
            concat(
                [for (p = tooth) let (a = off + p[1]) [p[0] * cos(a), p[0] * sin(a)]],
                [for (j = [1 : nr - 1])
                    let (a = off + th_b + (step - 2 * th_b) * j / nr)
                        [rf * cos(a), rf * sin(a)]]
            )
    ]);

module gear_2d(m, z, alpha, x = 0, bl = 0, ha = 1.0, hf = 1.25, ra = 0, rf = 0) {
    r = m * z / 2;
    psi = psi_pitch(m, z, alpha, x, bl);
    ra_ = ra > 0 ? ra : r + m * (ha + x);
    rf_ = rf > 0 ? rf : r - m * (hf - x);
    polygon(points = gear_outline(m, z, alpha, psi, ra_, rf_));
}

// ---- engrenagem externa helicoidal -----------------------------------------
module gear_ext(m, z, alpha, beta, w, hand = 1, x = 0, bl = 0,
                ha = 1.0, hf = 1.25, slices = 0) {
    r  = m * z / 2;
    tw = hand * atan(w * tan(beta) / r);          // graus (atan ja vem em graus)
    ns = slices > 0 ? slices : max(4, ceil(abs(tw) / 2));
    linear_extrude(height = w, twist = tw, slices = ns, convexity = 10)
        gear_2d(m, z, alpha, x, bl, ha, hf);
}

// ---- anel interno helicoidal -----------------------------------------------
// O cortador e exatamente o "espaco" do dente: a ponta do anel cai em r-m*ha
// e a raiz em r+m*hf. phase = 180/zr coloca um DENTE do anel no eixo +X
// (o cortador fica com um espaco no +X).
module ring_cut(m, z, alpha, beta, w, hand = -1, bl = 0, x = 0,
                ha = 1.0, hf = 1.25, phase = 0, slices = 0) {
    r    = m * z / 2;
    ra_c = r + m * (hf + x);      // ponta do cortador -> raiz do anel
    rf_c = r - m * (ha - x);      // raiz do cortador -> ponta do anel
    tw   = hand * atan(w * tan(beta) / r);        // graus
    ns   = slices > 0 ? slices : max(6, ceil(abs(tw) / 1.5));
    rotate([0, 0, phase])
        linear_extrude(height = w, twist = tw, slices = ns, convexity = 10)
            gear_2d(m = m, z = z, alpha = alpha, bl = -bl, ra = ra_c, rf = rf_c);
}

module ring_gear(m, z, alpha, beta, w, rout, hand = -1, bl = 0, x = 0,
                 ha = 1.0, hf = 1.25, phase = 0, slices = 0) {
    difference() {
        linear_extrude(height = w, convexity = 10) circle(r = rout, $fn = 160);
        ring_cut(m, z, alpha, beta, w, hand, bl, x, ha, hf, phase, slices);
    }
}

// ---- esferas (rolamento de airsoft) ----------------------------------------
module ball_ring(r_pitch, d, n, z) {
    for (i = [0 : n - 1])
        rotate([0, 0, i * 360 / n])
            translate([r_pitch, 0, z]) sphere(d = d, $fn = 24);
}

// pista toroidal (para cortar com difference)
module ball_groove(r_pitch, r_groove, z) {
    translate([0, 0, z])
        rotate_extrude(convexity = 10, $fn = 120)
            translate([r_pitch, 0, 0]) circle(r = r_groove, $fn = 20);
}
