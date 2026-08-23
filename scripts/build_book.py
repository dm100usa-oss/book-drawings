import os
import re
import math
import random
import subprocess
from PIL import Image, ImageFont
import numpy as np
import letters as LT

TOD = 'repos/toddler-coloring-book/public/drawings'
MAG = 'repos/magic-of-discoveries/public/printables'
CACHE = 'vec'
os.makedirs(CACHE, exist_ok=True)

# ---------- состав книги ----------
BOOK = [
    ('A', [('105', 'avocado', 'an'), ('052', 'axolotl', 'an')]),
    ('B', [('022', 'bear', 'a'), ('036', 'bee', 'a')]),
    ('C', [('030', 'cat', 'a'), ('043', 'crab', 'a')]),
    ('D', [('031', 'dog', 'a'), ('033', 'duck', 'a')]),
    ('E', [('002', 'elephant', 'an'), ('028', 'eagle', 'an')]),
    ('F', [('023', 'fox', 'a'), ('014', 'frog', 'a')]),
    ('G', [('012', 'giraffe', 'a'), ('019', 'goat', 'a')]),
    ('H', [('018', 'hedgehog', 'a'), ('029', 'hamster', 'a')]),
    ('I', [('M:ocean-island', 'island', 'an'), ('099', 'ice cream', '')]),
    ('J', [('045', 'jellyfish', 'a'), ('069', 'jet', 'a')]),
    ('K', [('013', 'koala', 'a'), ('007', 'kangaroo', 'a')]),
    ('L', [('001', 'lion', 'a'), ('109', 'lemon', 'a')]),
    ('M', [('006', 'monkey', 'a'), ('035', 'mouse', 'a')]),
    ('N', [('N:ninja', 'ninja', 'a'), ('N:nurse', 'nurse', 'a')]),
    ('O', [('017', 'owl', 'an'), ('044', 'octopus', 'an')]),
    ('P', [('004', 'parrot', 'a'), ('108', 'pineapple', 'a')]),
    ('Q', [('N:queen', 'queen', 'a'), ('N:quilt', 'quilt', 'a')]),
    ('R', [('008', 'rhino', 'a'), ('021', 'raccoon', 'a')]),
    ('S', [('032', 'squirrel', 'a'), ('040', 'shark', 'a')]),
    ('T', [('046', 'turtle', 'a'), ('097', 'tulip', 'a')]),
    ('U', [('057', 'unicorn', 'a'), ('083', 'umbrella', 'an')]),
    ('V', [('N:volcano', 'volcano', 'a'), ('N:violin', 'violin', 'a')]),
    ('W', [('042', 'whale', 'a'), ('100', 'watermelon', 'a')]),
    ('X', [('N:xylophone', 'xylophone', 'a'), ('N:xmastree', 'Xmas tree', 'a')]),
    ('Y', [('N:yacht', 'yacht', 'a'), ('N:yeti', 'yeti', 'a')]),
    ('Z', [('003', 'zebra', 'a'), ('N:zeppelin', 'zeppelin', 'a')]),
]

BONUS = [
    ('D', 'N:dinosaur', 'dinosaur', 'a'),
    ('P', 'N:pirate', 'pirate', 'a'),
    ('R', 'N:robot', 'robot', 'a'),
]

FRAMES = [('What do you see?', ['I', 'see']),
          ('What is this?', ['This', 'is'])]


# ---------- векторизация рисунка ----------
def vectorize(key):
    out = os.path.join(CACHE, key.replace(':', '_') + '.svg')
    if os.path.exists(out):
        return open(out).read()
    if key.startswith('M:'):
        src = os.path.join(MAG, key[2:] + '.png')
    elif key.startswith('N:'):
        src = os.path.join('newart', key[2:] + '_fix.png')
    else:
        src = os.path.join(TOD, key + '.png')
    im = Image.open(src).convert('L')
    a = np.array(im)
    ys, xs = np.where(a < 200)
    im = im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    k = max(1, int(1800 / max(im.size)))
    im = im.resize((im.width * k, im.height * k), Image.LANCZOS)
    b = (np.array(im) < 150).astype(np.uint8) * 255
    Image.fromarray(255 - b).save('/tmp/t.pbm')
    subprocess.run(['potrace', '-s', '-o', '/tmp/t.svg', '--turdsize', '6',
                    '--alphamax', '1.0', '--opttolerance', '0.2', '/tmp/t.pbm'],
                   check=True)
    s = open('/tmp/t.svg').read()
    vb = re.search(r'viewBox="([\d\. ]+)"', s).group(1).split()
    g = s[s.find('<g '):s.rfind('</g>') + 4]
    res = '<!--%s %s-->%s' % (vb[2], vb[3], g)
    open(out, 'w').write(res)
    return res


def art(key):
    s = vectorize(key)
    m = re.match(r'<!--([\d\.]+) ([\d\.]+)-->', s)
    return float(m.group(1)), float(m.group(2)), s[m.end():]


# ---------- шрифтовые метрики ----------
ASC_R, XH_R, CAP_R, STEM_R = 0.765, 0.412, 0.715, 0.060
FREG = 'fonts/SchoolPrint-Regular.ttf'
FBOLD = 'fonts/SchoolPrintBold-Regular.ttf'
FHEAVY = 'fonts/SchoolPrintHeavy-Regular.ttf'
_r = ImageFont.truetype(FREG, 1000)
_b = ImageFont.truetype(FBOLD, 1000)


def adv(ch, size, bold=False):
    if ch == 'I':
        return 0.40 * CAP_R * size * 1.6
    f = _b if bold else _r
    return f.getlength(ch) / 1000 * size


def tw(txt, size, bold=False):
    return sum(adv(c, size, bold) for c in txt)


# ---------- страница ----------
W, H = 612.0, 792.0
CX = W / 2
M = 36.0
L, R = M, W - M
CW = R - L


def arrow_head(x, y, ang, sz):
    return (f'<path d="M 0 0 L {-sz} {sz*0.52} L {-sz} {-sz*0.52} Z" '
            f'fill="#000" transform="translate({x:.2f},{y:.2f}) '
            f'rotate({ang:.2f})"/>')


def _measure_glyphs():
    from PIL import ImageDraw as _ID
    fh = ImageFont.truetype(FHEAVY, 400)
    asc = fh.getmetrics()[0]
    out = {}
    for ch in ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'
               'abcdefghijklmnopqrstuvwxyz'):
        im = Image.new('L', (900, 1000), 255)
        _ID.Draw(im).text((200, 300), ch, font=fh, fill=0)
        a = np.array(im) < 128
        ys, xs = np.where(a)
        out[ch] = {'lsb': (xs.min() - 200) / 400,
                   'w': (xs.max() - xs.min() + 1) / 400,
                   'adv': fh.getlength(ch) / 400}
    return out


GLYPH = _measure_glyphs()


def _measure_pairs():
    from PIL import ImageDraw as _ID
    fh = ImageFont.truetype(FHEAVY, 400)
    asc = fh.getmetrics()[0]
    out = {}
    for ch in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        pr = ch + ch.lower()
        im = Image.new('L', (1600, 1400), 255)
        _ID.Draw(im).text((200, 300), pr, font=fh, fill=0)
        a = np.array(im) < 128
        ys, xs = np.where(a)
        out[pr] = ((300 + asc - ys.min()) / 400,
                   (ys.max() - (300 + asc)) / 400,
                   (xs.max() - xs.min() + 1) / 400,
                   (xs.min() - 200) / 400)
    return out


PAIR = _measure_pairs()
MAXTOP = max(v[0] for v in PAIR.values())
MAXBOT = max(v[1] for v in PAIR.values())
MAXW = max(v[2] for v in PAIR.values())
PAD_T = 14.0
FL_GLOBAL = min((134.0 - 2 * PAD_T) / (MAXTOP + MAXBOT),
                (206.0 - 34.0) / MAXW)


def page(letter, key, word, article, frame_i, seed):
    q, verb = FRAMES[frame_i]
    words = [verb[0], verb[1]] + ([article] if article else []) + [word + '.']

    P = []
    A = P.append
    A(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}pt" height="{H}pt" '
      f'viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" fill="#fff"/>')

    # подбор кегля, чтобы клетки поместились по ширине
    FS = 59.0
    while FS > 34:
        cw = [max(tw(x, FS) + 22, 58.0) for x in words]
        tot = sum(c + 10 for c in cw) + 6 * (len(words) - 1)
        if tot <= CW - 12 and tw(' '.join(words), FS) <= CW - 40:
            break
        FS -= 1
    card_w = [max(tw(x, FS) + 22, 58.0) for x in words]
    box_w = [c + 10 for c in card_w]

    def put(txt, x, base, size, bold=False):
        f = _b if bold else _r
        fam = 'School Print Bold' if bold else 'School Print'
        st = (0.105 if bold else STEM_R) * size
        xh = (0.438 if bold else XH_R) * size
        for ch in txt:
            if ch == 'e':
                a_ = f.getlength('e') / 1000 * size
                r = (xh - st) / 2
                cx, cy = x + a_ / 2, base - xh / 2

                def PT(ang):
                    t = math.radians(ang)
                    return cx + r * math.cos(t), cy - r * math.sin(t)
                p0, p1, p2 = PT(0), PT(150), PT(300)
                A(f'<path d="M {p0[0]:.2f} {p0[1]:.2f} '
                  f'A {r:.2f} {r:.2f} 0 0 0 {p1[0]:.2f} {p1[1]:.2f} '
                  f'A {r:.2f} {r:.2f} 0 0 0 {p2[0]:.2f} {p2[1]:.2f}" '
                  f'fill="none" stroke="#000" stroke-width="{st:.2f}" '
                  f'stroke-linecap="round"/>')
                A(f'<path d="M {cx-r:.2f} {cy:.2f} L {cx+r:.2f} {cy:.2f}" '
                  f'fill="none" stroke="#000" stroke-width="{st:.2f}" '
                  f'stroke-linecap="round"/>')
                x += a_
            elif ch == 'I':
                cp = CAP_R * size
                bw = 0.40 * cp
                sl = bw * 1.6
                x0 = x + (sl - bw) / 2
                A(f'<rect x="{x+(sl-st)/2:.2f}" y="{base-cp:.2f}" '
                  f'width="{st:.2f}" height="{cp:.2f}" fill="#000"/>')
                A(f'<rect x="{x0:.2f}" y="{base-cp:.2f}" width="{bw:.2f}" '
                  f'height="{st:.2f}" fill="#000"/>')
                A(f'<rect x="{x0:.2f}" y="{base-st:.2f}" width="{bw:.2f}" '
                  f'height="{st:.2f}" fill="#000"/>')
                x += sl
            else:
                if ch != ' ':
                    A(f'<text x="{x:.2f}" y="{base:.2f}" font-family="{fam}" '
                      f'font-size="{size}" fill="#000">{ch}</text>')
                x += f.getlength(ch) / 1000 * size
        return x

    # ---- шапка ----
    BW, BH, BY = 206.0, 134.0, 30.0
    BX = R - BW
    A(f'<rect x="{BX}" y="{BY}" width="{BW}" height="{BH}" rx="12" '
      f'fill="#fff" stroke="#000" stroke-width="2"/>')
    pair = letter + letter.lower()
    ptop, pbot, pw, plsb = PAIR[pair]
    FL = FL_GLOBAL
    gb = BY + PAD_T + MAXTOP * FL
    WALL = 3.2
    ST = 0.14 * FL
    CAPH = 0.735 * FL
    XHH = 0.458 * FL

    def hol(paths, tt):
        for p in paths:
            A(f'<path d="{p}" fill="none" stroke="#000" stroke-width="{tt:.2f}" '
              f'stroke-linecap="round" stroke-linejoin="round"/>')
        for p in paths:
            A(f'<path d="{p}" fill="none" stroke="#fff" '
              f'stroke-width="{tt-2*WALL:.2f}" stroke-linecap="round" '
              f'stroke-linejoin="round"/>')

    def big_I(x, base):
        bw = 0.49 * FL
        y1, y2 = base - CAPH + ST / 2, base - ST / 2
        hol([f'M {x+bw/2:.2f} {y1:.2f} L {x+bw/2:.2f} {y2:.2f}',
             f'M {x+ST/2:.2f} {y1:.2f} L {x+bw-ST/2:.2f} {y1:.2f}',
             f'M {x+ST/2:.2f} {y2:.2f} L {x+bw-ST/2:.2f} {y2:.2f}'], ST)
        return bw

    def small_i(x, base):
        hol([f'M {x+ST/2:.2f} {base-XHH+ST/2:.2f} '
             f'L {x+ST/2:.2f} {base-ST/2:.2f}'], ST)
        cy = base - XHH - ST * 1.15
        A(f'<circle cx="{x+ST/2:.2f}" cy="{cy:.2f}" r="{ST/2:.2f}" '
          f'fill="#fff" stroke="#000" stroke-width="{WALL}"/>')
        return ST

    def small_e(x, base):
        r = (XHH - ST) / 2
        cx, cy = x + XHH / 2, base - XHH / 2

        def PT(ang):
            t = math.radians(ang)
            return cx + r * math.cos(t), cy - r * math.sin(t)
        p0, p1, p2 = PT(0), PT(150), PT(300)
        hol([f'M {p0[0]:.2f} {p0[1]:.2f} '
             f'A {r:.2f} {r:.2f} 0 0 0 {p1[0]:.2f} {p1[1]:.2f} '
             f'A {r:.2f} {r:.2f} 0 0 0 {p2[0]:.2f} {p2[1]:.2f}',
             f'M {cx-r:.2f} {cy:.2f} L {cx+r:.2f} {cy:.2f}'], ST)
        return XHH

    def font_glyph(ch, x, base):
        fh = ImageFont.truetype(FHEAVY, 1000)
        A(f'<text x="{x:.2f}" y="{base:.2f}" font-family="School Print Heavy" '
          f'font-size="{FL:.1f}" fill="#fff" stroke="#000" '
          f'stroke-width="3.2" stroke-linejoin="round" '
          f'stroke-linecap="round">{ch}</text>')
        return fh.getlength(ch) / 1000 * FL

    # --- геометрия пары букв ---
    fh = ImageFont.truetype(FHEAVY, 1000)
    CAPT = 0.735 * FL
    XHT = 0.458 * FL
    ASCT = 0.788 * FL
    DESC = 0.218 * FL
    up, lo = letter, letter.lower()
    ASCENDERS = set('bdfhklt')
    DESCENDERS = set('gjpqy')

    def inkbox(ch):
        m = GLYPH[ch]
        return m['lsb'] * FL, m['w'] * FL, m['adv'] * FL

    lsbU, wU, advU = inkbox(up)
    lsbL, wL, advL = inkbox(lo)
    if up == 'I':
        wU, advU, lsbU = 0.49 * FL, 0.49 * FL + 0.10 * FL, 0.05 * FL
    gapc = 0.12 * FL
    wtot = advU + gapc + advL
    gx = BX + (BW - wtot) / 2
    xU, xL = gx, gx + advU + gapc

    def draw_hollow_pair():
        if up == 'I':
            bw = 0.49 * FL
            y1, y2 = gb - CAPT + ST / 2, gb - ST / 2
            hol([f'M {xU+bw/2:.2f} {y1:.2f} L {xU+bw/2:.2f} {y2:.2f}',
                 f'M {xU+ST/2:.2f} {y1:.2f} L {xU+bw-ST/2:.2f} {y1:.2f}',
                 f'M {xU+ST/2:.2f} {y2:.2f} L {xU+bw-ST/2:.2f} {y2:.2f}'], ST)
        else:
            A(f'<text x="{xU:.2f}" y="{gb:.2f}" font-family="School Print '
              f'Heavy" font-size="{FL:.1f}" fill="#fff" stroke="#000" '
              f'stroke-width="3.2" stroke-linejoin="round" '
              f'stroke-linecap="round">{up}</text>')
        if lo == 'e':
            r = (XHT - ST) / 2
            ccx, ccy = xL + lsbL + wL / 2, gb - XHT / 2

            def PT(ang):
                t = math.radians(ang)
                return ccx + r * math.cos(t), ccy - r * math.sin(t)
            p0, p1, p2 = PT(0), PT(150), PT(300)
            hol([f'M {p0[0]:.2f} {p0[1]:.2f} '
                 f'A {r:.2f} {r:.2f} 0 0 0 {p1[0]:.2f} {p1[1]:.2f} '
                 f'A {r:.2f} {r:.2f} 0 0 0 {p2[0]:.2f} {p2[1]:.2f}',
                 f'M {ccx-r:.2f} {ccy:.2f} L {ccx+r:.2f} {ccy:.2f}'], ST)
        else:
            A(f'<text x="{xL:.2f}" y="{gb:.2f}" font-family="School Print '
              f'Heavy" font-size="{FL:.1f}" fill="#fff" stroke="#000" '
              f'stroke-width="3.2" stroke-linejoin="round" '
              f'stroke-linecap="round">{lo}</text>')

    draw_hollow_pair()

    # --- пунктир, точки и стрелки ---
    def overlay(ch, x0ink, wink, is_upper):
        g = {'L': x0ink + ST / 2, 'R': x0ink + wink - ST / 2,
             'B': gb - ST / 2}
        if is_upper:
            g['T'] = gb - CAPT + ST / 2
        else:
            g['xt'] = gb - XHT + ST / 2
            g['at'] = gb - ASCT + ST / 2
            g['T'] = g['at'] if ch in ASCENDERS else g['xt']
            g['db'] = gb + DESC - ST / 2 if ch in DESCENDERS else gb - ST / 2
            g['dot'] = gb - XHT - ST * 1.15
        used = []
        for n, (pth, apt, adeg) in enumerate(LT.strokes(ch, g), 1):
            if pth == 'DOT':
                sx, sy = apt
            else:
                A(f'<path d="{pth}" fill="none" stroke="#000" '
                  f'stroke-width="1.5" stroke-dasharray="4.5,4.5"/>')
                mm = re.match(r'M ([-\d\.]+) ([-\d\.]+)', pth)
                sx, sy = float(mm.group(1)), float(mm.group(2))
                A(arrow_head(apt[0], apt[1], adeg, 6.2))
            for (ux, uy) in used:
                if abs(ux - sx) < 13 and abs(uy - sy) < 13:
                    sx, sy = sx + 10, sy + 10
            used.append((sx, sy))
            A(f'<circle cx="{sx:.2f}" cy="{sy:.2f}" r="6.4" fill="#000" '
              f'stroke="#fff" stroke-width="1.1"/>')
            A(f'<text x="{sx:.2f}" y="{sy+3.1:.2f}" text-anchor="middle" '
              f'font-family="Quicksand" font-weight="700" font-size="9" '
              f'fill="#fff">{n}</text>')

    overlay(up, xU + lsbU, wU, True)
    overlay(lo, xL + lsbL, wL, False)

    A(f'<text x="{L+2}" y="54" font-family="Quicksand" font-weight="700" '
      f'font-size="11" fill="#000">Name</text>')
    A(f'<line x1="{L+44}" y1="56" x2="{L+280}" y2="56" stroke="#000" '
      f'stroke-width="1.4"/>')
    A(f'<text x="{L}" y="104" font-family="Baloo 2" font-weight="800" '
      f'font-size="27" fill="#9a9a9a">Build a Sentence</text>')
    put(q, L + 2, 156, 34, bold=True)

    # ---- рисунок ----
    pn_y, pn_h = 178.0, 216.0
    A(f'<rect x="{L}" y="{pn_y}" width="{CW}" height="{pn_h}" rx="9" '
      f'fill="none" stroke="#000" stroke-width="1.8"/>')
    ground = pn_y + pn_h - 26
    A(f'<line x1="{L+28}" y1="{ground}" x2="{R-28}" y2="{ground}" '
      f'stroke="#000" stroke-width="1" stroke-dasharray="3,5"/>')
    aw, ah, grp = art(key)
    lh = 182.0
    lw = aw / ah * lh
    if lw > CW * 0.68:
        lw = CW * 0.68
        lh = ah / aw * lw
    A(f'<g transform="translate({CX-lw/2:.2f},{ground-lh:.2f}) '
      f'scale({lh/ah:.6f})">{grp}</g>')

    # ---- строка с предложением ----
    SB = 452.0
    ROWH = 2 * XH_R * FS
    for yy, wgt, dsh in ((SB - ROWH, 0.9, ''), ((SB - ROWH + SB) / 2, 0.9,
                         ' stroke-dasharray="5,6"'), (SB, 2.4, '')):
        A(f'<line x1="{L}" y1="{yy:.2f}" x2="{R}" y2="{yy:.2f}" '
          f'stroke="#000" stroke-width="{wgt}"{dsh}/>')
    x = L + 16
    for wd in words:
        x = put(wd, x, SB, FS)
        x += 16

    # ---- клетки ----
    BOX_H, CARD_H = 82.0, 70.0
    box_y = 468.0
    x = L + 6
    for bwid in box_w:
        A(f'<rect x="{x:.2f}" y="{box_y}" width="{bwid:.2f}" height="{BOX_H}" '
          f'rx="7" fill="none" stroke="#000" stroke-width="1.7"/>')
        x += bwid + 6

    # ---- пропись ----
    for yy, wgt, dsh in ((564.0, 0.9, ''), (590.0, 0.9,
                         ' stroke-dasharray="5,6"'), (616.0, 2.4, '')):
        A(f'<line x1="{L}" y1="{yy}" x2="{R}" y2="{yy}" stroke="#000" '
          f'stroke-width="{wgt}"{dsh}/>')

    # ---- разрез и карточки ----
    cut_y = 640.0
    A(f'<g transform="translate({L+5},{cut_y})" fill="none" stroke="#000" '
      f'stroke-width="1.5"><circle cx="0" cy="-4.6" r="3.3"/>'
      f'<circle cx="0" cy="4.6" r="3.3"/>'
      f'<line x1="2.6" y1="-3.2" x2="15" y2="5.5"/>'
      f'<line x1="2.6" y1="3.2" x2="15" y2="-5.5"/></g>')
    A(f'<line x1="{L+25}" y1="{cut_y}" x2="{R}" y2="{cut_y}" stroke="#000" '
      f'stroke-width="1.2" stroke-dasharray="7,6"/>')

    idx = list(range(len(words)))
    rnd = random.Random(seed)
    for _ in range(200):
        rnd.shuffle(idx)
        if all(i != j for i, j in enumerate(idx)):
            break
    cy0 = 648.0
    tot = sum(card_w[i] for i in idx)
    x0 = CX - tot / 2
    D = 'stroke="#000" stroke-width="1.2" stroke-dasharray="7,6" fill="none"'
    A(f'<rect x="{x0:.2f}" y="{cy0}" width="{tot:.2f}" height="{CARD_H}" {D}/>')
    x = x0
    for k, i in enumerate(idx):
        if k:
            A(f'<line x1="{x:.2f}" y1="{cy0}" x2="{x:.2f}" '
              f'y2="{cy0+CARD_H}" {D}/>')
        put(words[i], x + (card_w[i] - tw(words[i], FS)) / 2,
            cy0 + CARD_H / 2 + XH_R * FS / 2 + 2, FS)
        x += card_w[i]

    A(f'<text x="{CX}" y="752" text-anchor="middle" font-family="Quicksand" '
      f'font-weight="600" font-size="7.5" fill="#000">'
      f'Magic of Discoveries  |  For single classroom use only.</text>')
    A('</svg>')
    return '\n'.join(P)


def cover():
    P = []
    A = P.append
    A(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}pt" height="{H}pt" '
      f'viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" fill="#fff"/>')
    A(f'<text x="{CX}" y="150" text-anchor="middle" font-family="Baloo 2" '
      f'font-weight="800" font-size="52" fill="#000">Build a Sentence</text>')
    A(f'<text x="{CX}" y="196" text-anchor="middle" font-family="Baloo 2" '
      f'font-weight="800" font-size="30" fill="#9a9a9a">Animals A to Z</text>')
    A(f'<text x="{CX}" y="240" text-anchor="middle" font-family="Quicksand" '
      f'font-weight="600" font-size="15" fill="#000">'
      f'Cut and paste worksheets for beginning readers</text>')
    row = ['001', '002', '017', '046', '023', '013', '042', '003']
    bx, by, sz = 66.0, 300.0, 118.0
    for i, k in enumerate(row):
        aw, ah, grp = art(k)
        h = sz - 16
        w = aw / ah * h
        if w > sz - 10:
            w = sz - 10
            h = ah / aw * w
        cx = bx + (i % 4) * 120 + 60
        cy = by + (i // 4) * 140 + 60
        A(f'<g transform="translate({cx-w/2:.2f},{cy-h/2:.2f}) '
          f'scale({h/ah:.6f})">{grp}</g>')
    A(f'<text x="{CX}" y="640" text-anchor="middle" font-family="Quicksand" '
      f'font-weight="700" font-size="14" fill="#000">'
      f'44 no-prep printable worksheets  |  Kindergarten and Grade 1</text>')
    A(f'<text x="{CX}" y="700" text-anchor="middle" font-family="Baloo 2" '
      f'font-weight="800" font-size="20" fill="#000">'
      f'Magic of Discoveries</text>')
    A('</svg>')
    return '\n'.join(P)


def terms():
    P = []
    A = P.append
    A(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}pt" height="{H}pt" '
      f'viewBox="0 0 {W} {H}"><rect width="{W}" height="{H}" fill="#fff"/>')
    A(f'<text x="{L}" y="86" font-family="Baloo 2" font-weight="800" '
      f'font-size="30" fill="#000">How to use</text>')
    steps = ['1.  Read the question and the sentence at the top.',
             '2.  Cut out the word cards along the dotted lines.',
             '3.  Glue the words in the boxes in the right order.',
             '4.  Write the sentence on the line.',
             '5.  Color the picture and draw your own scene around it.']
    y = 130
    for s in steps:
        A(f'<text x="{L+6}" y="{y}" font-family="Quicksand" font-weight="600" '
          f'font-size="14" fill="#000">{s}</text>')
        y += 30
    A(f'<text x="{L}" y="{y+34}" font-family="Baloo 2" font-weight="800" '
      f'font-size="24" fill="#000">What is inside</text>')
    ins = ['55 worksheets: two for every letter A to Z, plus 3 bonus pages.',
           'Two sentence patterns:  I see a ...   and   This is a ...',
           'Eight sight words in total:  I, see, this, is, a, an.',
           'Uppercase and lowercase letter card on every page.',
           'Word cards are scrambled, so the child has to think.',
           'Black and white, no color ink needed.']
    y += 66
    for s in ins:
        A(f'<text x="{L+6}" y="{y}" font-family="Quicksand" font-weight="600" '
          f'font-size="14" fill="#000">{s}</text>')
        y += 26
    A(f'<text x="{L}" y="{y+34}" font-family="Baloo 2" font-weight="800" '
      f'font-size="24" fill="#000">Terms of use</text>')
    tt = ['This file is licensed to one teacher for one classroom.',
          'You may print as many copies as you need for your own students.',
          'You may not share, resell, or post this file online.',
          'All artwork is original and belongs to Magic of Discoveries.']
    y += 66
    for s in tt:
        A(f'<text x="{L+6}" y="{y}" font-family="Quicksand" font-weight="600" '
          f'font-size="13" fill="#000">{s}</text>')
        y += 24
    A(f'<text x="{CX}" y="752" text-anchor="middle" font-family="Quicksand" '
      f'font-weight="600" font-size="7.5" fill="#000">'
      f'Magic of Discoveries  |  For single classroom use only.</text>')
    A('</svg>')
    return '\n'.join(P)


if __name__ == '__main__':
    import cairosvg
    from pypdf import PdfWriter
    os.makedirs('pages', exist_ok=True)
    files = []
    for nm, svg in (('00-cover', cover()), ('01-terms', terms())):
        p = 'pages/%s.pdf' % nm
        cairosvg.svg2pdf(bytestring=svg.encode(), write_to=p)
        files.append(p)
    n = 0
    for letter, items in BOOK:
        for fi in range(2):
            key, word, article = items[fi]
            svg = page(letter, key, word, article, fi, seed=hash((letter, fi)) & 0xffff)
            n += 1
            p = 'pages/%02d-%s%d.pdf' % (n + 1, letter, fi + 1)
            cairosvg.svg2pdf(bytestring=svg.encode(), write_to=p)
            files.append(p)
            print(letter, fi + 1, word)
    for bi, (letter, key, word, article) in enumerate(BONUS):
        svg = page(letter, key, word, article, bi % 2,
                   seed=hash(('bonus', letter)) & 0xffff)
        n += 1
        p = 'pages/%02d-bonus-%s.pdf' % (n + 1, letter)
        cairosvg.svg2pdf(bytestring=svg.encode(), write_to=p)
        files.append(p)
        print('бонус', letter, word)
    wtr = PdfWriter()
    for f in files:
        wtr.append(f)
    wtr.write('/mnt/user-data/outputs/Build-a-Sentence-Animals-A-Z.pdf')
    print('страниц:', len(files))
