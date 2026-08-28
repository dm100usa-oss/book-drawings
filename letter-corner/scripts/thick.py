import json, re, numpy as np, cairosvg, io
from PIL import Image
from scipy import ndimage

SRC='/mnt/user-data/uploads'
LET='AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz'
SH={}
for f in ['abc','def','ghi','jkl','mno','pqr','stu','vwx','yz']:
    s=open(f'{SRC}/{f}.svg').read()
    vb=[float(x) for x in re.search(r'viewBox="([\d\. ]+)"',s).group(1).split()]
    SH[f]=vb[3]
json.dump(SH, open('work/sheet_h.json','w'))

R=json.load(open('work/refs2.json'))['L']

def rast(paths, sheet_h, box, px_h, pad=30):
    x0,x1,y0,y1=box
    sc=px_h/(y1-y0)
    W=int((x1-x0)*sc)+2*pad; H=int((y1-y0)*sc)+2*pad
    body=''.join(f'<path d="{d}"/>' for d in paths)
    svg=(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">'
         f'<rect width="{W}" height="{H}" fill="#fff"/>'
         f'<g transform="translate({pad},{pad}) scale({sc}) translate({-x0},{-y0})">'
         f'<g transform="translate(0,{sheet_h}) scale(0.1,-0.1)" fill="#000">{body}</g></g></svg>')
    png=cairosvg.svg2png(bytestring=svg.encode())
    a=np.array(Image.open(io.BytesIO(png)).convert('L'))
    return a<128, sc

def band(mask):
    if mask.sum()==0: return 0.0
    dt=ndimage.distance_transform_edt(mask)
    mx=ndimage.maximum_filter(dt,size=3)
    sk=(dt>1.0)&(dt>=mx-1e-9)
    v=dt[sk]
    return float(2*np.median(v)) if v.size else 0.0

res={}
print('%-2s %-4s  outlineW  channelW   (per 1000 of ref height)'%('','' ))
for ch in LET:
    g=json.load(open(f'work/letters/{ch}.json'))
    ar=[(b[1]-b[0])*(b[3]-b[2]) for b in g['boxes']]
    k=max(range(len(ar)), key=lambda i:ar[i])
    outline=[g['d'][k]]
    ob=g['boxes'][k]
    ink,sc=rast(outline, SH[g['sheet']], ob, 900)
    F=ndimage.binary_fill_holes(ink)
    chan=F & ~ink
    W=band(ink); C=band(chan)
    ref=R[ch]['ref']*sc            # ref height in px
    res[ch]=dict(W=W/ref*1000, C=C/ref*1000)
    print('%-2s %-4s   %7.1f   %7.1f'%(ch,g['sheet'],res[ch]['W'],res[ch]['C']))
json.dump(res, open('work/thickness.json','w'), indent=1)
w=[v['W'] for v in res.values()]; c=[v['C'] for v in res.values()]
print('outline  min %.1f  median %.1f  max %.1f'%(min(w),np.median(w),max(w)))
print('channel  min %.1f  median %.1f  max %.1f'%(min(c),np.median(c),max(c)))
