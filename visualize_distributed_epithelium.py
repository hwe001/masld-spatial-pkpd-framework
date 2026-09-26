import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

R = Path(__file__).resolve().parent
O = R / 'outputs' / 'figures'
O.mkdir(parents=True, exist_ok=True)

txt = (R / 'FLOW.exnode').read_text().split('Group name: tree')[0]
nodes = {}
for block in txt.split('Node:')[1:]:
    lines = block.splitlines()
    try:
        key = int(lines[0].split()[0])
        v = []
        for row in lines[1:7]:
            v += [float(x) for x in row.split() if x != r'\n']
        if len(v) >= 7:
            nodes[key] = {'p': (v[0], v[2], v[4]), 'r': v[6]}
    except (ValueError, IndexError):
        pass

lines = (R / 'FLOW.exelem').read_text().splitlines()
edges = []
for i, line in enumerate(lines):
    if line.startswith(' Element:'):
        a, b = [int(x) for x in lines[i + 2].split()[:2]]
        if a in nodes and b in nodes:
            edges.append((a, b))

W, H = 1800, 900
im = Image.new('RGB', (W, H), 'white')
d = ImageDraw.Draw(im)
FONT = 'C:/Windows/Fonts/arial.ttf'
font_title = ImageFont.truetype(FONT, 32)
font_panel = ImageFont.truetype(FONT, 25)
font_label = ImageFont.truetype(FONT, 21)
font_small = ImageFont.truetype(FONT, 18)
pts = [n['p'] for n in nodes.values()]
lo = tuple(min(p[k] for p in pts) for k in range(3))
hi = tuple(max(p[k] for p in pts) for k in range(3))

def z(x, a, b): return (x - a) / (b - a or 1)
def P(p, ox):
    x = 55 + 530 * (0.86*z(p[0], lo[0], hi[0]) + 0.14*z(p[1], lo[1], hi[1]))
    y = 125 + 430 * (0.82*(1-z(p[2], lo[2], hi[2])) + 0.18*(1-z(p[1], lo[1], hi[1])))
    return ox + x, y
def green(x):
    x=max(0,min(1,x)); return (int(235-120*x), int(250-45*x), int(235-130*x))
def orange(x):
    x=max(0,min(1,x)); return (255, int(238-120*x), int(220-170*x))
def diverge(x):
    if x >= 0:
        q=min(1,x); return (int(235-170*q), int(235-80*q), int(245-30*q))
    q=min(1,-x); return (245, int(235-120*q), int(235-170*q))

radii = [(nodes[a]['r'] + nodes[b]['r']) / 2 for a, b in edges]
rmin, rmax = min(radii), max(radii)
def rn(v): return (v-rmin)/(rmax-rmin or 1)

d.text((45, 28), 'Distributed cholangiocyte secretion and absorption: parameterized sensitivity view', fill='black', font=font_title)
panels = [
    ('(a) secretion intensity per unit length', green),
    ('(b) absorption intensity per unit length', orange),
    ('(c) net epithelial contribution', diverge),
]
for pi, (title, fn) in enumerate(panels):
    ox = pi * 600
    d.text((ox+55, 65), title, fill='black', font=font_panel)
    for idx, (a, b) in enumerate(edges):
        q = rn(radii[idx])
        secretion = 0.25 + 0.75*(1-q)
        absorption = 0.15 + 0.60*q
        net = secretion - absorption
        value = secretion if pi == 0 else absorption if pi == 1 else net
        p0, p1 = P(nodes[a]['p'], ox), P(nodes[b]['p'], ox)
        d.line((*p0, *p1), fill=fn(value), width=7)

# Panel-specific colour bars make the normalization explicit without competing with the tree.
bars = [
    (green, 'normalized secretion intensity', '0', '1'),
    (orange, 'normalized absorption intensity', '0', '1'),
    (diverge, 'net contribution: absorption  <-  0  ->  secretion', '-1', '+1'),
]
for pi, (fn, label, left, right) in enumerate(bars):
    x0, y0, bw, bh = pi * 600 + 55, 690, 430, 22
    for k in range(bw):
        t = k / (bw - 1)
        value = 2*t - 1 if pi == 2 else t
        d.line((x0+k, y0, x0+k, y0+bh), fill=fn(value), width=1)
    d.rectangle((x0, y0, x0+bw, y0+bh), outline=(30,30,30), width=2)
    d.text((x0, y0-29), label, fill=(20,20,20), font=font_label)
    d.text((x0, y0+29), left, fill=(20,20,20), font=font_small)
    d.text((x0+bw-30, y0+29), right, fill=(20,20,20), font=font_small)
d.text((55, 825), 'Illustrative parameterization only: rates are not measured in this subject and are intended for sensitivity visualization.', fill=(55,55,55), font=font_label)
im.save(O/'figure5_distributed_epithelial_sensitivity.png')
print(f'nodes={len(nodes)} elements={len(edges)} output={O / "figure5_distributed_epithelial_sensitivity.png"}')
