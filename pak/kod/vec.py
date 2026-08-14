import pymupdf

# Chernye linii knigi risuyutsya plotnee, chtoby na pechati byli chernymi.
# Serye linii ne trogayutsya voobshche.
FATB = 0.0
# Serye linii knigi (risunok dlya obvodki i uzhe narisovannoe v shagah)
# delayutsya temnee vot vo skolko raz. Tolshchina ne menyaetsya.
GDARK = 1.0

DEC = (0.692,0.685,0.684)   # decorative leaves
GRAY = (0.646,0.644,0.644)  # trace / previous-step gray
GRAY2 = (0.639,0.637,0.635)
BLACK = (0.113,0.112,0.107)
WHITE = (1.0,1.0,1.0)

def grayer(c):
    """Seroe iz knigi temneet na GDARK. Chernoe, beloe i dekor ne trogaem."""
    if GDARK >= 1.0 or not c:
        return c
    if max(c) - min(c) < 0.06 and 0.55 < max(c) < 0.68:
        return tuple(v * GDARK for v in c)
    return c


def black(c):
    """Pochti chernoe iz knigi (0.113) stanovitsya chistym chernym.
    Seroe i beloe ne trogaem: seroe ostaetsya serym."""
    if c and max(c) < 0.30 and max(c) - min(c) < 0.06:
        return (0.0, 0.0, 0.0)
    return c


def col(x):
    c = x.get('fill') or x.get('color')
    return tuple(round(v,3) for v in c) if c else None

def mscale(m):
    """Vo skolko raz matrica menyaet razmer risunka."""
    return abs(m.a * m.d - m.b * m.c) ** 0.5


def tp(p, m):
    return pymupdf.Point(p) * m

def replay(page, paths, m):
    """Redraw vector paths onto page with matrix m."""
    for p in paths:
        sh = page.new_shape()
        for it in p['items']:
            k = it[0]
            if k == 'l':
                sh.draw_line(tp(it[1],m), tp(it[2],m))
            elif k == 'c':
                sh.draw_bezier(tp(it[1],m), tp(it[2],m), tp(it[3],m), tp(it[4],m))
            elif k == 're':
                r = it[1] * m
                sh.draw_rect(pymupdf.Rect(r))
            elif k == 'qu':
                q = it[1]
                sh.draw_polyline([tp(q.ul,m), tp(q.ur,m), tp(q.lr,m), tp(q.ll,m), tp(q.ul,m)])
        fill = grayer(black(p.get('fill')))
        stroke = grayer(black(p.get('color')))
        # tolshchina linii iz knigi umenshaetsya vmeste s risunkom,
        # inache u umenshennogo shaga linii ostayutsya knizhnoy tolshchiny
        w = (p.get('width') or 0) * mscale(m)
        if FATB and fill == (0.0, 0.0, 0.0) and stroke is None:
            stroke, w = fill, FATB
        elif FATB and stroke == (0.0, 0.0, 0.0):
            # figura zalita belym s chernoy obvodkoy: chernoe dolzhno byt
            # plotnee serogo, kak na etalonnom liste
            w = w + FATB
        sh.finish(color=stroke, fill=fill, width=w,
                  even_odd=p.get('even_odd', False),
                  closePath=p.get('closePath', True),
                  fill_opacity=p.get('fill_opacity') or 1,
                  stroke_opacity=p.get('stroke_opacity') or 1)
        sh.commit()

def fit(src_rect, dst_rect, keep=True):
    """matrix mapping src_rect into dst_rect"""
    sx = dst_rect.width/src_rect.width
    sy = dst_rect.height/src_rect.height
    if keep:
        s = min(sx, sy); sx = sy = s
    w = src_rect.width*sx; h = src_rect.height*sy
    ox = dst_rect.x0 + (dst_rect.width-w)/2
    oy = dst_rect.y0 + (dst_rect.height-h)/2
    m = pymupdf.Matrix(sx,0,0,sy, ox - src_rect.x0*sx, oy - src_rect.y0*sy)
    return m

def bbox(paths):
    r = None
    for p in paths:
        r = pymupdf.Rect(p['rect']) if r is None else r | p['rect']
    return r

def replay2(page, paths, m, fill=None, color=None, width=None, dashes=None, stroke_only=False):
    for p in paths:
        sh = page.new_shape()
        for it in p['items']:
            k = it[0]
            if k == 'l':
                sh.draw_line(tp(it[1],m), tp(it[2],m))
            elif k == 'c':
                sh.draw_bezier(tp(it[1],m), tp(it[2],m), tp(it[3],m), tp(it[4],m))
            elif k == 're':
                sh.draw_rect(pymupdf.Rect(it[1] * m))
            elif k == 'qu':
                q = it[1]
                sh.draw_polyline([tp(q.ul,m), tp(q.ur,m), tp(q.lr,m), tp(q.ll,m), tp(q.ul,m)])
        f = None if stroke_only else (fill if fill is not None else grayer(black(p.get('fill'))))
        c = color if color is not None else grayer(black(p.get('color')))
        w = width if width is not None else (p.get('width') or 0)
        if FATB and f == (0.0, 0.0, 0.0) and c is None:
            c, w = f, FATB
        sh.finish(color=c, fill=f, width=w, dashes=dashes,
                  even_odd=p.get('even_odd', False),
                  closePath=p.get('closePath', True))
        sh.commit()
