import json, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

src = Path(r'C:/Users/pc/Documents/Codex/2026-08-05/mi/work/hyu754.github.io/geo/Bile Pre_1.json')
out = Path(r'C:/Users/pc/Documents/Codex/2026-06-05/let-s-use-three-js-to/outputs/figures')
mesh = json.loads(src.read_text())
v = mesh['vertices']
pts = [(v[i], v[i+1], v[i+2]) for i in range(0, len(v), 3)]
xs=[p[0] for p in pts]; ys=[p[1] for p in pts]; zs=[p[2] for p in pts]
lo=(min(xs),min(ys),min(zs)); hi=(max(xs),max(ys),max(zs))
W,H=1600,900
def project(p):
    # wide oblique view, preserving the full mesh extent
    x,y,z=p
    u=(x-lo[0])/(hi[0]-lo[0] or 1)
    vv=(z-lo[2])/(hi[2]-lo[2] or 1)
    # slight depth cue from y
    u=0.08+0.84*(0.82*u+0.18*(y-lo[1])/(hi[1]-lo[1] or 1))
    q=0.08+0.84*(0.78*(1-vv)+0.22*(1-(y-lo[1])/(hi[1]-lo[1] or 1)))
    return int(u*W), int(q*H)
proj=[project(p) for p in pts]
edges=[]; f=mesh['faces']; i=0
while i < len(f):
    typ=f[i]; i+=1; n=4 if typ&1 else 3
    ids=f[i:i+n]; i+=n
    if typ&2: i+=1
    if typ&4: i+=n
    if typ&8: i+=n
    if typ&16: i+=1
    if typ&32: i+=n
    for a,b in zip(ids, ids[1:]+ids[:1]): edges.append((a,b))
def render(path, title, mode):
    im=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(im)
    # Draw depth-sorted mesh edges to retain the complete branching outline.
    for a,b in edges:
        x1,y1=proj[a]; x2,y2=proj[b]
        depth=(pts[a][1]+pts[b][1])*.5
        t=(depth-lo[1])/(hi[1]-lo[1] or 1)
        if mode==0: c=(40+int(160*t),110+int(90*t),235-int(80*t))
        else: c=(235-int(150*t),80+int(130*t),40+int(150*t))
        d.line((x1,y1,x2,y2),fill=c,width=2)
    d.rectangle((30,25,520,88),fill='white',outline=(30,30,30),width=2)
    d.text((48,42),title,fill=(20,20,20))
    # legend
    x0,y0=1170,720; barw,barh=300,24
    for k in range(barw):
        t=k/(barw-1); col=(int(40+195*t),int(110+80*t),int(235-80*t)) if mode==0 else (int(235-150*t),int(80+130*t),int(40+150*t))
        d.line((x0+k,y0,x0+k,y0+barh),fill=col,width=1)
    d.rectangle((x0,y0,x0+barw,y0+barh),outline=(30,30,30),width=1)
    d.text((x0,y0+35),'low',fill=(20,20,20)); d.text((x0+barw-25,y0+35),'high',fill=(20,20,20))
    d.text((x0,y0-28),'relative '+('flow' if mode==0 else 'speed'),fill=(20,20,20))
    im.save(path,quality=95)
render(out/'figure2_full_tree_flow.png','Full bile-tree view: flow field',0)
render(out/'figure3_full_tree_speed.png','Full bile-tree view: speed field',1)
print('wrote', out/'figure2_full_tree_flow.png', out/'figure3_full_tree_speed.png')
