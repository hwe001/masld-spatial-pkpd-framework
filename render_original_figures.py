import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
R=Path(r'C:/Users/pc/Documents/Codex/2026-06-05/let-s-use-three-js-to'); O=R/'outputs/figures'; O.mkdir(parents=True,exist_ok=True)
n={}; L=(R/'FLOW.exnode').read_text().splitlines(); i=0
while i<len(L):
 m=re.match(r'Node:\s+(\d+)',L[i])
 if not m: i+=1; continue
 v=[]; j=i+1
 while j<len(L) and len(v)<9:
  try: v += [float(x) for x in L[j].split()]
  except ValueError: pass
  j+=1
 if len(v)>=9: n[int(m.group(1))]={'p':[(v[0],v[2],v[4]),(v[1],v[3],v[5])],'r':v[6],'flow':v[7],'speed':v[8]}
 i=j
e=[]; L=(R/'FLOW.exelem').read_text().splitlines()
for i,s in enumerate(L):
 if re.match(r'\s*Element:',s):
  q=[int(x) for x in L[i+2].split()[:2]]
  if all(x in n for x in q): e.append(q)
p=[x['p'][0] for x in n.values()]; lo=tuple(min(x[k] for x in p) for k in range(3)); hi=tuple(max(x[k] for x in p) for k in range(3)); W,H=1600,1100
FONT='C:/Windows/Fonts/arial.ttf'
font_title=ImageFont.truetype(FONT,32)
font_label=ImageFont.truetype(FONT,26)
font_small=ImageFont.truetype(FONT,22)
def z(x,a,b): return (x-a)/(b-a or 1)
def P(q): return (W*(.1+.8*(.86*z(q[0],lo[0],hi[0])+.14*z(q[1],lo[1],hi[1]))),H*(.14+.64*(.82*(1-z(q[2],lo[2],hi[2]))+.18*(1-z(q[1],lo[1],hi[1])))))
def C(t,f): return (int(35+210*t),int(90+135*t),int(235-150*t)) if f=='flow' else (int(235-170*t),int(75+155*t),int(45+170*t))
def Hm(a,da,b,db,t):
 h00=2*t**3-3*t**2+1; h10=t**3-2*t**2+t; h01=-2*t**3+3*t**2; h11=t**3-t**2
 return tuple(h00*a[k]+h10*da[k]+h01*b[k]+h11*db[k] for k in range(3))
def render(path,f,title):
 vals=[n[k][f] for q in e for k in q]; mn,mx=min(vals),max(vals); r0,r1=min(x['r'] for x in n.values()),max(x['r'] for x in n.values()); im=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(im)
 for a,b in e:
  A,B=n[a],n[b]
  for q in range(20):
   t0,t1=q/20,(q+1)/20; q0=Hm(A['p'][0],A['p'][1],B['p'][0],B['p'][1],t0); q1=Hm(A['p'][0],A['p'][1],B['p'][0],B['p'][1],t1); x0,y0=P(q0); x1,y1=P(q1); val=A[f]+(B[f]-A[f])*(t0+t1)/2; w=max(4,int(4+12*z((A['r']+B['r'])/2,r0,r1))); d.line((x0,y0,x1,y1),fill=C(z(val,mn,mx),f),width=w)
 d.rectangle((30,25,760,105),fill='white',outline=(30,30,30),width=2); d.text((48,48),title,fill=(20,20,20),font=font_title); x0,y0,bw,bh=1120,895,360,30
 for k in range(bw): d.line((x0+k,y0,x0+k,y0+bh),fill=C(k/(bw-1),f),width=1)
 d.rectangle((x0,y0,x0+bw,y0+bh),outline=(30,30,30),width=2); d.text((x0,y0-38),f'{f} (native field; relative colour scale)',fill=(20,20,20),font=font_label); d.text((x0,y0+40),f'{mn:.3g}',fill=(20,20,20),font=font_small); d.text((x0+bw-55,y0+40),f'{mx:.3g}',fill=(20,20,20),font=font_small); im.save(path)
render(O/'figure2_original_tree_flow.png','flow','Complete reconstructed tree: native flow field'); render(O/'figure3_original_tree_speed.png','speed','Complete reconstructed tree: native speed field'); print(len(n),len(e))
