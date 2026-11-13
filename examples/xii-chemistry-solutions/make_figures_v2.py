"""Three schematic figures added in v2 (NCERT Figs 1.1, 1.4, 1.11 were only described in words).
Schematic, not to scale. Writes content/figures/<name>.svg. Colours via currentColor / tm-* classes."""
import random
from pathlib import Path

OUT = Path(__file__).parent / "content" / "figures"
rnd = random.Random(11)


def svg(w, h, body, label):
    return (f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{label}">'
            + "".join(body) + "</svg>")


def dots(x0, y0, x1, y1, n, cls, r=4, avoid=None):
    out, pts = [], []
    tries = 0
    while len(pts) < n and tries < 5000:
        tries += 1
        x, y = rnd.uniform(x0 + r, x1 - r), rnd.uniform(y0 + r, y1 - r)
        if any((x - a) ** 2 + (y - b) ** 2 < (2.6 * r) ** 2 for a, b in pts):
            continue
        pts.append((x, y))
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" class="{cls}"/>')
    return out


# Fig 1.1: gas over its solution, before and after compression
def gas_pressure():
    b = []
    for i, (top, label, ngas, nsol) in enumerate([(40, "(a) gas in equilibrium with its solution", 12, 10), (110, "(b) piston pushed down: more gas dissolves", 12, 16)]):
        ox = 20 + i * 300
        b += [f'<rect x="{ox}" y="30" width="240" height="250" fill="none" stroke="currentColor" stroke-width="2"/>',
              f'<rect x="{ox + 2}" y="{top - 14}" width="236" height="12" class="tm-mutedf"/>',
              f'<line x1="{ox + 120}" y1="{top - 14}" x2="{ox + 120}" y2="8" stroke="currentColor" stroke-width="4"/>',
              f'<rect x="{ox + 2}" y="190" width="236" height="88" class="tm-soft"/>',
              f'<line x1="{ox}" y1="190" x2="{ox + 240}" y2="190" stroke="currentColor" stroke-width="1.5"/>']
        b += dots(ox + 6, top, ox + 234, 186, ngas, "tm-accf")
        b += dots(ox + 6, 194, ox + 234, 276, nsol, "tm-accf")
        b.append(f'<text x="{ox + 120}" y="304" text-anchor="middle" font-size="13">{label}</text>')
    b.append('<text x="290" y="160" text-anchor="middle" font-size="22">→</text>')
    return svg(580, 316, b, "Gas above a solution in a cylinder. Pushing the piston down crowds the gas particles, and more of them dissolve until a new equilibrium is reached.")


# Fig 1.4: surface of pure solvent vs solution with a non-volatile solute
def vp_surface():
    b = []
    for i, (title, frac) in enumerate([("(a) pure solvent", 0.0), ("(b) solution: solute particles at the surface", 0.35)]):
        ox = 20 + i * 300
        b += [f'<path d="M{ox} 60 L{ox} 260 L{ox + 240} 260 L{ox + 240} 60" fill="none" stroke="currentColor" stroke-width="2"/>',
              f'<rect x="{ox + 2}" y="130" width="236" height="128" class="tm-soft"/>']
        # surface row
        for k in range(12):
            x = ox + 12 + k * 19.5
            solute = (i == 1 and k % 3 == 1)
            b.append(f'<circle cx="{x:.1f}" cy="138" r="6" class="{"tm-mutedf" if solute else "tm-accf"}"/>')
            if not solute and k % 2 == 0:
                b.append(f'<path d="M{x:.1f} 124 L{x:.1f} {96 if i == 0 or k % 4 == 0 else 108}" class="tm-acc" stroke-width="2"/>')
        for k in range(6 if i == 0 else 4):
            b.append(f'<circle cx="{ox + 30 + k * 36:.1f}" cy="{80 + (k % 2) * 10}" r="5" class="tm-accf"/>')
        b.append(f'<text x="{ox + 120}" y="284" text-anchor="middle" font-size="13">{title}</text>')
    b.append('<circle cx="40" cy="20" r="6" class="tm-accf"/><text x="52" y="24" font-size="12">solvent particle</text>')
    b.append('<circle cx="190" cy="20" r="6" class="tm-mutedf"/><text x="202" y="24" font-size="12">non-volatile solute particle</text>')
    return svg(580, 296, b, "Pure solvent: every surface particle is solvent and can escape. Solution: some surface places are taken by solute particles, so fewer solvent particles escape and the vapour pressure is lower.")


# Fig 1.11: reverse osmosis
def reverse_osmosis():
    b = ['<rect x="40" y="70" width="420" height="190" fill="none" stroke="currentColor" stroke-width="2"/>',
         '<line x1="250" y1="70" x2="250" y2="260" class="tm-acc" stroke-width="3" stroke-dasharray="7 5"/>',
         '<rect x="42" y="110" width="206" height="148" class="tm-soft"/>',
         '<rect x="252" y="110" width="206" height="148" fill="none"/>',
         '<rect x="44" y="96" width="202" height="12" class="tm-mutedf"/>',
         '<line x1="145" y1="22" x2="145" y2="86" stroke="currentColor" stroke-width="4"/>',
         '<path d="M133 74 L145 90 L157 74" fill="none" stroke="currentColor" stroke-width="4"/>',
         '<text x="170" y="46" font-size="13">pressure larger than π</text>',
         '<path d="M205 190 L300 190" class="tm-acc" stroke-width="4"/>',
         '<path d="M288 180 L304 190 L288 200" fill="none" class="tm-acc" stroke-width="4"/>',
         '<text x="300" y="176" font-size="12">water</text>',
         '<text x="145" y="284" text-anchor="middle" font-size="13">sea water (solution)</text>',
         '<text x="355" y="284" text-anchor="middle" font-size="13">fresh water (solvent)</text>',
         '<text x="250" y="304" text-anchor="middle" font-size="12">semipermeable membrane, e.g. cellulose acetate</text>']
    b += dots(48, 116, 200, 254, 16, "tm-mutedf", r=4)
    return svg(500, 316, b, "Reverse osmosis: a pressure larger than the osmotic pressure on the sea-water side pushes water through the membrane to the fresh-water side; the salts stay behind.")


for name, fn in [("gas_pressure", gas_pressure), ("vp_surface", vp_surface), ("reverse_osmosis", reverse_osmosis)]:
    (OUT / f"{name}.svg").write_text(fn(), encoding="utf-8")
    print("wrote", name)
