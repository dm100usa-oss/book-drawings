import os
DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
NAME = lambda ch: ('up-' if ch.isupper() else 'low-') + ch

"""Собирает из готовых букв настоящий шрифтовой файл.

Каждая буква рисуется целиком (контур, пунктир, стрелки, кружки с цифрами),
переводится в кривые и кладётся в шрифт как один знак.
"""
import io, json, os, re, subprocess
import numpy as np, cairosvg
from PIL import Image
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.transformPen import TransformPen
from fontTools.svgLib.path import parse_path
from fontTools.misc.transform import Transform

V = json.load(open(DATA+'/vec3/letters.json'))
OUT = os.path.join(os.path.dirname(DATA), 'out')
os.makedirs(OUT, exist_ok=True)
LET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
CIRC_R, RING, DIG, LW = 3.7, 0.8, 5.6, 1.33

UPM = 1000
CAP = 700.0            # высота заглавной в единицах шрифта
K = CAP / 100.0        # одна наша единица = столько единиц шрифта
SB = 35                # поля слева и справа
PX = 26                # пикселей на одну нашу единицу при отрисовке


def letter_svg(ch, pad=2.0):
    L = V[ch]
    x0, x1 = -pad, L['w'] + pad
    y0, y1 = L['top'] - pad, L['bot'] + pad
    for c in L['circles']:
        x0 = min(x0, c['x'] - CIRC_R - pad); x1 = max(x1, c['x'] + CIRC_R + pad)
        y0 = min(y0, c['y'] - CIRC_R - pad); y1 = max(y1, c['y'] + CIRC_R + pad)
    for e in L.get('extra', []):
        if e.get('kind') == 'ring':
            x0 = min(x0, e['x'] - e['r'] - pad); x1 = max(x1, e['x'] + e['r'] + pad)
            y0 = min(y0, e['y'] - e['r'] - pad); y1 = max(y1, e['y'] + e['r'] + pad)
        elif e.get('kind') == 'dash':
            for px, py in e['pts']:
                x0 = min(x0, px - pad); x1 = max(x1, px + pad)
                y0 = min(y0, py - pad); y1 = max(y1, py + pad)
        else:
            r = e['s'] * 1.3
            x0 = min(x0, e['x'] - r - pad); x1 = max(x1, e['x'] + r + pad)
            y0 = min(y0, e['y'] - r - pad); y1 = max(y1, e['y'] + r + pad)
    body = ''.join('<path d="%s"/>' % d for d in L['paths'])
    g = ('<g transform="scale(%s) translate(%.3f,%.3f) translate(0,%s) scale(0.1,-0.1)" '
         'fill="#000">%s</g>' % (1 / L['PPU'], -L['left_px'], -L['base_px'], L['ph'], body))
    for e in L.get('extra', []):
        if e.get('kind') == 'ring':
            g += ('<circle cx="%.3f" cy="%.3f" r="%.3f" fill="none" stroke="#000" '
                  'stroke-width="%s"/>' % (e['x'], e['y'], e['r'] - LW / 2, LW))
        elif e.get('kind') == 'dash':
            d = 'M ' + ' L '.join('%.2f %.2f' % (px, py) for px, py in e['pts'])
            g += ('<path d="%s" fill="none" stroke="#000" stroke-width="0.62" '
                  'stroke-dasharray="2.2,2.2" stroke-linecap="round"/>' % d)
        else:
            g += ('<g transform="translate(%.3f,%.3f) rotate(%s)"><path d="M 0 0 '
                  'L %.2f %.2f L %.2f %.2f Z" fill="#000"/></g>'
                  % (e['x'], e['y'], e['a'], -e['s'] * 1.15, e['s'] * 0.6,
                     -e['s'] * 1.15, -e['s'] * 0.6))
    for c in L['circles']:
        g += ('<circle cx="%.3f" cy="%.3f" r="%.3f" fill="#fff" stroke="#000" '
              'stroke-width="%s"/>'
              '<text x="%.3f" y="%.3f" text-anchor="middle" font-family="Quicksand" '
              'font-weight="700" font-size="%s" fill="#000">%s</text>'
              % (c['x'], c['y'], CIRC_R - RING / 2, RING,
                 c['x'], c['y'] + DIG * 0.35, DIG, c['n']))
    w, h = x1 - x0, y1 - y0
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
           'viewBox="%.3f %.3f %.3f %.3f"><rect x="%.3f" y="%.3f" width="%.3f" '
           'height="%.3f" fill="#fff"/>%s</svg>'
           % (round(w * PX), round(h * PX), x0, y0, w, h, x0, y0, w, h, g))
    return svg, x0, y0, w, h


def outline(ch):
    """рисует букву, обводит по контуру и возвращает кривые в единицах шрифта"""
    svg, x0, y0, w, h = letter_svg(ch)
    png = cairosvg.svg2png(bytestring=svg.encode())
    im = Image.open(io.BytesIO(png)).convert('L')
    a = np.array(im) < 128
    ys, xs = np.where(a)
    # рамка чернил в наших единицах
    ux0 = x0 + (xs.min() / im.width) * w
    ux1 = x0 + ((xs.max() + 1) / im.width) * w
    uy0 = y0 + (ys.min() / im.height) * h
    uy1 = y0 + ((ys.max() + 1) / im.height) * h
    Image.fromarray((~a * 255).astype(np.uint8)).save('/tmp/f.pbm')
    subprocess.run(['potrace', '-s', '-o', '/tmp/f.svg', '--turdsize', '2',
                    '--alphamax', '1.0', '--opttolerance', '0.15', '/tmp/f.pbm'],
                   check=True)
    s = open('/tmp/f.svg').read()
    ds = re.findall(r'\sd="([^"]+)"', s)
    m = re.search(r'transform="translate\(([\d.\-]+),([\d.\-]+)\) '
                  r'scale\(([\d.\-]+),([\d.\-]+)\)"', s)
    tx, ty, sx, sy = (float(v) for v in m.groups())
    pre = Transform(sx, 0, 0, sy, tx, ty)          # из потрейса в точки
    # рамка контура в точках
    from fontTools.pens.boundsPen import ControlBoundsPen
    bp = ControlBoundsPen(None)
    tp = TransformPen(bp, pre)
    for d in ds:
        parse_path(d, tp)
    bx0, by0, bx1, by1 = bp.bounds
    scale = (ux1 - ux0) / (bx1 - bx0) * K          # точки -> единицы шрифта
    return ds, pre, scale, bx0, by0, (ux0, uy0)


def build():
    glyphs, widths, order = {}, {}, ['.notdef', 'space']
    pen = TTGlyphPen(None); glyphs['.notdef'] = pen.glyph(); widths['.notdef'] = 400
    pen = TTGlyphPen(None); glyphs['space'] = pen.glyph(); widths['space'] = 300
    cmap = {32: 'space'}
    for ch in LET:
        ds, pre, scale, bx0, by0, (ux0, uy0) = outline(ch)
        # ставим букву: левый край чернил в SB, нижняя линия письма в 0
        post = Transform(scale, 0, 0, -scale,
                         SB - bx0 * scale, scale * by0 - K * uy0)
        pen = TTGlyphPen(None)
        tp = TransformPen(Cu2QuPen(pen, max_err=1.0), post.transform(pre))
        for d in ds:
            parse_path(d, tp)
        name = ('up' + ch) if ch.isupper() else ('low' + ch)
        glyphs[name] = pen.glyph()
        widths[name] = int(round(V[ch]['w'] * K)) + 2 * SB
        cmap[ord(ch)] = name
        order.append(name)
        print(' ', ch, 'ширина', widths[name], flush=True)
    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap(cmap)
    fb.setupGlyf(glyphs)
    fb.setupHorizontalMetrics({g: (widths[g], 0) for g in order})
    fb.setupHorizontalHeader(ascent=820, descent=-260)
    fb.setupNameTable({
        'familyName': 'Magic Trace', 'styleName': 'Regular',
        'psName': 'MagicTrace-Regular', 'version': 'Version 1.000',
        'copyright': 'Copyright Magic of Discoveries LLC',
        'manufacturer': 'Magic of Discoveries LLC',
        'licenseDescription': 'For use in Magic of Discoveries products.',
    })
    fb.setupOS2(sTypoAscender=820, sTypoDescender=-260, usWinAscent=820,
                usWinDescent=260, sCapHeight=int(CAP), sxHeight=int(CAP / 2))
    fb.setupPost()
    os.makedirs('/mnt/user-data/outputs', exist_ok=True)
    fb.save(OUT+'/MagicTrace-Regular.ttf')
    print('готово')


if __name__ == '__main__':
    build()
