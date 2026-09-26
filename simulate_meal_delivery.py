import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

R = Path(__file__).resolve().parent
OUT = R / 'outputs' / 'figures'
OUT.mkdir(parents=True, exist_ok=True)

# Read only the field-bearing bile_1 group. The supplied file contains a later
# topology-only group that must not overwrite these scalar fields.
text = (R / 'FLOW.exnode').read_text().split('Group name: tree')[0]
nodes = {}
for block in text.split('Node:')[1:]:
    lines = block.splitlines()
    try:
        key = int(lines[0].split()[0])
        values = []
        for row in lines[1:7]:
            values.extend(float(x) for x in row.split() if x != r'\n')
        if len(values) >= 7:
            nodes[key] = {
                'p': [(values[0], values[2], values[4]),
                      (values[1], values[3], values[5])],
                'flow': values[7] if len(values) > 7 else 0.0,
            }
    except (ValueError, IndexError):
        continue

lines = (R / 'FLOW.exelem').read_text().splitlines()
edges = []
for i, line in enumerate(lines):
    if line.startswith(' Element:'):
        a, b = (int(x) for x in lines[i + 2].split()[:2])
        if a in nodes and b in nodes:
            edges.append((a, b))

flows = [max(0.0, (nodes[a]['flow'] + nodes[b]['flow']) / 2) for a, b in edges]
fmin, fmax = min(flows), max(flows)

def meal_delivery(t_min):
    """Illustrative common-delivery waveform in mL/min.

    The baseline and peak are display assumptions, not unit-validated outputs.
    """
    baseline = 0.50
    peak_increment = 2.00
    tau = 12.0
    return baseline + peak_increment * (t_min / tau) * math.exp(1 - t_min / tau) if t_min > 0 else baseline

W, H = 1800, 1100
im = Image.new('RGB', (W, H), 'white')
draw = ImageDraw.Draw(im)
FONT = 'C:/Windows/Fonts/arial.ttf'
font_title = ImageFont.truetype(FONT, 34)
font_panel = ImageFont.truetype(FONT, 28)
font_label = ImageFont.truetype(FONT, 24)
font_small = ImageFont.truetype(FONT, 20)
points = [n['p'][0] for n in nodes.values()]
lo = tuple(min(p[k] for p in points) for k in range(3))
hi = tuple(max(p[k] for p in points) for k in range(3))

def norm(x, a, b):
    return (x - a) / (b - a or 1)

def project(p, ox, oy, pw=850, ph=470):
    x = 0.08 + 0.84 * (0.86 * norm(p[0], lo[0], hi[0]) + 0.14 * norm(p[1], lo[1], hi[1]))
    y = 0.08 + 0.80 * (0.82 * (1 - norm(p[2], lo[2], hi[2])) + 0.18 * (1 - norm(p[1], lo[1], hi[1])))
    return ox + pw * x, oy + ph * y

def colour(value):
    value = max(0.0, min(1.0, value))
    return (int(190 - 125 * value), int(220 - 125 * value), int(248 - 70 * value))

def draw_tree(ox, oy, title, delivery):
    draw.text((ox + 20, oy + 12), title, fill='black', font=font_panel)
    for flow, (a, b) in zip(flows, edges):
        relative = (flow - fmin) / (fmax - fmin or 1)
        p0 = project(nodes[a]['p'][0], ox, oy)
        p1 = project(nodes[b]['p'][0], ox, oy)
        draw.line((*p0, *p1), fill=colour(relative), width=7)

draw.text((55, 35), 'Illustrative meal-dependent biliary delivery', fill='black', font=font_title)
draw_tree(0, 110, '(a) fasting baseline: 0.50 mL/min', 0.50)
draw_tree(900, 110, '(b) broad sensitivity peak: 2.50 mL/min', 2.50)

# A compact waveform panel beneath the two tree views.
x0, y0, pw, ph = 90, 825, 1620, 0
draw.text((90, 785), 'Common delivery waveform (illustrative)', fill='black', font=font_panel)
prev = None
for i in range(601):
    t = i / 10
    q = meal_delivery(t)
    x = 90 + 1620 * t / 60
    y = 1010 - 170 * (q - 0.3) / 2.4
    if prev:
        draw.line((*prev, x, y), fill=(35, 90, 170), width=5)
    prev = (x, y)
draw.line((90, 1010, 1710, 1010), fill=(80,80,80), width=2)
for label, x in [('0 min', 90), ('12 min', 414), ('30 min', 900), ('60 min', 1710)]:
    draw.text((x - 18, 1025), label, fill='black', font=font_small)
draw.text((90, 650), 'The branch pattern is held fixed; only total delivery varies with the meal-response waveform.', fill=(60, 60, 60), font=font_label)
draw.text((90, 685), 'Scenario assumptions: fasting 0.50 mL/min; broad peak 2.50 mL/min near 12 min; no new unit calibration.', fill=(60, 60, 60), font=font_label)
draw.text((90, 1060), 'Delivery rate (mL/min)', fill=(20,20,20), font=font_small)
im.save(OUT / 'figure4_meal_delivery.png')
print(f'nodes={len(nodes)} elements={len(edges)} fasting={meal_delivery(0):.2f} peak={meal_delivery(12):.2f} mL/min')
