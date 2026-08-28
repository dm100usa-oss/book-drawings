import os
DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
NAME = lambda ch: ('up-' if ch.isupper() else 'low-') + ch

import re, os, json
from svgpathtools import parse_path

SRC=os.path.join(os.path.dirname(DATA),'source')
OUT=DATA+'/letters'; os.makedirs(OUT, exist_ok=True)
SHEETS={'abc':'AaBbCc','def':'DdEeFf','ghi':'GgHhIi','jkl':'JjKkLl','mno':'MmNnOo',
        'pqr':'PpQqRr','stu':'SsTtUu','vwx':'VvWwXx','yz':'YyZz'}
SPLITX={'stu':[4352.0],'vwx':[1448.0,4837.0]}

def clusters(boxes, tol=0):
    n=len(boxes); par=list(range(n))
    def find(a):
        while par[a]!=a: par[a]=par[par[a]]; a=par[a]
        return a
    for i in range(n):
        for j in range(i+1,n):
            a,b=boxes[i],boxes[j]
            if a[0]-tol<=b[1] and b[0]-tol<=a[1] and a[2]-tol<=b[3] and b[2]-tol<=a[3]:
                x,y=find(i),find(j)
                if x!=y: par[x]=y
    g={}
    for i in range(n): g.setdefault(find(i),[]).append(i)
    return list(g.values())

allletters={}
for f,names in SHEETS.items():
    s=open(f'{SRC}/{f}.svg').read()
    vb=[float(x) for x in re.search(r'viewBox="([\d\. ]+)"',s).group(1).split()]
    H=vb[3]
    boxes=[];ds=[]
    for d in re.findall(r'<path d="(.*?)"/>', s, re.S):
        dd=d.replace('\n',' ')
        try: p=parse_path(dd); x0,x1,y0,y1=p.bbox()
        except Exception: continue
        b=(x0/10,x1/10,H-y1/10,H-y0/10)
        if (b[3]-b[2])/max(b[1]-b[0],1e-9)>25 and (b[0]<40 or b[1]>vb[2]-40): continue
        boxes.append(b); ds.append(dd)
    cl=clusters(boxes)
    # split merged pairs
    if f in SPLITX:
        newcl=[]
        for c in cl:
            x0=min(boxes[i][0] for i in c); x1=max(boxes[i][1] for i in c)
            sp=[x for x in SPLITX[f] if x0<x<x1]
            if sp:
                x=sp[0]
                newcl.append([i for i in c if (boxes[i][0]+boxes[i][1])/2 < x])
                newcl.append([i for i in c if (boxes[i][0]+boxes[i][1])/2 >= x])
            else: newcl.append(c)
        cl=newcl
    cl=[c for c in cl if c]
    cl.sort(key=lambda c: min(boxes[i][0] for i in c))
    # merge dot clusters (small, sits above another cluster, x-range inside it)
    while len(cl)>len(names):
        merged=False
        for i,c in enumerate(cl):
            if len(c)>6: continue
            cx0=min(boxes[k][0] for k in c); cx1=max(boxes[k][1] for k in c)
            best=None
            for j,o in enumerate(cl):
                if j==i: continue
                ox0=min(boxes[k][0] for k in o); ox1=max(boxes[k][1] for k in o)
                ov=min(cx1,ox1)-max(cx0,ox0)
                if ov>0 and (best is None or ov>best[0]): best=(ov,j)
            if best:
                cl[best[1]]=cl[best[1]]+c; cl.pop(i); merged=True; break
        if not merged: break
    cl.sort(key=lambda c: min(boxes[i][0] for i in c))
    assert len(cl)==len(names), (f,len(cl))
    for ch,c in zip(names,cl):
        g=dict(sheet=f,
               d=[ds[i] for i in c],
               boxes=[list(boxes[i]) for i in c])
        g['x0']=min(b[0] for b in g['boxes']); g['x1']=max(b[1] for b in g['boxes'])
        g['y0']=min(b[2] for b in g['boxes']); g['y1']=max(b[3] for b in g['boxes'])
        json.dump(g, open(f'{OUT}/{ch}.json','w'))
        allletters[ch]=dict(sheet=f,n=len(c),x0=g['x0'],x1=g['x1'],y0=g['y0'],y1=g['y1'])
    print(f,'ok')

json.dump(allletters, open(DATA+'/geom.json','w'), indent=1)
for ch in 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz':
    v=allletters[ch]
    print('%-2s %-4s paths=%3d w=%7.1f h=%7.1f top=%7.1f bot=%7.1f'%(ch,v['sheet'],v['n'],v['x1']-v['x0'],v['y1']-v['y0'],v['y0'],v['y1']))
