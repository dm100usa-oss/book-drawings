import json, io, re, subprocess, math
import numpy as np, cairosvg
from PIL import Image
from scipy import ndimage
CAPS=set('ABCDEFGHIJKLMNOPQRSTUVWXYZ'); ASC=set('bdfhklt')
SH=json.load(open('work/sheet_h.json')); R=json.load(open('work/refs2.json'))['L']
MJ=json.load(open('work/meas2.json')); PPU=MJ['PPU']; WT=MJ['WT']; MT=MJ['MT']
det=json.load(open('work/detect.json')); DIG=json.load(open('work/digits.json'))
tref=lambda ch: MJ['CAP'] if (ch in CAPS or ch in ASC) else MJ['XH']
PAD=90; CIRC_R=3.7
V=json.load(open('work/vec/letters.json'))

def disk(r):
    r=int(r); y,x=np.ogrid[-r:r+1,-r:r+1]; return x*x+y*y<=r*r
def build(ch):
    g=json.load(open(f'work/letters/{ch}.json')); ref=R[ch]['ref']; sc=tref(ch)*PPU/ref
    big=[];small=[]
    for d,b in zip(g['d'],g['boxes']):
        (big if max(b[1]-b[0],b[3]-b[2])>0.20*ref else small).append(d)
    def rd(p):
        x0,x1,y0,y1=g['x0'],g['x1'],g['y0'],g['y1']
        W=int((x1-x0)*sc)+2*PAD; H=int((y1-y0)*sc)+2*PAD
        b=''.join(f'<path d="{d}"/>' for d in p)
        s=(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="#fff"/>'
           f'<g transform="translate({PAD},{PAD}) scale({sc}) translate({-x0},{-y0})">'
           f'<g transform="translate(0,{SH[g["sheet"]]}) scale(0.1,-0.1)" fill="#000">{b}</g></g></svg>')
        return np.array(Image.open(io.BytesIO(cairosvg.svg2png(bytestring=s.encode()))).convert('L'))<128
    def mo(m,d):
        n=int(round(abs(d)))
        if n==0: return m
        st=ndimage.generate_binary_structure(2,1)
        return ndimage.binary_dilation(m,st,n) if d>0 else ndimage.binary_erosion(m,st,n)
    B=mo(rd(big),(WT-MJ['m'][ch]['W'])/2); S=mo(rd(small),(MT-MJ['m'][ch]['M'])/2)
    H,W=B.shape; Y,X=np.ogrid[:H,:W]
    base=PAD+(R[ch]['base']-g['y0'])*sc
    for c in det[ch]['circles']:
        cx,cy,r=c['cx'],c['cy'],c['r']; rout=r+MT/2+2
        rr=int(rout*1.7)+int(r*1.05)+4
        y0=max(0,int(cy)-rr); y1=min(H,int(cy)+rr); x0=max(0,int(cx)-rr); x1=min(W,int(cx)+rr)
        sub=B[y0:y1,x0:x1]; patch=ndimage.binary_closing(sub,disk(r*1.05))
        yy,xx=np.ogrid[y0:y1,x0:x1]
        B[y0:y1,x0:x1]=np.where((yy-cy)**2+(xx-cx)**2<=(rout*1.7)**2, patch, sub)
        S=S & ~((Y-cy)**2+(X-cx)**2 <= (rout+2)**2)
    return B,S,base,(Y,X)
def trace(mask,name):
    Image.fromarray((~mask*255).astype(np.uint8)).save(f'/tmp/{name}.pbm')
    subprocess.run(['potrace','-s','-o',f'/tmp/{name}.svg','--turdsize','2','--alphamax','1.0',
                    '--opttolerance','0.2',f'/tmp/{name}.pbm'],check=True)
    s=open(f'/tmp/{name}.svg').read()
    vb=[float(x) for x in re.search(r'viewBox="([\d\. ]+)"',s).group(1).split()]
    return [d.replace('\n',' ') for d in re.findall(r'<path d="(.*?)"/>',s,re.S)], vb[3]
def repack(ch,B,S,base,extra_circles=(),extra=()):
    ink=B|S; ds,ph=trace(ink,ch+'_fix')
    ys,xs=np.where(ink)
    cs=list(V[ch]['circles'])+list(extra_circles)
    left=min(float(xs.min()), min((c['x']+V[ch]['left_px']/PPU-CIRC_R)*PPU for c in cs))
    # keep original left reference so previously stored circle x stay valid
    left=V[ch]['left_px']
    V[ch]=dict(paths=ds, ph=ph, PPU=PPU, base_px=base, left_px=left, circles=cs,
        w=float((max(xs.max(), max((c['x']+left/PPU+CIRC_R)*PPU for c in cs))-left)/PPU),
        top=float((ys.min()-base)/PPU), bot=float((ys.max()-base)/PPU), extra=list(extra))

# ---------- L : add circle 2 at the corner ----------
B,S,base,(Y,X)=build('L')
ys,xs=np.where(S); left=V['L']['left_px']
cx=float(np.median(xs[ys< base-40*PPU]))    # vertical dash column
cy=float(np.median(ys[xs> left+30*PPU]))    # horizontal dash row
repack('L',B,S,base,[dict(x=(cx-left)/PPU, y=(cy-base)/PPU, n=2)])
print('L circle2 at (%.1f,%.1f)'%((cx-left)/PPU,(cy-base)/PPU))

# ---------- e : add circle 2 at the right end of the bar ----------
B,S,base,(Y,X)=build('e')
left=V['e']['left_px']; y1=V['e']['circles'][0]['y']*PPU+base
ys,xs=np.where(S)
sel=np.abs(ys-y1)<3*PPU
mx=float(xs[sel].max())
cx=mx-CIRC_R*PPU
repack('e',B,S,base,[dict(x=(cx-left)/PPU, y=(y1-base)/PPU, n=2)])
print('e circle2 at (%.1f,%.1f)'%((cx-left)/PPU,(y1-base)/PPU))

# ---------- i : clear old digit inside the dot, add circle 2 ----------
B,S,base,(Y,X)=build('i')
left=V['i']['left_px']
lb,nb=ndimage.label(B)
best=None
for k in range(1,nb+1):
    yy,xx=np.where(lb==k); h=yy.max()-yy.min()+1; w=xx.max()-xx.min()+1
    if 0.7<w/h<1.4 and h<0.5*(-V['i']['top'])*PPU:
        best=(xx.mean(),yy.mean(),h/2)
dcx,dcy,dr=best
S=S & ~((Y-dcy)**2+(X-dcx)**2 <= (dr*1.30)**2)
B=B & ~((Y-dcy)**2+(X-dcx)**2 <= (dr*1.35)**2)
repack('i',B,S,base,[dict(x=(dcx-left)/PPU, y=(dcy-base)/PPU, n=2)],
       [dict(kind='ring', x=(dcx-left)/PPU, y=(dcy-base)/PPU, r=dr/PPU)])
print('i dot centre (%.1f,%.1f) r=%.1f'%((dcx-left)/PPU,(dcy-base)/PPU,dr/PPU))

# ---------- Q : remove wrong arrow, add correct one ----------
B,S,base,(Y,X)=build('Q')
left=V['Q']['left_px']
lb,n=ndimage.label(S); cands=[]
for k in range(1,n+1):
    yy,xx=np.where(lb==k); a=len(yy); h=yy.max()-yy.min()+1; w=xx.max()-xx.min()+1
    cands.append((a/(w*h), a, xx.mean(), yy.mean(), w, h, k))
# the wrong arrowhead: compact solid blob in the upper right of the oval
arrow=max([c for c in cands if c[0]>0.40 and c[3]<base-40*PPU], key=lambda c:c[1])
S[lb==arrow[6]]=False
print('Q removed arrow at (%.1f,%.1f) size %dx%d'%((arrow[2]-left)/PPU,(arrow[3]-base)/PPU,arrow[4],arrow[5]))
# new arrow: on the dashed loop, just clockwise of circle 1, pointing left
ys,xs=np.where(S)
oy,ox=ys.mean(),xs.mean()
c1=V['Q']['circles'][0]
th1=math.atan2(-(c1['y']*PPU+base-oy), c1['x']*PPU+left-ox)
best=None
for th in [th1-math.radians(t) for t in (14,16,18,20,22)]:
    d=(np.cos(np.arctan2(-(ys-oy),xs-ox)-th)); i=int(np.argmax(d))
    if best is None: best=(xs[i],ys[i],th)
ax,ay,th=best
ang=math.degrees(math.atan2(0,-1))  # pointing left
repack('Q',B,S,base,[],[dict(x=(ax-left)/PPU, y=(ay-base)/PPU, a=180.0, s=3.0)])
print('Q new arrow at (%.1f,%.1f)'%((ax-left)/PPU,(ay-base)/PPU))

# ---------- u : add missing arrow at end of stroke 1 ----------
c2=V['u']['circles'][1]
V['u']['extra']=[dict(x=c2['x'], y=c2['y']+CIRC_R+2.6, a=-90.0, s=3.0)]
print('u new arrow at (%.1f,%.1f)'%(c2['x'], c2['y']+CIRC_R+2.6))

for ch in V:
    V[ch].setdefault('extra',[])
json.dump(V, open('work/vec/letters.json','w'))
print('saved')
