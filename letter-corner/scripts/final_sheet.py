import json, cairosvg
V=json.load(open('work/vec2/letters.json')); PPU=V['A']['PPU']
CIRC_R=3.7; RING=0.8; DIG=5.6; LW=1.33
LET='ABCDEFGHIJKLMNOPQRSTUVWXYZ'

def lg(ch,dx,dy,s):
    L=V[ch]; body=''.join(f'<path d="{d}"/>' for d in L['paths'])
    g=(f'<g transform="translate({dx:.3f},{dy:.3f}) scale({s:.5f})">'
       f'<g transform="scale({1/L["PPU"]}) translate({-L["left_px"]:.3f},{-L["base_px"]:.3f}) '
       f'translate(0,{L["ph"]}) scale(0.1,-0.1)" fill="#000">{body}</g>')
    for e in L.get('extra',[]):
        if e.get('kind')=='ring':
            g+=(f'<circle cx="{e["x"]:.3f}" cy="{e["y"]:.3f}" r="{e["r"]-LW/2:.3f}" '
                f'fill="none" stroke="#000" stroke-width="{LW}"/>')
        else:
            g+=(f'<g transform="translate({e["x"]:.3f},{e["y"]:.3f}) rotate({e["a"]})">'
                f'<path d="M 0 0 L {-e["s"]*1.15:.2f} {e["s"]*0.6:.2f} L {-e["s"]*1.15:.2f} {-e["s"]*0.6:.2f} Z" fill="#000"/></g>')
    for c in L['circles']:
        g+=(f'<circle cx="{c["x"]:.3f}" cy="{c["y"]:.3f}" r="{CIRC_R-RING/2:.3f}" fill="#fff" '
            f'stroke="#000" stroke-width="{RING}"/>'
            f'<text x="{c["x"]:.3f}" y="{c["y"]+DIG*0.35:.3f}" text-anchor="middle" '
            f'font-family="Quicksand" font-weight="700" font-size="{DIG}" fill="#000">{c["n"]}</text>')
    return g+'</g>'

W,H=612.0,792.0; M=30.0
COLS,ROWS=4,7
colw=(W-2*M)/COLS; rowh=(H-2*M-14)/ROWS
GAP=9.0
pw=max(V[c]['w']+GAP+V[c.lower()]['w'] for c in LET)
S=min((colw-14)/pw, (rowh-30)/128.0)
P=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}pt" height="{H}pt" viewBox="0 0 {W} {H}">'
   f'<rect width="{W}" height="{H}" fill="#fff"/>']
for i,u in enumerate(LET):
    l=u.lower(); r,c=divmod(i,COLS)
    x0=M+c*colw+7; yb=M+14+r*rowh+rowh-24
    x1=x0+(V[u]['w']+GAP+V[l]['w'])*S
    for yy,st in ((yb-100*S,'stroke="#bfbfbf" stroke-width="0.5"'),
                  (yb-50*S,'stroke="#bfbfbf" stroke-width="0.5" stroke-dasharray="2.5,2.5"'),
                  (yb,'stroke="#bfbfbf" stroke-width="0.8"')):
        P.append(f'<line x1="{x0-6:.2f}" y1="{yy:.2f}" x2="{x1+6:.2f}" y2="{yy:.2f}" {st}/>')
    P.append(lg(u,x0,yb,S))
    P.append(lg(l,x0+(V[u]['w']+GAP)*S,yb,S))
P.append('</svg>')
svg='\n'.join(P)
open('work/alphabet-26-pairs.svg','w').write(svg)
cairosvg.svg2pdf(bytestring=svg.encode(), write_to='/mnt/user-data/outputs/alphabet-26-pairs.pdf')
cairosvg.svg2png(bytestring=svg.encode(), write_to='work/final.png', output_width=1600)
print('scale=%.3f  cap height=%.1f pt'%(S,100*S))
