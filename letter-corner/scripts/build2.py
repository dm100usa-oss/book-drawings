import json, os, io
import numpy as np, cairosvg
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

LET='AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz'
CAPS=set('ABCDEFGHIJKLMNOPQRSTUVWXYZ'); ASC=set('bdfhklt')
SH=json.load(open('work/sheet_h.json')); R=json.load(open('work/refs2.json'))['L']
MJ=json.load(open('work/meas2.json')); PPU=MJ['PPU']; WT=MJ['WT']; MT=MJ['MT']
CAP=MJ['CAP']; XH=MJ['XH']
tref=lambda ch: CAP if (ch in CAPS or ch in ASC) else XH
EXP={'A':3,'B':3,'C':1,'D':2,'E':4,'F':3,'G':2,'H':3,'I':3,'J':2,'K':3,'L':2,'M':4,
     'N':3,'O':1,'P':2,'Q':2,'R':3,'S':1,'T':2,'U':1,'V':2,'W':4,'X':2,'Y':3,'Z':3,
     'a':2,'b':2,'c':1,'d':2,'e':2,'f':2,'g':2,'h':2,'i':2,'j':2,'k':3,'l':1,'m':3,
     'n':2,'o':1,'p':2,'q':2,'r':2,'s':1,'t':2,'u':2,'v':2,'w':4,'x':2,'y':2,'z':3}
PAD=90
os.makedirs('work/out', exist_ok=True)

def render(g, paths, sc, pad):
    x0,x1,y0,y1=g['x0'],g['x1'],g['y0'],g['y1']
    W=int((x1-x0)*sc)+2*pad; H=int((y1-y0)*sc)+2*pad
    body=''.join(f'<path d="{d}"/>' for d in paths)
    svg=(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">'
         f'<rect width="{W}" height="{H}" fill="#fff"/>'
         f'<g transform="translate({pad},{pad}) scale({sc}) translate({-x0},{-y0})">'
         f'<g transform="translate(0,{SH[g["sheet"]]}) scale(0.1,-0.1)" fill="#000">{body}</g></g></svg>')
    return np.array(Image.open(io.BytesIO(cairosvg.svg2png(bytestring=svg.encode()))).convert('L'))<128

def morph(m,delta):
    n=int(round(abs(delta)))
    if n==0: return m
    st=ndimage.generate_binary_structure(2,1)
    return ndimage.binary_dilation(m,st,n) if delta>0 else ndimage.binary_erosion(m,st,n)

FONT='/home/claude/bd/fonts/Quicksand-Variable.ttf'
def tmpl(d,f=FONT,sz=110):
    im=Image.new('L',(160,180),255)
    ImageDraw.Draw(im).text((80,90),str(d),font=ImageFont.truetype(f,sz),fill=0,anchor='mm')
    a=np.array(im)<128; ys,xs=np.where(a); a=a[ys.min():ys.max()+1,xs.min():xs.max()+1]
    return np.array(Image.fromarray((a*255).astype(np.uint8)).resize((36,48)))>128
TM={d:tmpl(d) for d in (1,2,3,4)}
def norm36(c):
    ys,xs=np.where(c)
    if len(ys)<15: return None
    c=c[ys.min():ys.max()+1,xs.min():xs.max()+1]
    return np.array(Image.fromarray((c*255).astype(np.uint8)).resize((36,48)))>128
def classify(c):
    c=norm36(c)
    if c is None: return None,0.0
    b=(None,-1)
    for d,t in TM.items():
        i=(c&t).sum()/max((c|t).sum(),1)
        if i>b[1]: b=(d,i)
    return b

res={}; crops={}
for ch in LET:
    g=json.load(open(f'work/letters/{ch}.json'))
    ref=R[ch]['ref']; sc=tref(ch)*PPU/ref
    big=[];small=[]
    for d,b in zip(g['d'],g['boxes']):
        (big if max(b[1]-b[0],b[3]-b[2])>0.20*ref else small).append(d)
    ink = morph(render(g,big,sc,PAD),(WT-MJ['m'][ch]['W'])/2) | \
          morph(render(g,small,sc,PAD),(MT-MJ['m'][ch]['M'])/2)
    lab,n=ndimage.label(~ink); bg=lab[0,0]
    cs=[]
    for i in range(1,n+1):
        if i==bg: continue
        comp=(lab==i); ys,xs=np.where(comp)
        h=ys.max()-ys.min()+1; w=xs.max()-xs.min()+1
        if not (3.0*PPU<=h<=12.0*PPU): continue
        if not (0.72<=w/h<=1.40): continue
        f=len(ys)/(w*h)
        if not (0.42<=f<=0.95): continue
        disc=ndimage.binary_fill_holes(comp)
        digit=disc & ~comp
        d,iou=classify(digit)
        cs.append(dict(cx=float((xs.min()+xs.max())/2), cy=float((ys.min()+ys.max())/2),
                       r=float(h/2), d=d, iou=round(float(iou),2), digit=digit))
    # drop concentric outer duplicates
    keep=[]
    for i,a in enumerate(cs):
        if any(j!=i and ((a['cx']-b['cx'])**2+(a['cy']-b['cy'])**2)**.5 < a['r'] and b['r']<a['r'] for j,b in enumerate(cs)):
            continue
        keep.append(a)
    cs=keep
    crops[ch]=[c.pop('digit') for c in cs]
    res[ch]=dict(sc=sc, circles=cs, exp=EXP[ch], shape=list(ink.shape))
    np.save(f'work/out/{ch}.npy', ink)
    flag='' if len(cs)==EXP[ch] else '   <-- CHECK'
    print('%-2s exp=%d found=%d  %s%s'%(ch,EXP[ch],len(cs),
        ' '.join('%s(%.2f)'%(c['d'],c['iou']) for c in cs),flag))
json.dump(res, open('work/detect.json','w'), indent=1)
np.save('work/crops.npy', np.array(list(crops.items()),dtype=object), allow_pickle=True)
# montage of digit crops
cells=[]
for ch in LET:
    for k,c in enumerate(crops[ch]):
        z=norm36(c)
        if z is None: z=np.zeros((48,36),bool)
        cells.append((ch,k,z))
cols=12; rows=(len(cells)+cols-1)//cols
CW,CHh=60,80
im=Image.new('L',(cols*CW,rows*CHh),255); dr=ImageDraw.Draw(im)
f=ImageFont.truetype(FONT,13)
for idx,(ch,k,z) in enumerate(cells):
    r,c=divmod(idx,cols)
    im.paste(Image.fromarray((~z*255).astype(np.uint8)),(c*CW+12,r*CHh+22))
    dr.text((c*CW+4,r*CHh+4),'%s%d'%(ch,k+1),font=f,fill=0)
im.save('work/digits_montage.png')
print('cells',len(cells))
