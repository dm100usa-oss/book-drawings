import json, os, io, re, subprocess
import numpy as np, cairosvg
from PIL import Image
from scipy import ndimage

LET='AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz'
CAPS=set('ABCDEFGHIJKLMNOPQRSTUVWXYZ'); ASC=set('bdfhklt')
SH=json.load(open('work/sheet_h.json')); R=json.load(open('work/refs2.json'))['L']
MJ=json.load(open('work/meas2.json')); PPU=MJ['PPU']
det=json.load(open('work/detect.json')); DIG=json.load(open('work/digits.json'))
LIMB=json.load(open('work/limb.json'))
tref=lambda ch: 100.0 if (ch in CAPS or ch in ASC) else 50.0

T_TARGET = 13.0      # limb width, grid units
W_TARGET = 1.33      # outline band, grid units
M_TARGET = 0.74      # dashed trace, grid units  (was 0.51 -> +45%)
CIRC_R   = 3.7
PAD=110
os.makedirs('work/vec2', exist_ok=True)

def disk(r):
    r=int(max(1,r)); y,x=np.ogrid[-r:r+1,-r:r+1]; return x*x+y*y<=r*r
def dil(m,n):
    n=int(round(n))
    return m if n<=0 else ndimage.binary_dilation(m,disk(n))
def ero(m,n):
    n=int(round(n))
    return m if n<=0 else ndimage.binary_erosion(m,disk(n))

def left0(m):
    ys,xs=np.where(m); return float(xs.min())

def render(g,paths,sc):
    x0,x1,y0,y1=g['x0'],g['x1'],g['y0'],g['y1']
    W=int((x1-x0)*sc)+2*PAD; H=int((y1-y0)*sc)+2*PAD
    b=''.join(f'<path d="{d}"/>' for d in paths)
    s=(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">'
       f'<rect width="{W}" height="{H}" fill="#fff"/>'
       f'<g transform="translate({PAD},{PAD}) scale({sc}) translate({-x0},{-y0})">'
       f'<g transform="translate(0,{SH[g["sheet"]]}) scale(0.1,-0.1)" fill="#000">{b}</g></g></svg>')
    return np.array(Image.open(io.BytesIO(cairosvg.svg2png(bytestring=s.encode()))).convert('L'))<128

def seal(B, circles, scale_factor, protect):
    """close the gaps the old number circles cut in the letter band"""
    if not circles: return B
    Rc=int(max(c['r'] for c in circles)*scale_factor*1.15)+2
    C=ndimage.binary_closing(B, disk(Rc))
    return (B | (C & ~protect))

def deep_whites(ink):
    """solid glyph: everything except background and the deepest counters"""
    lw,nw=ndimage.label(~ink)
    lb,nb=ndimage.label(ink)
    bg=lw[0,0]
    # adjacency white<->black
    adj_wb={}; adj_bw={}
    for dy,dx in ((0,1),(1,0)):
        a=lw[:-dy or None,:-dx or None]; b=lb[dy:,dx:]
        m=(a>0)&(b>0)
        for w,k in zip(a[m].ravel(), b[m].ravel()):
            adj_wb.setdefault(w,set()).add(k); adj_bw.setdefault(k,set()).add(w)
        a=lb[:-dy or None,:-dx or None]; b=lw[dy:,dx:]
        m=(a>0)&(b>0)
        for k,w in zip(a[m].ravel(), b[m].ravel()):
            adj_wb.setdefault(w,set()).add(k); adj_bw.setdefault(k,set()).add(w)
    lev={('w',bg):0}; q=[('w',bg)]
    while q:
        t,i=q.pop(0); d=lev[(t,i)]
        nb_=adj_wb.get(i,()) if t=='w' else adj_bw.get(i,())
        for j in nb_:
            key=('b',j) if t=='w' else ('w',j)
            if key not in lev:
                lev[key]=d+1; q.append(key)
    deep=np.zeros_like(ink)
    for (t,i),d in lev.items():
        if t=='w' and d>=3 and i!=bg:
            deep |= (lw==i)
    return deep

def outer_glyph(ink, deep):
    return ndimage.binary_fill_holes(ink) & ~deep

def band(m):
    if m.sum()==0: return 0.0
    dt=ndimage.distance_transform_edt(m)
    mx=ndimage.maximum_filter(dt,size=3)
    v=dt[(dt>1.0)&(dt>=mx-1e-9)]
    return float(2*np.median(v)) if v.size else 0.0

def trace(mask,name):
    Image.fromarray((~mask*255).astype(np.uint8)).save(f'/tmp/{name}.pbm')
    subprocess.run(['potrace','-s','-o',f'/tmp/{name}.svg','--turdsize','2','--alphamax','1.0',
                    '--opttolerance','0.2',f'/tmp/{name}.pbm'],check=True)
    s=open(f'/tmp/{name}.svg').read()
    vb=[float(x) for x in re.search(r'viewBox="([\d\. ]+)"',s).group(1).split()]
    return [d.replace('\n',' ') for d in re.findall(r'<path d="(.*?)"/>',s,re.S)], vb[3]

out={}
for ch in LET:
    g=json.load(open(f'work/letters/{ch}.json'))
    ref=R[ch]['ref']; Ht=tref(ch)*PPU
    sc0=Ht/ref
    big=[d for d,b in zip(g['d'],g['boxes']) if max(b[1]-b[0],b[3]-b[2])>0.20*ref]
    small=[d for d,b in zip(g['d'],g['boxes']) if max(b[1]-b[0],b[3]-b[2])<=0.20*ref]
    T0=LIMB[ch]['T']*PPU
    s=(Ht-T_TARGET*PPU)/(Ht-T0)
    k=Ht*(1-s)/2
    sc=sc0*s
    B0=render(g,big,sc)
    deep0=deep_whites(B0)
    B=seal(B0, det[ch]['circles'], s, deep0)
    G=outer_glyph(B, deep_whites(B))
    G = dil(G,k) if k>0 else ero(G,-k)
    ink = G & ~ero(G, W_TARGET*PPU)
    S=render(g,small,sc)
    mw=band(S); d=(M_TARGET*PPU-mw)/2
    S = dil(S,d) if d>0 else ero(S,-d)
    Hh,Ww=ink.shape; Y,X=np.ogrid[:Hh,:Ww]
    circles=[]
    base=PAD+(R[ch]['base']-g['y0'])*sc + k
    for c,dg in zip(det[ch]['circles'],DIG[ch]):
        cx=PAD+(c['cx']-PAD)*s; cy=PAD+(c['cy']-PAD)*s
        S=S & ~((Y-cy)**2+(X-cx)**2 <= (c['r']*s+14)**2)
        ink=ink & ~((Y-cy)**2+(X-cx)**2 <= (CIRC_R*PPU)**2)
        circles.append(dict(cx=cx,cy=cy,n=dg))
    extra=[]
    import math as _m
    if ch=='L':
        ys_,xs_=np.where(S)
        lx=left0(ink) if ink.any() else float(np.where(S)[1].min())
        colsel=ys_< base-40*PPU; rowsel=xs_> lx+30*PPU
        ccx=float(np.median(xs_[colsel])) if colsel.any() else float(np.median(xs_))
        ccy=float(np.median(ys_[rowsel])) if rowsel.any() else float(base-4*PPU)
        circles.append(dict(cx=ccx,cy=ccy,n=2))
    if ch=='e':
        y1=circles[0]['cy']; ys_,xs_=np.where(S)
        sel=np.abs(ys_-y1)<3*PPU
        circles.append(dict(cx=float(xs_[sel].max())-CIRC_R*PPU, cy=y1, n=2))
    if ch=='i':
        lb2,nb2=ndimage.label(ink)
        dot=None
        for kk in range(1,nb2+1):
            yy,xx=np.where(lb2==kk); hh=yy.max()-yy.min()+1; ww=xx.max()-xx.min()+1
            if 0.7<ww/hh<1.4 and hh<0.5*100*PPU: dot=(xx.mean(),yy.mean(),hh/2)
        if dot:
            dcx,dcy,dr=dot
            S=S & ~((Y-dcy)**2+(X-dcx)**2 <= (dr*1.30)**2)
            ink=ink & ~((Y-dcy)**2+(X-dcx)**2 <= (dr*1.35)**2)
            circles.append(dict(cx=dcx,cy=dcy,n=2))
            extra.append(dict(kind='ring', x=dcx, y=dcy, r=dr))
    if ch=='Q':
        lb3,n3=ndimage.label(S); cands=[]
        for kk in range(1,n3+1):
            yy,xx=np.where(lb3==kk); a=len(yy)
            hh=yy.max()-yy.min()+1; ww=xx.max()-xx.min()+1
            cands.append((a/(ww*hh),a,xx.mean(),yy.mean(),kk))
        up=[c for c in cands if c[0]>0.40 and c[3]<base-40*PPU]
        if up:
            bad=max(up,key=lambda c:c[1]); S[lb3==bad[4]]=False
        ys_,xs_=np.where(S); oy,ox=ys_.mean(),xs_.mean()
        c1=circles[0]
        th1=_m.atan2(-(c1['cy']-oy), c1['cx']-ox)
        th=th1-_m.radians(18)
        ang=np.arctan2(-(ys_-oy), xs_-ox)
        i2=int(np.argmax(np.cos(ang-th)))
        extra.append(dict(x=float(xs_[i2]), y=float(ys_[i2]), a=180.0, s=3.0*PPU))
    if ch=='u':
        c2=circles[1]
        extra.append(dict(x=c2['cx'], y=c2['cy']+(CIRC_R+2.6)*PPU, a=-90.0, s=3.0*PPU))
    full=ink|S
    ds,ph=trace(full,ch+'_r')
    ys,xs=np.where(full)
    iy,ix=np.where(ink)
    DESC=set('gjpqy')
    base_eff = base if (ch in DESC or ch=='Q') else float(iy.max())
    Hact = base_eff-float(iy.min())
    PPUe = Hact/tref(ch)
    base = base_eff
    left=min(float(xs.min()), min(c['cx']-CIRC_R*PPU for c in circles) if circles else 1e9)
    ex=[]
    for e in extra:
        if e.get('kind')=='ring':
            ex.append(dict(kind='ring', x=(e['x']-left)/PPUe, y=(e['y']-base)/PPUe, r=e['r']/PPUe))
        else:
            ex.append(dict(x=(e['x']-left)/PPUe, y=(e['y']-base)/PPUe, a=e['a'], s=e['s']/PPUe))
    out[ch]=dict(paths=ds, ph=ph, PPU=PPUe, base_px=base, left_px=left,
        circles=[dict(x=(c['cx']-left)/PPUe, y=(c['cy']-base)/PPUe, n=c['n']) for c in circles],
        w=float((max(xs.max(), max(c['cx']+CIRC_R*PPU for c in circles) if circles else 0)-left)/PPUe),
        top=float((ys.min()-base)/PPUe), bot=float((ys.max()-base)/PPUe),
        s=s, k=k/PPU, extra=ex)
    print('%-2s s=%.4f k=%+.2f  top=%7.2f bot=%6.2f'%(ch,s,k/PPU,out[ch]['top'],out[ch]['bot']), flush=True)
json.dump(out, open('work/vec2/letters.json','w'))
