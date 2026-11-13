"""Example: generate to-scale SVG figures for the Class XII Solutions chapter. Usage: python make_figures.py out.json (then split into content/figures/*.svg)."""
import json, math, sys

W, H = 600, 360
X0, X1, Y0, Y1 = 80, 560, 300, 40  # plot box: x left/right, y bottom/top


def axes(xlabel, ylabel, xticks=(), yticks=()):
    s = [f'<line x1="{X0}" y1="{Y0}" x2="{X1}" y2="{Y0}" stroke="currentColor" stroke-width="1.5"/>',
         f'<line x1="{X0}" y1="{Y0}" x2="{X0}" y2="{Y1 - 10}" stroke="currentColor" stroke-width="1.5"/>',
         f'<text x="{(X0 + X1) / 2}" y="{Y0 + 40}" text-anchor="middle" font-size="14">{xlabel}</text>',
         f'<text x="22" y="{(Y0 + Y1) / 2}" text-anchor="middle" font-size="14" transform="rotate(-90 22 {(Y0 + Y1) / 2})">{ylabel}</text>']
    for x, lab in xticks:
        s.append(f'<line x1="{x}" y1="{Y0}" x2="{x}" y2="{Y0 + 5}" stroke="currentColor"/>')
        s.append(f'<text x="{x}" y="{Y0 + 20}" text-anchor="middle" font-size="12">{lab}</text>')
    for y, lab in yticks:
        s.append(f'<line x1="{X0 - 5}" y1="{y}" x2="{X0}" y2="{y}" stroke="currentColor"/>')
        s.append(f'<text x="{X0 - 9}" y="{y + 4}" text-anchor="end" font-size="12">{lab}</text>')
    return s


def svg(body, w=W, h=H):
    return f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">' + "".join(body) + "</svg>"


def poly(pts, cls="", dash=False, width=2.2):
    d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    extra = ' stroke-dasharray="6 5"' if dash else ""
    c = f' class="{cls}"' if cls else ' stroke="currentColor"'
    return f'<polyline points="{d}" fill="none"{c} stroke-width="{width}"{extra}/>'


out = {}

# 1. Raoult's law, ideal solution (NCERT Fig 1.3). p1° = 120 units, p2° = 230 units (pixels).
p1o, p2o = 120, 230
def px(x2):
    return X0 + (X1 - X0) * x2
def py(p):
    return Y0 - p
b = axes("Mole fraction", "Vapour pressure",
         [(X0, "x₁ = 1, x₂ = 0"), (X1, "x₁ = 0, x₂ = 1")], [])
b.append(f'<line x1="{X1}" y1="{Y0}" x2="{X1}" y2="{Y1 - 10}" stroke="currentColor" stroke-width="1.5"/>')
b.append(poly([(px(0), py(p1o)), (px(1), py(0))], dash=True))
b.append(poly([(px(0), py(0)), (px(1), py(p2o))], dash=True))
b.append(poly([(px(0), py(p1o)), (px(1), py(p2o))], cls="tm-acc", width=3))
b.append(f'<text x="{px(0) + 8}" y="{py(p1o) - 8}" font-size="13">p₁°</text>')
b.append(f'<text x="{px(1) - 8}" y="{py(p2o) - 8}" font-size="13" text-anchor="end">p₂°</text>')
b.append(f'<text x="{px(0.08)}" y="{py(p1o * 0.92) + 30}" font-size="13">I: p₁ = x₁p₁°</text>')
b.append(f'<text x="{px(0.70)}" y="{py(p2o * 0.70) + 30}" font-size="13">II: p₂ = x₂p₂°</text>')
b.append(f'<text x="{px(0.45)}" y="{py(p1o + (p2o - p1o) * 0.45) - 12}" font-size="13" class="tm-accf">III: p(total)</text>')
out["raoult_ideal"] = svg(b)

# 2. Positive and negative deviation (NCERT Fig 1.6), two panels side by side.
def panel(ox, sign, title):
    w, h = 270, 220
    x0, x1, y0 = ox + 30, ox + 30 + w, 30 + h
    s = [f'<line x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}" stroke="currentColor" stroke-width="1.5"/>',
         f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="30" stroke="currentColor" stroke-width="1.5"/>',
         f'<line x1="{x1}" y1="{y0}" x2="{x1}" y2="30" stroke="currentColor" stroke-width="1.5"/>',
         f'<text x="{(x0 + x1) / 2}" y="{y0 + 40}" text-anchor="middle" font-size="13">{title}</text>',
         f'<text x="{x0}" y="{y0 + 18}" text-anchor="middle" font-size="11">x_A = 1</text>',
         f'<text x="{x1}" y="{y0 + 18}" text-anchor="middle" font-size="11">x_B = 1</text>']
    pa, pb = 90, 150
    xs = [i / 40 for i in range(41)]
    def X(t): return x0 + (x1 - x0) * t
    def Y(p): return y0 - p
    # ideal (dashed)
    s.append(poly([(X(0), Y(pa)), (X(1), Y(0))], dash=True, width=1.4))
    s.append(poly([(X(0), Y(0)), (X(1), Y(pb))], dash=True, width=1.4))
    s.append(poly([(X(0), Y(pa)), (X(1), Y(pb))], dash=True, width=1.4))
    # real: Margules-type correction p_i = x_i p_i° exp(sign*k*(1-x_i)^2)
    k = 0.9
    pA = [(X(t), Y((1 - t) * pa * math.exp(sign * k * t * t))) for t in xs]
    pB = [(X(t), Y(t * pb * math.exp(sign * k * (1 - t) ** 2))) for t in xs]
    pT = [(X(t), Y((1 - t) * pa * math.exp(sign * k * t * t) + t * pb * math.exp(sign * k * (1 - t) ** 2))) for t in xs]
    s.append(poly(pA, width=2))
    s.append(poly(pB, width=2))
    s.append(poly(pT, cls="tm-acc", width=3))
    s.append(f'<text x="{X(0) + 6}" y="{Y(pa) - 6}" font-size="12">p_A°</text>')
    s.append(f'<text x="{X(1) - 6}" y="{Y(pb) - 6}" font-size="12" text-anchor="end">p_B°</text>')
    return s


b = panel(10, +1, "(a) Positive deviation") + panel(345, -1, "(b) Negative deviation")
b.append('<text x="330" y="20" text-anchor="middle" font-size="12">Dashed: Raoult\'s law (ideal). Solid: real solution. Thick: total vapour pressure.</text>')
out["deviations"] = svg(b, 660, 300)

# 3. Elevation of boiling point (NCERT Fig 1.7): p = A exp(-B/T)
T0, T1 = 340.0, 400.0
def tx(T): return X0 + (X1 - X0) * (T - T0) / (T1 - T0)
def ppy(p): return Y0 - p * 220 / 1.6
B_ = 4600.0
A_ = 1.013 * math.exp(B_ / 373.15)
def ps(T): return A_ * math.exp(-B_ / T)
f = 0.80  # solution vapour pressure = 0.93 x solvent's (exaggerated so the gap is visible)
Tb_sol = B_ / math.log(A_ * f / 1.013)
b = axes("Temperature / K", "Vapour pressure / bar", [], [(ppy(1.013), "1.013")])
Ts = [T0 + i * (T1 - T0) / 60 for i in range(61)]
b.append(poly([(tx(T), ppy(ps(T))) for T in Ts if ps(T) < 1.55], width=2.4))
b.append(poly([(tx(T), ppy(f * ps(T))) for T in Ts if f * ps(T) < 1.55], cls="tm-acc", width=2.4))
b.append(f'<line x1="{X0}" y1="{ppy(1.013)}" x2="{X1}" y2="{ppy(1.013)}" class="tm-muted" stroke-dasharray="4 4" stroke-width="1.2"/>')
for T, lab in ((373.15, "T_b°"), (Tb_sol, "T_b")):
    b.append(f'<line x1="{tx(T)}" y1="{ppy(1.013)}" x2="{tx(T)}" y2="{Y0}" class="tm-muted" stroke-dasharray="3 3"/>')
    b.append(f'<text x="{tx(T)}" y="{Y0 + 18}" text-anchor="middle" font-size="12">{lab}</text>')
mid = (tx(373.15) + tx(Tb_sol)) / 2
b.append(f'<text x="{mid}" y="{Y0 - 8}" text-anchor="middle" font-size="12" class="tm-accf">ΔT_b</text>')
b.append(f'<text x="{tx(352)}" y="{ppy(ps(352)) - 10}" font-size="12">pure solvent</text>')
b.append(f'<text x="{tx(388)}" y="{ppy(f * ps(388)) + 22}" font-size="12" class="tm-accf">solution</text>')
b.append(f'<text x="{X0 + 8}" y="{ppy(1.013) - 8}" font-size="11">atmospheric pressure</text>')
out["bp_elevation"] = svg(b)

# 4. Depression of freezing point (NCERT Fig 1.8): solid curve steeper than liquid curve.
T0, T1 = 258.0, 280.0
def tx2(T): return X0 + (X1 - X0) * (T - T0) / (T1 - T0)
def py2(p): return Y0 - p * 44.0
Tf0 = 273.15
Bl, Bs = 5400.0, 9000.0
pl = lambda T: 4.58 * math.exp(-Bl * (1 / T - 1 / Tf0))
psol = lambda T: 4.58 * math.exp(-Bs * (1 / T - 1 / Tf0))
fr = 0.80
# solution freezes where fr*pl(T) = psol(T): fr = exp(-(Bs-Bl)(1/T - 1/Tf0))
Tf = 1 / (1 / Tf0 - math.log(fr) / (Bs - Bl))
b = axes("Temperature / K", "Vapour pressure", [], [])
Ts = [T0 + i * (T1 - T0) / 60 for i in range(61)]
b.append(poly([(tx2(T), py2(psol(T))) for T in Ts if T <= Tf0 + 0.5], width=2.4))
b.append(poly([(tx2(T), py2(pl(T))) for T in Ts if T >= Tf - 4], width=2.4, dash=False))
b.append(poly([(tx2(T), py2(fr * pl(T))) for T in Ts if T >= Tf - 1], cls="tm-acc", width=2.4))
for T, lab in ((Tf0, "T_f°"), (Tf, "T_f")):
    b.append(f'<line x1="{tx2(T)}" y1="{py2(psol(T))}" x2="{tx2(T)}" y2="{Y0}" class="tm-muted" stroke-dasharray="3 3"/>')
    b.append(f'<text x="{tx2(T)}" y="{Y0 + 18}" text-anchor="middle" font-size="12">{lab}</text>')
b.append(f'<text x="{(tx2(Tf0) + tx2(Tf)) / 2}" y="{Y0 - 8}" text-anchor="middle" font-size="12" class="tm-accf">ΔT_f</text>')
b.append(f'<text x="{tx2(259)}" y="{py2(psol(259)) + 22}" font-size="12">frozen solvent</text>')
b.append(f'<text x="{tx2(264)}" y="{py2(pl(264)) - 12}" font-size="12">liquid solvent</text>')
b.append(f'<text x="{tx2(279)}" y="{py2(fr * pl(279)) + 22}" font-size="12" class="tm-accf">solution</text>')
out["fp_depression"] = svg(b)

# 5. NCERT Exercise 1.37 - acetone/chloroform data vs ideal lines.
xa = [0, 11.8, 23.4, 36.0, 50.8, 58.2, 64.5, 72.1]
pac = [0, 54.9, 110.1, 202.4, 322.7, 405.9, 454.1, 521.1]
pch = [632.8, 548.1, 469.4, 359.7, 257.7, 193.6, 161.2, 120.7]
pa0, pc0 = 741.8, 632.8
def ex(x): return X0 + (X1 - X0) * x / 100
def ey(p): return Y0 - p * 250 / 800
b = axes("100 × x(acetone)", "Vapour pressure / mm Hg",
         [(ex(v), str(v)) for v in (0, 20, 40, 60, 80, 100)], [(ey(v), str(v)) for v in (0, 200, 400, 600, 800)])
for v in (200, 400, 600, 800):
    b.append(f'<line x1="{X0}" y1="{ey(v)}" x2="{X1}" y2="{ey(v)}" class="tm-line" stroke-width="1"/>')
b.append(poly([(ex(0), ey(0)), (ex(100), ey(pa0))], dash=True, width=1.4))
b.append(poly([(ex(0), ey(pc0)), (ex(100), ey(0))], dash=True, width=1.4))
b.append(poly([(ex(0), ey(pc0)), (ex(100), ey(pa0))], dash=True, width=1.4))
b.append(poly([(ex(x), ey(p)) for x, p in zip(xa, pac)], width=2))
b.append(poly([(ex(x), ey(p)) for x, p in zip(xa, pch)], width=2))
b.append(poly([(ex(x), ey(p + q)) for x, p, q in zip(xa, pac, pch)], cls="tm-acc", width=3))
for x, p, q in zip(xa, pac, pch):
    b.append(f'<circle cx="{ex(x):.1f}" cy="{ey(p + q):.1f}" r="3.5" class="tm-accf"/>')
b.append(f'<text x="{ex(64)}" y="{ey(pc0 + (pa0 - pc0) * 0.64) - 10}" font-size="12">ideal p(total)</text>')
b.append(f'<text x="{ex(30)}" y="{ey(600) + 30}" font-size="12" class="tm-accf">measured p(total)</text>')
b.append(f'<text x="{ex(76)}" y="{ey(521.1) + 4}" font-size="12">p(acetone)</text>')
b.append(f'<text x="{ex(76)}" y="{ey(120.7) + 4}" font-size="12">p(chloroform)</text>')
out["ex137"] = svg(b)

# 6. Henry's law graph (NCERT Fig 1.2 style): straight line through origin, slope K_H
b = axes("Mole fraction of gas in solution, x", "Partial pressure of gas, p", [], [])
b.append(poly([(X0, Y0), (X1 - 40, Y1 + 20)], cls="tm-acc", width=3))
b.append(f'<text x="{X1 - 150}" y="{Y1 + 60}" font-size="13">slope = K_H</text>')
b.append(f'<text x="{X0 + 20}" y="{Y1 + 10}" font-size="13">p = K_H x  (constant T)</text>')
out["henry"] = svg(b)

# 7. Osmosis set-up (NCERT Fig 1.9 / 1.10) - schematic, not a graph.
b = [
    # beaker
    '<path d="M120 120 L120 320 Q120 330 130 330 L470 330 Q480 330 480 320 L480 120" fill="none" stroke="currentColor" stroke-width="2"/>',
    '<rect x="122" y="180" width="356" height="148" class="tm-soft"/>',
    '<text x="140" y="315" font-size="13">pure solvent (water)</text>',
    # thistle funnel: bulb + stem
    '<path d="M240 260 Q300 300 360 260 L360 240 L240 240 Z" fill="none" stroke="currentColor" stroke-width="2"/>',
    '<path d="M240 260 L360 260" class="tm-acc" stroke-width="3" stroke-dasharray="4 3"/>',
    '<rect x="292" y="40" width="16" height="200" fill="none" stroke="currentColor" stroke-width="2"/>',
    '<rect x="294" y="90" width="12" height="150" class="tm-accf" opacity="0.35"/>',
    '<path d="M242 242 L358 242 L358 258 L242 258 Z" class="tm-accf" opacity="0.35"/>',
    '<line x1="294" y1="140" x2="250" y2="140" stroke="currentColor" stroke-dasharray="3 3"/>',
    '<line x1="294" y1="90" x2="250" y2="90" stroke="currentColor" stroke-dasharray="3 3"/>',
    '<text x="245" y="136" font-size="12" text-anchor="end">initial level</text>',
    '<text x="245" y="94" font-size="12" text-anchor="end">level rises</text>',
    '<text x="370" y="232" font-size="12">solution</text>',
    '<text x="370" y="276" font-size="12" class="tm-accf">semipermeable membrane</text>',
    '<path d="M300 310 L300 272" class="tm-acc" stroke-width="2.5"/>',
    '<path d="M293 282 L300 270 L307 282" fill="none" class="tm-acc" stroke-width="2.5"/>',
    '<text x="312" y="300" font-size="12">solvent flows in</text>',
    '<path d="M300 22 L300 36" stroke="currentColor" stroke-width="2"/>',
    '<text x="312" y="30" font-size="12">apply π here to stop osmosis</text>',
]
out["osmosis"] = svg(b, 600, 345)

json.dump(out, open(sys.argv[1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print({k: len(v) for k, v in out.items()}, "Tb_sol", round(Tb_sol, 2), "Tf", round(Tf, 2))
