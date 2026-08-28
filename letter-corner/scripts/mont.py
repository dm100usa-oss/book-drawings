import json, numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage
LET='AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz'
det=json.load(open('work/detect.json'))
F=ImageFont.truetype('/home/claude/bd/fonts/Quicksand-Variable.ttf',26)
cells=[]
for ch in LET:
    ink=np.load(f'work/out/{ch}.npy')
    lab,n=ndimage.label(~ink); bg=lab[0,0]
    for k,c in enumerate(det[ch]['circles']):
        y,x=int(round(c['cy'])),int(round(c['cx'])); r=int(round(c['r']))
        crop=ink[max(0,y-r-4):y+r+5, max(0,x-r-4):x+r+5]
        im=Image.fromarray((~crop*255).astype(np.uint8)).resize((100,100), Image.LANCZOS)
        cells.append(('%s%d'%(ch,k+1), im))
COLS=10; CW,CHh=110,140
for part in range(2):
    sub=cells[part*60:(part+1)*60]
    if not sub: continue
    rows=(len(sub)+COLS-1)//COLS
    out=Image.new('L',(COLS*CW,rows*CHh),255); dr=ImageDraw.Draw(out)
    for i,(lbl,im) in enumerate(sub):
        r,c=divmod(i,COLS)
        out.paste(im,(c*CW+5,r*CHh+34))
        dr.text((c*CW+5,r*CHh+3),lbl,font=F,fill=0)
    out.save(f'work/mont{part+1}.png')
    print('mont%d'%(part+1), len(sub))
