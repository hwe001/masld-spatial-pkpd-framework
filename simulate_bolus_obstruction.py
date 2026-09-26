import re, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

R=Path(r'C:/Users/pc/Documents/Codex/2026-06-05/let-s-use-three-js-to'); O=R/'outputs'/'figures'; O.mkdir(parents=True,exist_ok=True)
# FLOW.exnode also contains a later topology-only ``tree`` group.  The
# field-bearing ``bile_1`` group is the source for this transport pilot.
exnode_text=(R/'FLOW.exnode').read_text().split('Group name: tree')[0]
blocks=exnode_text.split('Node:')[1:]; nodes={}
for b in blocks:
    L=b.splitlines()
    try:
        key=int(L[0].split()[0]); v=[]
        for row in L[1:7]: v += [float(x) for x in row.split() if x != r'\n']
        if len(v) < 7: continue
        nodes[key]={'p':[(v[0],v[2],v[4]),(v[1],v[3],v[5])],
                    'r':v[6], 'flow':v[7] if len(v)>7 else None,
                    'speed':v[8] if len(v)>8 else None}
    except (ValueError,IndexError): pass
# Node 8072 in the supplied file has no scalar field values.  Keep its
# geometry and use the median imported speed only for this illustrative pilot.
speeds=[n['speed'] for n in nodes.values() if n['speed'] is not None]
fallback_speed=sorted(speeds)[len(speeds)//2]
for n in nodes.values():
    n['speed']=n['speed'] if n['speed'] is not None else fallback_speed
    n['flow']=n['flow'] if n['flow'] is not None else 0.0
L=(R/'FLOW.exelem').read_text().splitlines(); edges=[]
for i,s in enumerate(L):
    if s.startswith(' Element:'):
        q=[int(x) for x in L[i+2].split()[:2]]
        if q[0] in nodes and q[1] in nodes: edges.append(q)
adj={k:[] for k in nodes}
for ei,(a,b) in enumerate(edges):
    pa,pb=nodes[a]['p'][0],nodes[b]['p'][0]
    length=math.sqrt(sum((pa[k]-pb[k])**2 for k in range(3)))
    speed=max(1e-9,(nodes[a]['speed']+nodes[b]['speed'])/2)
    adj[a].append((b,ei,length/speed)); adj[b].append((a,ei,length/speed))
deg={k:len(v) for k,v in adj.items()}; outlet=max((k for k,d in deg.items() if d==1),key=lambda k:nodes[k]['r'])
target=max(range(len(edges)),key=lambda i:(nodes[edges[i][0]]['r']+nodes[edges[i][1]]['r'])/2)
def distances(stenosis):
    d={outlet:0.0}; seen=set(); todo=[(0.0,outlet)]
    while todo:
        todo.sort(); dist,u=todo.pop(0)
        if u in seen: continue
        seen.add(u)
        for v,ei,dt in adj[u]:
            mult=(1/(1-stenosis))**2 if ei==target and stenosis<1 else (1e6 if ei==target else 1)
            nd=dist+dt*mult
            if nd<d.get(v,1e99): d[v]=nd; todo.append((nd,v))
    return d
base=distances(0); t_eval=max(base.values())*.55; bolus_duration=max(1.0,t_eval*.12)
W,H=1600,1050
FONT='C:/Windows/Fonts/arial.ttf'
font_panel=ImageFont.truetype(FONT,30)
font_note=ImageFont.truetype(FONT,22)
font_legend=ImageFont.truetype(FONT,24)
pts=[n['p'][0] for n in nodes.values()]; lo=tuple(min(p[k] for p in pts) for k in range(3)); hi=tuple(max(p[k] for p in pts) for k in range(3))
def z(x,a,b): return (x-a)/(b-a or 1)
def P(p,ox,oy): return (ox+800*(.06+.86*(.86*z(p[0],lo[0],hi[0])+.14*z(p[1],lo[1],hi[1]))),oy+525*(.08+.68*(.82*(1-z(p[2],lo[2],hi[2]))+.18*(1-z(p[1],lo[1],hi[1])))))
def col(c):
    # Keep low-concentration branches visible on the white manuscript page.
    c=max(0,min(1,c)); return (int(185-125*c),int(215-125*c),int(245-70*c))
scenarios=[0,.25,.5,.75]
def render():
    im=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(im)
    maxd=max(base.values()); 
    for pi,sten in enumerate(scenarios):
        ox=(pi%2)*800; oy=(pi//2)*525
        d.text((ox+24,oy+18),f'({chr(97+pi)}) virtual radius reduction: {int(sten*100)}%',fill='black',font=font_panel)
        dist=distances(sten)
        for ei,(a,b) in enumerate(edges):
            da,db=dist.get(a,1e9),dist.get(b,1e9); c=0.0
            for q in range(16):
                t0=q/16; t1=(q+1)/16; dd=da+(db-da)*(t0+t1)/2
                # finite-duration bolus with a soft front/back for a readable snapshot
                c=max(c,math.exp(-((dd-t_eval)/(max(1,bolus_duration*.35)))**2))
            p0,p1=P(nodes[a]['p'][0],ox,oy),P(nodes[b]['p'][0],ox,oy); d.line((p0[0],p0[1],p1[0],p1[1]),fill=col(c),width=6 if ei==target else 4)
        if pi==0: d.text((ox+24,oy+470),f't = {t_eval:.1f} display time units; bolus duration = {bolus_duration:.1f}',fill='black',font=font_note)
    bx,by=1120,945
    for k in range(360): d.line((bx+k,by,bx+k,by+26),fill=col(k/359),width=1)
    d.rectangle((bx,by,bx+360,by+26),outline='black',width=2); d.text((bx,by-38),'normalized concentration C/C0',fill='black',font=font_legend); d.text((bx,by+34),'0',fill='black',font=font_note); d.text((bx+340,by+34),'1',fill='black',font=font_note)
    d.text((24,1020),'Scenario model: retrograde injection at the common-duct end; stenosis changes local advective travel time. Results are not patient-calibrated.',fill=(60,60,60),font=font_note)
    im.save(O/'figure3_transient_obstruction.png')
render()
print(f'nodes={len(nodes)} elements={len(edges)} outlet={outlet} target_element={target} baseline_time={t_eval:.3f} bolus_duration={bolus_duration:.3f}')
