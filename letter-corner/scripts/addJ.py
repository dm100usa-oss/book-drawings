import re, json
from svgpathtools import parse_path
s=open('work/Jnew.svg').read()
vb=[float(x) for x in re.search(r'viewBox="([\d\. ]+)"',s).group(1).split()]
H=vb[3]
boxes=[];ds=[]
for d in re.findall(r'<path d="(.*?)"/>', s, re.S):
    dd=d.replace('\n',' ')
    try: p=parse_path(dd); x0,x1,y0,y1=p.bbox()
    except Exception: continue
    boxes.append([x0/10,x1/10,H-y1/10,H-y0/10]); ds.append(dd)
g=dict(sheet='Jnew', d=ds, boxes=boxes,
       x0=min(b[0] for b in boxes), x1=max(b[1] for b in boxes),
       y0=min(b[2] for b in boxes), y1=max(b[3] for b in boxes))
json.dump(g, open('work/letters/J.json','w'))
sh=json.load(open('work/sheet_h.json')); sh['Jnew']=H
json.dump(sh, open('work/sheet_h.json','w'))
ar=[(b[1]-b[0])*(b[3]-b[2]) for b in boxes]
k=max(range(len(ar)), key=lambda i:ar[i])
print('J outline', boxes[k], 'full', g['x0'],g['x1'],g['y0'],g['y1'], 'paths',len(ds))
# refresh refs2 for J
r=json.load(open('work/refs2.json'))
ob=boxes[k]
r['L']['J']=dict(sheet='Jnew', top=ob[2], base=ob[3], ref=ob[3]-ob[2],
                 x0=g['x0'],x1=g['x1'],y0=g['y0'],y1=g['y1'],
                 ox0=ob[0],ox1=ob[1],oy0=ob[2],oy1=ob[3])
json.dump(r, open('work/refs2.json','w'), indent=1)
print('J ref', r['L']['J']['ref'])
