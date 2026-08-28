import json, sys, cairosvg
V=json.load(open('work/vec2/letters.json')); PPU=V['A']['PPU']
CIRC_R=3.7; RING=0.8; DIG=5.6; LW=1.33
def lg(ch,dx,dy):
    L=V[ch]; b=''.join(f'<path d="{d}"/>' for d in L['paths'])
    s=(f'<g transform="translate({dx},{dy})"><g transform="scale({1/L["PPU"]}) '
       f'translate({-L["left_px"]},{-L["base_px"]}) translate(0,{L["ph"]}) scale(0.1,-0.1)" fill="#000">{b}</g>')
    for e in L.get('extra',[]):
        if e.get('kind')=='ring':
            s+=f'<circle cx="{e["x"]:.2f}" cy="{e["y"]:.2f}" r="{e["r"]-LW/2:.2f}" fill="none" stroke="#000" stroke-width="{LW}"/>'
        else:
            s+=(f'<g transform="translate({e["x"]:.2f},{e["y"]:.2f}) rotate({e["a"]})">'
                f'<path d="M 0 0 L {-e["s"]*1.15:.2f} {e["s"]*0.6:.2f} L {-e["s"]*1.15:.2f} {-e["s"]*0.6:.2f} Z" fill="#000"/></g>')
    for c in L['circles']:
        s+=(f'<circle cx="{c["x"]:.2f}" cy="{c["y"]:.2f}" r="{CIRC_R-RING/2:.2f}" fill="#fff" stroke="#000" stroke-width="{RING}"/>'
            f'<text x="{c["x"]:.2f}" y="{c["y"]+DIG*0.35:.2f}" text-anchor="middle" font-family="Quicksand" '
            f'font-weight="700" font-size="{DIG}" fill="#000">{c["n"]}</text>')
    return s+'</g>'
group=sys.argv[1].split(',')
GAP=10; COLGAP=26; M=20
xs=[]; x=M
for ch in group:
    xs.append(x); x+=V[ch]['w']+COLGAP
W=x+M; H=200
P=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" fill="#fff"/>']
yb=140
for yy,st in ((yb-100,'stroke="#ccc" stroke-width="0.6"'),(yb-50,'stroke="#ccc" stroke-width="0.6" stroke-dasharray="3,3"'),(yb,'stroke="#ccc" stroke-width="0.9"')):
    P.append(f'<line x1="{M-8}" y1="{yy}" x2="{W-M+8}" y2="{yy}" {st}/>')
for ch,x0 in zip(group,xs): P.append(lg(ch,x0,yb))
P.append('</svg>')
cairosvg.svg2png(bytestring='\n'.join(P).encode(), write_to='work/scan.png', output_width=1500)
print('ok')
