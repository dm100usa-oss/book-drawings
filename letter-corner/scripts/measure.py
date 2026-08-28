import json, numpy as np, cairosvg, io
from PIL import Image
from scipy import ndimage

LET='AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz'
CAPS=set('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
ASCEND=set('bdfhklt'); DESC=set('gjpqy'); DOTTED=set('ij')
refs=json.load(open('work/refs.json'))

# sheet baselines from non-descender letters
sheets={}
for ch in LET:
    r=refs[ch]
    if ch in DESC or ch=='Q': continue
    sheets.setdefault(r['sheet'],[]).append(r['outline'][3])
SB={k:float(np.median(v)) for k,v in sheets.items()}

def render(paths, box, px_h=900, pad=40):
    x0,x1,y0,y1=box
    w=x1-x0; h=y1-y0
    sc=px_h/h
    W=int(w*sc)+2*pad; H=int(h*sc)+2*pad
    body=''.join(f'<path d="{d}"/>' for d in paths)
    svg=(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
         f'viewBox="0 0 {W} {H}"><g transform="translate({pad-x0*sc},{pad-y0*sc}) '
         f'scale({sc*0.1},{-sc*0.1}) translate(0,{-0})">{body}</g></svg>')
    return svg,sc,W,H

def bandwidth(mask):
    if mask.sum()==0: return 0.0
    dt=ndimage.distance_transform_edt(mask)
    mx=ndimage.maximum_filter(dt,size=3)
    sk=(dt>0.9)&(dt>=mx-1e-9)
    v=dt[sk]
    if v.size==0: return 0.0
    return float(2*np.median(v))

out={}
for ch in LET:
    g=json.load(open(f'work/letters/{ch}.json'))
    r=refs[ch]
    ob=r['outline']
    top=ob[2]
    base = SB[r['sheet']] if (ch in DESC or ch=='Q') else ob[3]
    ref = base-top
    out[ch]=dict(sheet=r['sheet'], top=top, base=base, ref=ref,
                 x0=g['x0'], x1=g['x1'], y0=g['y0'], y1=g['y1'],
                 ox0=ob[0], ox1=ob[1], oy0=ob[2], oy1=ob[3])
json.dump(dict(SB=SB, L=out), open('work/refs2.json','w'), indent=1)
for ch in LET:
    o=out[ch]
    kind = 'CAP' if ch in CAPS else ('ASC' if ch in ASCEND else 'XH')
    print('%-2s %-4s %-3s ref=%7.1f top=%7.1f base=%7.1f'%(ch,o['sheet'],kind,o['ref'],o['top'],o['base']))
