import numpy as np, pymupdf
from skimage.morphology import skeletonize
import vec

def word_polylines(paths, res=900):
    """Render filled word paths, skeletonize, return polylines in source coords."""
    b = vec.bbox(paths)
    pad = 6
    sc = res / max(b.width, b.height)
    W = int(b.width*sc)+2*pad
    H = int(b.height*sc)+2*pad
    doc = pymupdf.open()
    pg = doc.new_page(width=W, height=H)
    m = pymupdf.Matrix(sc, 0, 0, sc, pad - b.x0*sc, pad - b.y0*sc)
    vec.replay2(pg, paths, m, fill=(0, 0, 0), color=None)
    pix = pg.get_pixmap(colorspace=pymupdf.csGRAY, alpha=False)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
    binimg = img < 128
    sk = skeletonize(binimg)
    polys = trace_skeleton(sk, min_spur=res*0.045)
    out = []
    inv = ~m
    for p in polys:
        pts = [pymupdf.Point(x, y) * inv for (x, y) in p]
        out.append(pts)
    return out, b

def trace_skeleton(sk, min_spur=20):
    H, W = sk.shape
    pts = set(zip(*np.nonzero(sk)))  # (row, col)
    nbr = {}
    off = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
    for (r, c) in pts:
        ns = [(r+dr, c+dc) for dr, dc in off if (r+dr, c+dc) in pts]
        nbr[(r, c)] = ns
    nodes = {p for p in pts if len(nbr[p]) != 2}
    edges = []
    visited = set()
    for n in nodes:
        for start in nbr[n]:
            if (n, start) in visited:
                continue
            path = [n, start]
            visited.add((n, start))
            prev, cur = n, start
            while cur not in nodes:
                nxt = [q for q in nbr[cur] if q != prev]
                if not nxt:
                    break
                prev, cur = cur, nxt[0]
                path.append(cur)
            visited.add((path[-1], path[-2]))
            edges.append(path)
    # closed loops (no nodes)
    rest = pts - {p for e in edges for p in e}
    while rest:
        s = next(iter(rest))
        loop = [s]; rest.discard(s)
        prev, cur = None, s
        while True:
            nxt = [q for q in nbr[cur] if q != prev and q in rest]
            if not nxt:
                break
            prev, cur = cur, nxt[0]
            loop.append(cur); rest.discard(cur)
        loop.append(s)
        edges.append(loop)
    # prune spurs
    keep = []
    for e in edges:
        d0, d1 = len(nbr[e[0]]), len(nbr[e[-1]])
        if plen(e) < min_spur and ((d0 == 1 and d1 >= 3) or (d1 == 1 and d0 >= 3)):
            continue
        keep.append(e)
    return [simplify([(c, r) for (r, c) in e], 1.4) for e in keep]

def plen(e):
    return sum(((e[i][0]-e[i+1][0])**2 + (e[i][1]-e[i+1][1])**2)**0.5 for i in range(len(e)-1))

def simplify(pts, tol):
    if len(pts) < 3:
        return pts
    def rdp(p):
        if len(p) < 3:
            return p
        x0, y0 = p[0]; x1, y1 = p[-1]
        dx, dy = x1-x0, y1-y0
        n = (dx*dx+dy*dy)**0.5
        best, bi = -1, 0
        for i in range(1, len(p)-1):
            x, y = p[i]
            d = abs(dy*x - dx*y + x1*y0 - y1*x0)/n if n else ((x-x0)**2+(y-y0)**2)**0.5
            if d > best:
                best, bi = d, i
        if best > tol:
            return rdp(p[:bi+1])[:-1] + rdp(p[bi:])
        return [p[0], p[-1]]
    import sys
    sys.setrecursionlimit(10000)
    return rdp(pts)


def text_polylines(text, fontfile, size=600):
    """Centerline polylines for a word set in a real font.
    Returns (polys, capH, ascH, xH, adv) in font units (y up, baseline 0)."""
    import pymupdf
    from fontTools.ttLib import TTFont
    from fontTools.pens.boundsPen import BoundsPen
    tf = TTFont(fontfile)
    upem = tf['head'].unitsPerEm
    gs, cm = tf.getGlyphSet(), tf.getBestCmap()

    def gh(ch):
        bp = BoundsPen(gs)
        gs[cm[ord(ch)]].draw(bp)
        return bp.bounds[3]

    f = pymupdf.Font(fontfile=fontfile)
    tw = f.text_length(text, size)
    pad = 30
    Wp, Hp = int(tw) + 2*pad, int(size*1.8)
    base = size*1.25
    doc = pymupdf.open()
    pg = doc.new_page(width=Wp, height=Hp)
    w = pymupdf.TextWriter(pg.rect)
    w.append((pad, base), text, font=f, fontsize=size)
    w.write_text(pg, color=(0, 0, 0))
    pix = pg.get_pixmap(colorspace=pymupdf.csGRAY, alpha=False)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
    binimg = img < 128
    from skimage.measure import label, regionprops
    lab = label(binimg)
    dots = []
    keep = binimg.copy()
    for r in regionprops(lab):
        h = r.bbox[2] - r.bbox[0]
        w = r.bbox[3] - r.bbox[1]
        fill = r.area / float(h*w)
        if max(h, w) < size*0.16 and abs(h - w) < 0.35*max(h, w) and fill > 0.62:
            cy, cx = r.centroid
            rad = ((h + w) / 4.0)
            dots.append((cx, cy, rad))
            keep[lab == r.label] = False
    sk = skeletonize(keep)
    polys = trace_skeleton(sk, min_spur=size*0.05)
    k = upem / size
    out = [[((x - pad)*k, (base - y)*k) for (x, y) in p] for p in polys]
    import math
    for (cx, cy, rad) in dots:
        c = [(cx + rad*math.cos(t*math.pi/8), cy + rad*math.sin(t*math.pi/8)) for t in range(17)]
        out.append([((x - pad)*k, (base - y)*k) for (x, y) in c])
    return out, gh('E'), gh('l'), gh('o'), tw*k


def trace_polylines(paths, res=1100, close_r=6):
    """Turn the book's dashed trace figure into clean centre-line polylines."""
    import pymupdf, vec
    from skimage.morphology import binary_closing, disk
    b = vec.bbox(paths)
    pad = 14
    sc = res / max(b.width, b.height)
    W = int(b.width*sc) + 2*pad
    H = int(b.height*sc) + 2*pad
    doc = pymupdf.open()
    pg = doc.new_page(width=W, height=H)
    m = pymupdf.Matrix(sc, 0, 0, sc, pad - b.x0*sc, pad - b.y0*sc)
    vec.replay2(pg, paths, m, fill=(0, 0, 0), color=None)
    pix = pg.get_pixmap(colorspace=pymupdf.csGRAY, alpha=False)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
    binimg = img < 128
    r = max(2, int(close_r * sc / 10))
    closed = binary_closing(binimg, disk(r))
    sk = skeletonize(closed)
    polys = trace_skeleton(sk, min_spur=res*0.03)
    inv = ~m
    out = []
    for p in polys:
        out.append([tuple(pymupdf.Point(x, y) * inv) for (x, y) in p])
    return out, b
