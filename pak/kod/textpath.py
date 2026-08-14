import pymupdf
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import RecordingPen

_cache = {}

def load(path):
    if path not in _cache:
        f = TTFont(path)
        _cache[path] = (f, f.getGlyphSet(), f.getBestCmap(), f['head'].unitsPerEm)
    return _cache[path]


def _quads_to_cubes(start, pts):
    """pts: list of points, last may be on-curve (or None for closed contour)."""
    out = []
    cur = start
    if pts[-1] is None:
        pts = pts[:-1]
        implied_close = True
    else:
        implied_close = False
    for i in range(len(pts)-1) if not implied_close else range(len(pts)):
        off = pts[i]
        if implied_close:
            nxt = pts[(i+1) % len(pts)]
            on = ((off[0]+nxt[0])/2.0, (off[1]+nxt[1])/2.0)
        else:
            nxt = pts[i+1]
            on = nxt if i == len(pts)-2 else ((off[0]+nxt[0])/2.0, (off[1]+nxt[1])/2.0)
        c1 = (cur[0] + 2.0/3*(off[0]-cur[0]), cur[1] + 2.0/3*(off[1]-cur[1]))
        c2 = (on[0] + 2.0/3*(off[0]-on[0]), on[1] + 2.0/3*(off[1]-on[1]))
        out.append((cur, c1, c2, on))
        cur = on
    return out, cur


def word_contours(text, fontfile, tracking=0.0):
    """Return (contours, advance, ymax, xheight, upem) in font units, y up, baseline y=0."""
    f, gs, cmap, upem = load(fontfile)
    hmtx = f['hmtx']
    contours = []
    x = 0.0
    ymax = 0.0
    for ch in text:
        gn = cmap.get(ord(ch))
        if gn is None:
            x += upem*0.3
            continue
        pen = RecordingPen()
        gs[gn].draw(pen)
        cur = None
        start = None
        cont = []
        for op, args in pen.value:
            if op == 'moveTo':
                if cont:
                    contours.append(cont); cont = []
                cur = args[0]; start = cur
                cont = [('m', (cur[0]+x, cur[1]))]
            elif op == 'lineTo':
                p = args[0]
                cont.append(('l', (p[0]+x, p[1])))
                cur = p
            elif op == 'curveTo':
                pts = list(args)
                if len(pts) == 3:
                    cont.append(('c', (pts[0][0]+x, pts[0][1]), (pts[1][0]+x, pts[1][1]), (pts[2][0]+x, pts[2][1])))
                    cur = pts[2]
                else:
                    for p in pts:
                        cont.append(('l', (p[0]+x, p[1]))); cur = p
            elif op == 'qCurveTo':
                cubes, cur = _quads_to_cubes(cur, list(args))
                for (a, c1, c2, on) in cubes:
                    cont.append(('c', (c1[0]+x, c1[1]), (c2[0]+x, c2[1]), (on[0]+x, on[1])))
            elif op == 'closePath':
                if cont:
                    cont.append(('z', (start[0]+x, start[1])))
                    contours.append(cont); cont = []
        if cont:
            contours.append(cont)
        x += hmtx[gn][0] + tracking
    for c in contours:
        for it in c:
            for p in it[1:]:
                ymax = max(ymax, p[1])
    xh = getattr(f['OS/2'], 'sxHeight', 0) or upem*0.52
    return contours, x, ymax, xh, upem


def draw_word(page, text, fontfile, x0, baseline, scale,
              color=(0.15, 0.15, 0.15), width=1.4, dashes="[4 3.4] 0"):
    contours, adv, ymax, xh, upem = word_contours(text, fontfile)
    def T(p):
        return pymupdf.Point(x0 + p[0]*scale, baseline - p[1]*scale)
    sh = page.new_shape()
    for c in contours:
        cur = None
        for it in c:
            k = it[0]
            if k == 'm':
                cur = T(it[1])
            elif k == 'l':
                p = T(it[1]); sh.draw_line(cur, p); cur = p
            elif k == 'c':
                c1, c2, p = T(it[1]), T(it[2]), T(it[3])
                sh.draw_bezier(cur, c1, c2, p); cur = p
            elif k == 'z':
                p = T(it[1])
                if abs(p.x-cur.x) > 0.01 or abs(p.y-cur.y) > 0.01:
                    sh.draw_line(cur, p)
                cur = p
    sh.finish(color=color, fill=None, width=width, dashes=dashes, closePath=False)
    sh.commit()
    return adv*scale
