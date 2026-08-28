import os
DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
NAME = lambda ch: ('up-' if ch.isupper() else 'low-') + ch

import json, os, io, re, subprocess
import numpy as np, cairosvg
from PIL import Image
from scipy import ndimage

import sys
LET=sys.argv[1] if len(sys.argv)>1 else 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz'
KEEP=set(LET)
if 'h' in LET and 'n' not in LET: LET='n'+LET
LET=('n'+LET.replace('n','')) if 'n' in LET else LET
NMASK=None
CAPS=set('ABCDEFGHIJKLMNOPQRSTUVWXYZ'); ASC=set('bdfhklt')
SH=json.load(open(DATA+'/sheet_h.json')); R=json.load(open(DATA+'/refs2.json'))['L']
MJ=json.load(open(DATA+'/meas2.json')); PPU=MJ['PPU']
det=json.load(open(DATA+'/detect.json')); DIG=json.load(open(DATA+'/digits.json'))
LIMB=json.load(open(DATA+'/limb.json'))
tref=lambda ch: 100.0 if (ch in CAPS or ch in ASC) else 50.0

T_TARGET = 13.0      # limb width, grid units
W_TARGET = 1.33      # outline band, grid units
M_TARGET = 0.74      # dashed trace, grid units  (was 0.51 -> +45%)
CIRC_R   = 3.7
PAD=110
DOT_UP=15.8   # gap from the top of the stem to the centre of the dot
DOT_R=7.5    # ring around the dot
PAD_DET=90   # build2.py detected the circles on a render with a 90px margin
os.makedirs(DATA+'/vec3', exist_ok=True)

def disk(r):
    r=int(max(1,r)); y,x=np.ogrid[-r:r+1,-r:r+1]; return x*x+y*y<=r*r
def dil(m,n):
    return m if n<=0 else (ndimage.distance_transform_edt(~m)<=n)
def ero(m,n):
    return m if n<=0 else (ndimage.distance_transform_edt(m)>n)
def close(m,n):
    return ero(dil(m,n),n)

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

def ring_outer(B, cx, cy, r_in):
    """outer radius of the old number ring, even if it does not touch the digit"""
    Hh,Ww=B.shape
    th=np.linspace(0,2*np.pi,240,endpoint=False)
    ct,st_=np.cos(th),np.sin(th)
    def frac(t):
        xx=np.clip((cx+ct*t).astype(int),0,Ww-1); yy=np.clip((cy+st_*t).astype(int),0,Hh-1)
        return B[yy,xx].mean()
    t=r_in; lim_in=r_in+0.35*r_in+8
    while t<lim_in and frac(t)<0.55: t+=1.0
    if t>=lim_in: return r_in+2.0
    last=t; lim_out=t+0.9*max(r_in,10)+30
    while t<lim_out and frac(t)>=0.55:
        last=t; t+=1.0
    return last+2.0

def strip_circles(B, circles, scale_factor, ROUT):
    """erase the old number circles out of the letter layer"""
    if not circles: return B, []
    Hh,Ww=B.shape; Y,X=np.ogrid[:Hh,:Ww]; pts=[]
    for c in circles:
        cx=PAD+(c['cx']-PAD_DET)*scale_factor; cy=PAD+(c['cy']-PAD_DET)*scale_factor
        ro=ROUT[(c['cx'],c['cy'])]
        B=B & ~((Y-cy)**2+(X-cx)**2 <= ro*ro)
        pts.append((cx,cy,ro))
    return B, pts

def seal(B, pts, protect):
    """bridge each hole locally, strictly inside the disk that was erased"""
    if not pts: return B
    Hh,Ww=B.shape; out=B.copy()
    for cx,cy,ro in pts:
        Rc=ro+3.0; W3=int(Rc*3)
        y0=max(0,int(cy-W3)); y1=min(Hh,int(cy+W3))
        x0=max(0,int(cx-W3)); x1=min(Ww,int(cx+W3))
        sub=B[y0:y1,x0:x1]
        yy,xx=np.ogrid[y0:y1,x0:x1]
        m=((yy-cy)**2+(xx-cx)**2 <= (ro+2.0)**2)
        out[y0:y1,x0:x1] |= (close(sub,Rc) & m & ~protect[y0:y1,x0:x1])
    return out

def deep_whites(ink):
    """solid glyph: everything except background and the deepest counters"""
    lw,nw=ndimage.label(~ink)
    lb,nb=ndimage.label(ink)
    bg=lw[0,0]
    adj_wb={}; adj_bw={}
    for dy,dx in ((0,1),(1,0)):
        for A,Bb,wfirst in ((lw,lb,True),(lb,lw,False)):
            a=A[:-dy or None,:-dx or None]; b=Bb[dy:,dx:]
            m=(a>0)&(b>0)
            if not m.any(): continue
            pr=np.unique(np.stack([a[m],b[m]]),axis=1)
            for u,v in pr.T:
                if wfirst: adj_wb.setdefault(int(u),set()).add(int(v)); adj_bw.setdefault(int(v),set()).add(int(u))
                else: adj_wb.setdefault(int(v),set()).add(int(u)); adj_bw.setdefault(int(u),set()).add(int(v))
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
    g=json.load(open(f'{DATA}/letters/{NAME(ch)}.json'))
    ref=R[ch]['ref']; Ht=tref(ch)*PPU
    sc0=Ht/ref
    big=[d for d,b in zip(g['d'],g['boxes']) if max(b[1]-b[0],b[3]-b[2])>0.20*ref]
    small=[d for d,b in zip(g['d'],g['boxes']) if max(b[1]-b[0],b[3]-b[2])<=0.20*ref]
    T0=LIMB[ch]['T']*PPU
    s=(Ht-T_TARGET*PPU)/(Ht-T0)
    k=Ht*(1-s)/2
    sc=sc0*s
    B0=render(g,big,sc)
    S0=render(g,small,sc)
    ROUT={}
    for c in det[ch]['circles']:
        cx=PAD+(c['cx']-PAD_DET)*s; cy=PAD+(c['cy']-PAD_DET)*s
        ROUT[(c['cx'],c['cy'])]=ring_outer(B0|S0, cx, cy, c['r']*s)
    B0,CPTS=strip_circles(B0, det[ch]['circles'], s, ROUT)
    B=seal(B0, CPTS, deep_whites(B0))
    G=outer_glyph(B, deep_whites(B))
    G = dil(G,k) if k>0 else ero(G,-k)
    ink = G & ~ero(G, W_TARGET*PPU)
    S=S0
    mw=band(S); d=(M_TARGET*PPU-mw)/2
    S = dil(S,d) if d>0 else ero(S,-d)
    Hh,Ww=ink.shape; Y,X=np.ogrid[:Hh,:Ww]
    circles=[]
    base=PAD+(R[ch]['base']-g['y0'])*sc + k
    for c,dg in zip(det[ch]['circles'],DIG[ch]):
        cx=PAD+(c['cx']-PAD_DET)*s; cy=PAD+(c['cy']-PAD_DET)*s
        ro=ROUT[(c['cx'],c['cy'])]
        S=S & ~((Y-cy)**2+(X-cx)**2 <= (ro+3)**2)
        rer=max(CIRC_R*PPU, ro)+2.0
        ink=ink & ~((Y-cy)**2+(X-cx)**2 <= rer*rer)
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
    if ch in ('i','j'):
        lb2,nb2=ndimage.label(ink)
        dot=None
        for kk in range(1,nb2+1):
            yy,xx=np.where(lb2==kk); hh=yy.max()-yy.min()+1; ww=xx.max()-xx.min()+1
            if 0.7<ww/hh<1.4 and hh<0.5*100*PPU: dot=(xx.mean(),yy.mean(),hh/2,kk)
        if dot:
            dcx,dcy,dr,dk=dot
            S=S & ~((Y-dcy)**2+(X-dcx)**2 <= (dr*1.30)**2)
            ink=ink & ~(lb2==dk)
            iy3,ix3=np.where(ink)
            xtop=float(iy3.min())                        # top of the stem
            dcy=xtop-DOT_UP*PPU                          # same gap for i and j
            near=iy3 < xtop+6.0*PPU                      # only the top of the stem
            dcx=float((ix3[near].min()+ix3[near].max())/2)
            dr=DOT_R*PPU
            circles=[c for c in circles if not (c['n']==2 and
                     (c['cx']-dcx)**2+(c['cy']-dcy)**2 < (dr*3.0)**2)]
            circles.append(dict(cx=dcx,cy=dcy,n=2))
            extra.append(dict(kind='ring', x=dcx, y=dcy, r=dr))
    if ch=='g':
        c1=[c for c in circles if c['n']==1][0]
        lbg,ng=ndimage.label(S)
        best=None
        for kk in range(1,ng+1):
            yy,xx=np.where(lbg==kk); a=len(yy)
            hh=yy.max()-yy.min()+1; ww=xx.max()-xx.min()+1
            if a<200 or a/(ww*hh)<0.35: continue
            d=((xx.mean()-c1['cx'])**2+(yy.mean()-c1['cy'])**2)**0.5
            if 2.5*PPU<d<10.0*PPU and (best is None or d<best[0]): best=(d,kk)
        if best: S[lbg==best[1]]=False
    if ch in ('h','r'):
        T=13.0*PPU
        iy2,ix2=np.where(G)
        bnd=(iy2>base-7*PPU)&(iy2<base-2*PPU)
        xb=np.sort(np.unique(ix2[bnd]))
        runs=[[float(xb[0]),float(xb[0])]]
        for a_,b_ in zip(xb,xb[1:]):
            if b_-a_>3: runs.append([float(b_),float(b_)])
            else: runs[-1][1]=float(b_)
        scx=(runs[0][0]+runs[0][1])/2
        ymid=base-50.0*PPU+T/2
        c2=[c for c in circles if c['n']==2][0]
        c2['cx'],c2['cy']=scx,base-6.5*PPU
        lbs,nls=ndimage.label(S)
        for kk in range(1,nls+1):
            yy,xx=np.where(lbs==kk)
            if xx.mean()>scx+0.20*T or yy.mean()>base-8*PPU: S[lbs==kk]=False
        if ch=='h' and NMASK is not None:
            Sn,scn,bn_=NMASK
            dy=int(round(base-bn_)); dx=int(round(scx-scn))
            ys_,xs_=np.where(Sn)
            yy=ys_+dy; xx=xs_+dx
            ok=(yy>=0)&(yy<S.shape[0])&(xx>=0)&(xx<S.shape[1])
            S[yy[ok],xx[ok]]=True
        else:
            def _cub(p0,p1,p2,p3,n=22):
                o=[]
                for t in [k/n for k in range(n+1)]:
                    u=1-t
                    o.append((u**3*p0[0]+3*u*u*t*p1[0]+3*u*t*t*p2[0]+t**3*p3[0],
                              u**3*p0[1]+3*u*u*t*p1[1]+3*u*t*t*p2[1]+t**3*p3[1]))
                return o
            top=float(iy2.min()); band2=(iy2<top+T)
            xr=float(ix2[band2].max())-T/2
            y_s=c2['cy']-(CIRC_R+1.0)*PPU
            extra.append(dict(kind='dash', pts=_cub(
                (scx,y_s),(scx,ymid-4.0*PPU),(xr-7.0*PPU,ymid-4.0*PPU),
                (xr-4.0*PPU,ymid+0.4*PPU))))
            extra.append(dict(x=xr, y=ymid+0.7*PPU, a=0.0, s=3.0*PPU))
        extra.append(dict(x=scx, y=c2['cy']-(CIRC_R+1.3)*PPU, a=90.0, s=3.0*PPU))
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
        extra.append(dict(x=c2['cx'], y=c2['cy']+(CIRC_R+1.1)*PPU, a=-90.0, s=3.0*PPU))
    if ch=='n':
        iyn,ixn=np.where(G); bn=(iyn>base-7*PPU)&(iyn<base-2*PPU)
        xbn=np.sort(np.unique(ixn[bn]))
        rn=[[float(xbn[0]),float(xbn[0])]]
        for a_,b_ in zip(xbn,xbn[1:]):
            if b_-a_>3: rn.append([float(b_),float(b_)])
            else: rn[-1][1]=float(b_)
        scn=(rn[0][0]+rn[0][1])/2
        Yn,Xn=np.ogrid[:S.shape[0],:S.shape[1]]
        NMASK=(S & ~(np.abs(Xn-scn)<0.22*13.0*PPU), scn, base)
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
        elif e.get('kind')=='dash':
            ex.append(dict(kind='dash', pts=[[(px-left)/PPUe,(py-base)/PPUe] for px,py in e['pts']]))
        else:
            ex.append(dict(x=(e['x']-left)/PPUe, y=(e['y']-base)/PPUe, a=e['a'], s=e['s']/PPUe))
    out[ch]=dict(paths=ds, ph=ph, PPU=PPUe, base_px=base, left_px=left,
        circles=[dict(x=(c['cx']-left)/PPUe, y=(c['cy']-base)/PPUe, n=c['n']) for c in circles],
        w=float((max(xs.max(), max(c['cx']+CIRC_R*PPU for c in circles) if circles else 0)-left)/PPUe),
        top=float((ys.min()-base)/PPUe), bot=float((ys.max()-base)/PPUe),
        s=s, k=k/PPU, extra=ex)
    print('%-2s s=%.4f k=%+.2f  top=%7.2f bot=%6.2f'%(ch,s,k/PPU,out[ch]['top'],out[ch]['bot']), flush=True)
# при сборке части букв дописываем их в общий файл, а не заменяем его
path=DATA+'/vec3/letters.json'
old={}
if os.path.exists(path):
    try: old=json.load(open(path))
    except Exception: old={}
old.update({k:v for k,v in out.items() if k in KEEP})
json.dump(old, open(path,'w'))
print('букв в файле:', len(old))
