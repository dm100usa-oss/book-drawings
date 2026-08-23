import math
from PIL import ImageFont

W, H = 612.0, 792.0
CX = W / 2
M = 36.0
L, R = M, W - M
CW = R - L

lion_group = open('lion_group.svg').read()
LION_W, LION_H = 1976.0, 2060.0

SENT = ['I', 'see', 'a', 'big', 'lion.']
CARDS = ['see', 'lion.', 'big', 'I', 'a']

FS = 59.0
FS_TAG = 15.0
_f = ImageFont.truetype('fonts/SchoolPrint-Regular.ttf', int(FS))
_ft = ImageFont.truetype('fonts/SchoolPrint-Regular.ttf', int(FS_TAG))
ASC_R, XH_R = 0.765, 0.412
CAP_R, STEM_R = 0.715, 0.060

IW = 0.40 * CAP_R * FS * 1.6          # ширина слота под букву I

# начертания: (имя, доля х-высоты, доля толщины, доля левого выноса o)
FACE = {
    'r': ('School Print', 0.412, 0.060, 0.050),
    'b': ('School Print Bold', 0.438, 0.105, 0.043),
}


def draw_e(x, base, size, face):
    """буква e с горизонтальной перекладиной, как учат писать"""
    import math as _m
    fam, xhr, stf, lsbf = FACE[face]
    xh = xhr * size
    st = stf * size
    f = ImageFont.truetype('fonts/%s.ttf'
                           % ('SchoolPrint-Regular' if face == 'r'
                              else 'SchoolPrintBold-Regular'), 1000)
    adv = f.getlength('e') / 1000 * size
    r = (xh - st) / 2
    cx, cy = x + adv / 2, base - xh / 2

    def P(a):
        t = _m.radians(a)
        return cx + r * _m.cos(t), cy - r * _m.sin(t)
    p0, p1, p2 = P(0), P(150), P(300)
    A(f'<path d="M {p0[0]:.2f} {p0[1]:.2f} '
      f'A {r:.2f} {r:.2f} 0 0 0 {p1[0]:.2f} {p1[1]:.2f} '
      f'A {r:.2f} {r:.2f} 0 0 0 {p2[0]:.2f} {p2[1]:.2f}" fill="none" '
      f'stroke="#000" stroke-width="{st:.2f}" stroke-linecap="round"/>')
    A(f'<path d="M {cx-r:.2f} {cy:.2f} L {cx+r:.2f} {cy:.2f}" fill="none" '
      f'stroke="#000" stroke-width="{st:.2f}" stroke-linecap="round"/>')
    return adv


def draw_I(x, base, size, face):
    fam, xhr, stf, lsbf = FACE[face]
    st = stf * size
    cp = CAP_R * size
    bw = 0.40 * cp
    w = bw * 1.6
    x0 = x + (w - bw) / 2
    A(f'<rect x="{x+(w-st)/2:.2f}" y="{base-cp:.2f}" width="{st:.2f}" '
      f'height="{cp:.2f}" fill="#000"/>')
    A(f'<rect x="{x0:.2f}" y="{base-cp:.2f}" width="{bw:.2f}" '
      f'height="{st:.2f}" fill="#000"/>')
    A(f'<rect x="{x0:.2f}" y="{base-st:.2f}" width="{bw:.2f}" '
      f'height="{st:.2f}" fill="#000"/>')
    return w


def text_w(txt, size, face):
    fam = FACE[face][0]
    fp = 'fonts/%s.ttf' % ('SchoolPrint-Regular' if face == 'r'
                           else 'SchoolPrintBold-Regular')
    f = ImageFont.truetype(fp, 1000)
    tot = 0.0
    for ch in txt:
        if ch == 'I':
            tot += 0.40 * CAP_R * size * 1.6
        else:
            tot += f.getlength(ch) / 1000 * size
    return tot


def draw_text(txt, x, base, size, face='r'):
    """рисует текст по буквам, подменяя e и I на правильные формы"""
    fam = FACE[face][0]
    fp = 'fonts/%s.ttf' % ('SchoolPrint-Regular' if face == 'r'
                           else 'SchoolPrintBold-Regular')
    f = ImageFont.truetype(fp, 1000)
    for ch in txt:
        if ch == 'e':
            x += draw_e(x, base, size, face)
        elif ch == 'I':
            x += draw_I(x, base, size, face)
        else:
            if ch != ' ':
                A(f'<text x="{x:.2f}" y="{base:.2f}" font-family="{fam}" '
                  f'font-size="{size}" fill="#000">{ch}</text>')
            x += f.getlength(ch) / 1000 * size
    return x


def put_word(w, x, base, centered_w=None):
    if centered_w is not None:
        x = x + (centered_w - wid[w]) / 2
    draw_text(w, x, base, FS, 'r')


P = []
A = P.append
wid = {w: text_w(w, FS, 'r') for w in SENT}
A(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}pt" height="{H}pt" '
  f'viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" fill="#fff"/>')

LETTERS = {
    'L': {'w': 0.56, 'apos': [0.86, 1.0],
          'strokes': [('line', 0, 0, 0, 1), ('line', 0, 1, 1, 1)]},
    'l': {'w': 0.20, 'apos': [0.90],
          'strokes': [('line', 0.5, 0, 0.5, 1)]},
}


def paths_of(c, x, y, h):
    inf = LETTERS[c]
    w = inf['w'] * h
    return ['M {:.2f} {:.2f} L {:.2f} {:.2f}'.format(
        x + a * w, y + b * h, x + cc * w, y + d * h)
        for _, a, b, cc, d in inf['strokes']], w


def marks_of(c, x, y, h):
    inf = LETTERS[c]
    w = inf['w'] * h
    out = []
    for k, (_, a, b, cc, d) in enumerate(inf['strokes']):
        x1, y1 = x + a * w, y + b * h
        x2, y2 = x + cc * w, y + d * h
        f = inf['apos'][k]
        out.append((x1, y1, x1 + (x2 - x1) * f, y1 + (y2 - y1) * f,
                    math.degrees(math.atan2(y2 - y1, x2 - x1))))
    return out


def arrow(x, y, ang, s):
    return (f'<path d="M 0 0 L {-s} {s*0.52} L {-s} {-s*0.52} Z" fill="#000" '
            f'transform="translate({x:.2f},{y:.2f}) rotate({ang:.2f})"/>')


def draw_letter(c, x, y, h, tt):
    ps, lw = paths_of(c, x, y, h)
    for p in ps:
        A(f'<path d="{p}" fill="none" stroke="#000" stroke-width="{tt}" '
          f'stroke-linecap="round" stroke-linejoin="round"/>')
    for p in ps:
        A(f'<path d="{p}" fill="none" stroke="#fff" stroke-width="{tt-3.2}" '
          f'stroke-linecap="round" stroke-linejoin="round"/>')
    for p in ps:
        A(f'<path d="{p}" fill="none" stroke="#000" stroke-width="1.1" '
          f'stroke-dasharray="3.5,3.5"/>')
    for n, (px, py, ex, ey, ang) in enumerate(marks_of(c, x, y, h), 1):
        A(arrow(ex, ey, ang, 5.2))
        A(f'<circle cx="{px:.2f}" cy="{py:.2f}" r="5.0" fill="#000" '
          f'stroke="#fff" stroke-width="1"/>')
        A(f'<text x="{px:.2f}" y="{py+2.3:.2f}" text-anchor="middle" '
          f'font-family="Quicksand" font-weight="700" font-size="6.8" '
          f'fill="#fff">{n}</text>')
    return lw


def tagw(txt):
    return _ft.getlength(txt) + 20


def tag(x, ybase, txt):
    """подпись зоны в рамке-ярлыке"""
    tw = _ft.getlength(txt) + 20
    th = 22.0
    A(f'<rect x="{x:.2f}" y="{ybase-th+5:.2f}" width="{tw:.2f}" '
      f'height="{th}" rx="{th/2}" fill="#fff" stroke="#000" '
      f'stroke-width="1.2"/>')
    A(f'<text x="{x+tw/2:.2f}" y="{ybase:.2f}" text-anchor="middle" '
      f'font-family="School Print" font-size="{FS_TAG}" fill="#000">{txt}</text>')


# ---------------- шапка ----------------
BW, BH = 206.0, 134.0
BX, BY = R - BW, 30.0
A(f'<rect x="{BX}" y="{BY}" width="{BW}" height="{BH}" rx="12" fill="#fff" '
  f'stroke="#000" stroke-width="2"/>')
FL = 124.0                      # кегль буквы в уголке
STEM = 0.140 * FL
CAPH = 0.735 * FL
ASCH = 0.787 * FL
WL = 0.492 * FL
BEAR_L, BEAR_l = 0.095 * FL, 0.072 * FL
GAPL = 36.0
grp = WL + GAPL + STEM
gx = BX + (BW - grp) / 2
gbase = BY + BH / 2 + ASCH / 2 - 4


def hollow(txt, x, ybase):
    A(f'<text x="{x:.2f}" y="{ybase:.2f}" font-family="School Print Heavy" '
      f'font-size="{FL}" fill="#fff" stroke="#000" stroke-width="2.4" '
      f'stroke-linejoin="round" stroke-linecap="round" '
      f'paint-order="stroke fill">{txt}</text>')


def dash(p):
    A(f'<path d="{p}" fill="none" stroke="#000" stroke-width="1.5" '
      f'stroke-dasharray="4.5,4.5"/>')


def dot(x, y, n):
    A(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="6.6" fill="#000" '
      f'stroke="#fff" stroke-width="1.1"/>')
    A(f'<text x="{x:.2f}" y="{y+3.0:.2f}" text-anchor="middle" '
      f'font-family="Quicksand" font-weight="700" font-size="9" '
      f'fill="#fff">{n}</text>')


# заглавная L
lx = gx - BEAR_L
hollow('L', lx, gbase)
ax = gx + STEM / 2
ay1, ay2 = gbase - CAPH, gbase - STEM / 2
dash(f'M {ax:.2f} {ay1:.2f} L {ax:.2f} {ay2:.2f}')
dash(f'M {ax:.2f} {ay2:.2f} L {gx+WL-STEM/2:.2f} {ay2:.2f}')
A(arrow(ax, ay2 - 9, 90, 6.6))
A(arrow(gx + WL - STEM / 2, ay2, 0, 6.6))
dot(ax, ay1 + 8, 1)
dot(ax, ay2, 2)

# строчная l
gx2 = gx + WL + GAPL
hollow('l', gx2 - BEAR_l, gbase)
bx2 = gx2 + STEM / 2
dash(f'M {bx2:.2f} {gbase-ASCH:.2f} L {bx2:.2f} {gbase-2:.2f}')
A(arrow(bx2, gbase - 10, 90, 6.6))
dot(bx2, gbase - ASCH + 8, 1)

A(f'<text x="{L+2}" y="54" font-family="Quicksand" font-weight="700" '
  f'font-size="11" fill="#000">Name</text>')
A(f'<line x1="{L+44}" y1="56" x2="{L+280}" y2="56" stroke="#000" '
  f'stroke-width="1.4"/>')

A(f'<text x="{L}" y="104" font-family="Baloo 2" font-weight="800" '
  f'font-size="27" fill="#9a9a9a">Build a Sentence</text>')
draw_text('What do you see?', L + 2, 156, 34, 'b')


ASC_R, XH_R = 0.765, 0.412     # доли кегля: верх высоких букв и круглых
CAP_R, STEM_R = 0.715, 0.060


def rule(top, base, mid=None):
    mid = (top + base) / 2
    A(f'<line x1="{L}" y1="{top}" x2="{R}" y2="{top}" stroke="#000" '
      f'stroke-width="0.9"/>')
    A(f'<line x1="{L}" y1="{mid}" x2="{R}" y2="{mid}" stroke="#000" '
      f'stroke-width="0.9" stroke-dasharray="5,6"/>')
    A(f'<line x1="{L}" y1="{base}" x2="{R}" y2="{base}" stroke="#000" '
      f'stroke-width="2.4" stroke-linecap="round"/>')


# ---------------- главный блок: рисунок ----------------
pn_y, pn_h = 178.0, 216.0
A(f'<rect x="{L}" y="{pn_y}" width="{CW}" height="{pn_h}" rx="9" '
  f'fill="none" stroke="#000" stroke-width="1.8"/>')
ground = pn_y + pn_h - 32
A(f'<line x1="{L+28}" y1="{ground}" x2="{R-28}" y2="{ground}" stroke="#000" '
  f'stroke-width="1" stroke-dasharray="3,5"/>')
lh = 172.0
lw = LION_W / LION_H * lh
A(f'<g transform="translate({CX-lw/2:.2f},{ground-lh:.2f}) '
  f'scale({lh/LION_H:.6f})">{lion_group}</g>')

# ---------------- читай ----------------
SB = 452.0
ROWH = 2 * XH_R * FS
r1_top, r1_base = SB - ROWH, SB
rule(r1_top, r1_base)
x = L + 16
for w in SENT:
    put_word(w, x, r1_base)
    x += wid[w] + 16

# ---------------- клей ----------------
BOX_H, CARD_H = 82.0, 70.0
box_y = 468.0
card_w = {w: max(wid[w] + 22, 58.0) for w in SENT}
box_w = {w: card_w[w] + 10 for w in SENT}
gap = 6.0
x = L + 6
for w in SENT:
    A(f'<rect x="{x:.2f}" y="{box_y}" width="{box_w[w]:.2f}" '
      f'height="{BOX_H}" rx="7" fill="none" stroke="#000" '
      f'stroke-width="1.7"/>')
    x += box_w[w] + gap

# ---------------- пиши ----------------
rule(564.0, 616.0)

# ---------------- разрез и карточки ----------------
cut_y = 640.0
A(f'<g transform="translate({L+5},{cut_y})" fill="none" stroke="#000" '
  f'stroke-width="1.5"><circle cx="0" cy="-4.6" r="3.3"/>'
  f'<circle cx="0" cy="4.6" r="3.3"/>'
  f'<line x1="2.6" y1="-3.2" x2="15" y2="5.5"/>'
  f'<line x1="2.6" y1="3.2" x2="15" y2="-5.5"/></g>')
A(f'<line x1="{L+25}" y1="{cut_y}" x2="{R}" y2="{cut_y}" stroke="#000" '
  f'stroke-width="1.2" stroke-dasharray="7,6"/>')

cy0 = 648.0
tot = sum(card_w[w] for w in CARDS)
x0 = CX - tot / 2
D = 'stroke="#000" stroke-width="1.2" stroke-dasharray="7,6" fill="none"'
A(f'<rect x="{x0:.2f}" y="{cy0}" width="{tot:.2f}" height="{CARD_H}" {D}/>')
x = x0
for i, w in enumerate(CARDS):
    if i:
        A(f'<line x1="{x:.2f}" y1="{cy0}" x2="{x:.2f}" y2="{cy0+CARD_H}" {D}/>')
    put_word(w, x, cy0 + CARD_H / 2 + XH_R * FS / 2 + 2, card_w[w])
    x += card_w[w]

A(f'<text x="{CX}" y="750" text-anchor="middle" font-family="Quicksand" '
  f'font-weight="600" font-size="7.5" fill="#000">'
  f'Magic of Discoveries  |  For single classroom use only.</text>')
A('</svg>')
open('sentence2.svg', 'w').write('\n'.join(P))
print('готово')
