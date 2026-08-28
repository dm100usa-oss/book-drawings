import json, io, numpy as np, cairosvg
from PIL import Image
from scipy import ndimage
LET='AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz'
CAPS=set('ABCDEFGHIJKLMNOPQRSTUVWXYZ'); ASC=set('bdfhklt')
SH=json.load(open('work/sheet_h.json')); R=json.load(open('work/refs2.json'))['L']
MJ=json.load(open('work/meas2.json')); PPU=MJ['PPU']
tref=lambda ch: 100.0 if (ch in CAPS or ch in ASC) else 50.0
PAD=90
def letter_ink(ch):
    g=json.load(open(f'work/letters/{ch}.json')); ref=R[ch]['ref']; sc=tref(ch)*PPU/ref
    big=[d for d,b in zip(g['d'],g['boxes']) if max(b[1]-b[0],b[3]-b[2])>0.20*ref]
    x0,x1,y0,y1=g['x0'],g['x1'],g['y0'],g['y1']
    W=int((x1-x0)*sc)+2*PAD; H=int((y1-y0)*sc)+2*PAD
    b=''.join(f'<path d="{d}"/>' for d in big)
    s=(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}"><rect width="{W}" height="{H}" fill="#fff"/>'
       f'<g transform="translate({PAD},{PAD}) scale({sc}) translate({-x0},{-y0})">'
       f'<g transform="translate(0,{SH[g["sheet"]]}) scale(0.1,-0.1)" fill="#000">{b}</g></g></svg>')
    return np.array(Image.open(io.BytesIO(cairosvg.svg2png(bytestring=s.encode()))).convert('L'))<128, sc
def skel_dt(m):
    dt=ndimage.distance_transform_edt(m)
    mx=ndimage.maximum_filter(dt,size=3)
    return dt[(dt>1.0)&(dt>=mx-1e-9)]
out={}
print(' ch   band W   channel C   limb T   (grid units)')
for ch in LET:
    ink,sc=letter_ink(ch)
    v=skel_dt(ink); W=2*np.median(v) if v.size else 0
    inner = ndimage.binary_fill_holes(ink) & ~ink
    u=skel_dt(inner)
    if u.size:
        h,edges=np.histogram(2*u, bins=40)
        C=float((edges[h.argmax()]+edges[h.argmax()+1])/2)
    else: C=0.0
    T=C+2*W
    out[ch]=dict(W=float(W)/PPU, C=C/PPU, T=float(T)/PPU)
    print('  %-2s  %6.2f     %6.2f    %6.2f'%(ch,W/PPU,C/PPU,T/PPU))
json.dump(out, open('work/limb.json','w'), indent=1)
import numpy as np
Ts=[v['T'] for v in out.values()]; Ws=[v['W'] for v in out.values()]
print('\nlimb T : min %.2f  median %.2f  max %.2f'%(min(Ts),np.median(Ts),max(Ts)))
print('band W : min %.2f  median %.2f  max %.2f'%(min(Ws),np.median(Ws),max(Ws)))
