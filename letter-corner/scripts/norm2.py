import json, os, io
import numpy as np, cairosvg
from PIL import Image
from scipy import ndimage

LET='AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz'
CAPS=set('ABCDEFGHIJKLMNOPQRSTUVWXYZ'); ASC=set('bdfhklt')
SH=json.load(open('work/sheet_h.json')); R=json.load(open('work/refs2.json'))['L']
CAP=100.0; XH=50.0; PPU=12.0
tref=lambda ch: CAP if (ch in CAPS or ch in ASC) else XH

def band(m):
    if m.sum()==0: return 0.0
    dt=ndimage.distance_transform_edt(m)
    mx=ndimage.maximum_filter(dt,size=3)
    sk=(dt>1.0)&(dt>=mx-1e-9); v=dt[sk]
    return float(2*np.median(v)) if v.size else 0.0

def parts(ch):
    g=json.load(open(f'work/letters/{ch}.json'))
    ref=R[ch]['ref']
    big=[];small=[]
    for d,b in zip(g['d'],g['boxes']):
        if max(b[1]-b[0], b[3]-b[2]) > 0.20*ref: big.append(d)
        else: small.append(d)
    return g,big,small

def render(g, paths, sc, pad):
    x0,x1,y0,y1=g['x0'],g['x1'],g['y0'],g['y1']
    W=int((x1-x0)*sc)+2*pad; H=int((y1-y0)*sc)+2*pad
    body=''.join(f'<path d="{d}"/>' for d in paths)
    svg=(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">'
         f'<rect width="{W}" height="{H}" fill="#fff"/>'
         f'<g transform="translate({pad},{pad}) scale({sc}) translate({-x0},{-y0})">'
         f'<g transform="translate(0,{SH[g["sheet"]]}) scale(0.1,-0.1)" fill="#000">{body}</g></g></svg>')
    png=cairosvg.svg2png(bytestring=svg.encode())
    return np.array(Image.open(io.BytesIO(png)).convert('L'))<128

m={}
for ch in LET:
    g,big,small=parts(ch)
    sc=tref(ch)*PPU/R[ch]['ref']
    m[ch]=dict(sc=sc, nbig=len(big), nsmall=len(small),
               W=band(render(g,big,sc,60)), M=band(render(g,small,sc,60)))
WT=float(np.median([v['W'] for v in m.values()]))
MT=float(np.median([v['M'] for v in m.values()]))
print('TARGET outline %.1fpx = %.2f units | markers %.1fpx = %.2f units'%(WT,WT/PPU,MT,MT/PPU))
for ch in LET:
    v=m[ch]
    print('  %-2s big=%3d small=%3d  W=%5.1f (d%+5.1f)  M=%5.1f (d%+5.1f)'%(
        ch,v['nbig'],v['nsmall'],v['W'],(WT-v['W'])/2,v['M'],(MT-v['M'])/2))
json.dump(dict(m=m,WT=WT,MT=MT,PPU=PPU,CAP=CAP,XH=XH), open('work/meas2.json','w'), indent=1)
