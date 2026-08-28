import json, sys, cairosvg
V=json.load(open('work/vec2/letters.json')); PPU=V['A']['PPU']
CIRC_R=3.7; RING=0.8; DIG=5.6
def lg(ch,dx,dy):
    L=V[ch]; body=''.join(f'<path d="{d}"/>' for d in L['paths'])
    s=(f'<g transform="translate({dx:.3f},{dy:.3f})"><g transform="scale({1/L["PPU"]}) '
       f'translate({-L["left_px"]:.3f},{-L["base_px"]:.3f}) translate(0,{L["ph"]}) scale(0.1,-0.1)" fill="#000">{body}</g>')
    for c in L['circles']:
        s+=(f'<circle cx="{c["x"]:.3f}" cy="{c["y"]:.3f}" r="{CIRC_R-RING/2:.3f}" fill="#fff" stroke="#000" stroke-width="{RING}"/>'
            f'<text x="{c["x"]:.3f}" y="{c["y"]+DIG*0.35:.3f}" text-anchor="middle" font-family="Quicksand" '
            f'font-weight="700" font-size="{DIG}" fill="#000">{c["n"]}</text>')
    for e in L.get('extra',[]):
        if e.get('kind')=='ring':
            LW=1.33
            s+=(f'<circle cx="{e["x"]:.3f}" cy="{e["y"]:.3f}" r="{e["r"]-LW/2:.3f}" '
                f'fill="none" stroke="#000" stroke-width="{LW}"/>')
            continue
        s+=(f'<g transform="translate({e["x"]:.3f},{e["y"]:.3f}) rotate({e["a"]})">'
            f'<path d="M 0 0 L {-e["s"]*1.15:.2f} {e["s"]*0.6:.2f} L {-e["s"]*1.15:.2f} {-e["s"]*0.6:.2f} Z" fill="#000"/></g>')
    return s+'</g>'
pairs=sys.argv[1].split(',')
GAP=10; COLGAP=30; ROWH=190; COLS=3; M=25
colw=max(V[p[0]]['w']+GAP+V[p[1]]['w'] for p in pairs)+COLGAP
rows=(len(pairs)+COLS-1)//COLS
W=M*2+colw*COLS; H=M*2+ROWH*rows
P=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" fill="#fff"/>']
for i,p in enumerate(pairs):
    r,c=divmod(i,COLS); x0=M+c*colw; yb=M+r*ROWH+130
    for yy,st in ((yb-100,'stroke="#bbb" stroke-width="0.7"'),(yb-50,'stroke="#bbb" stroke-width="0.7" stroke-dasharray="3,3"'),(yb,'stroke="#bbb" stroke-width="1"')):
        P.append(f'<line x1="{x0-10}" y1="{yy}" x2="{x0+colw-COLGAP+10}" y2="{yy}" {st}/>')
    P.append(lg(p[0],x0,yb)); P.append(lg(p[1],x0+V[p[0]]['w']+GAP,yb))
P.append('</svg>')
open('work/zoom.svg','w').write('\n'.join(P))
cairosvg.svg2svg
cairosvg.svg2png(bytestring='\n'.join(P).encode(), write_to='work/zoom.png', output_width=1500)
print('ok')
