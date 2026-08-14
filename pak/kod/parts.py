import pymupdf, vec, detect
from vec import col, DEC, GRAY, BLACK, WHITE

def ribbon_inner(dr):
    best = None
    for x in dr:
        r = pymupdf.Rect(x['rect'])
        if col(x) == WHITE and r.y1 < 145 and r.width > 120 and 30 < r.height < 90:
            if best is None or r.get_area() > best.get_area():
                best = r
    return best

def title_paths(page):
    dr = page.get_drawings()
    inner = ribbon_inner(dr)
    if inner is None: return []
    box = inner + (2, 2, -2, -2)
    # Zaglavnaya bukva s udareniem, naprimer A v slove Aguila, torchit chut
    # vyshe belogo polya lenty. Poetomu verhnyaya granica podnimaetsya:
    # inache takaya bukva teryaetsya i nazvanie vyhodit bez pervoy bukvy.
    box = pymupdf.Rect(box.x0, inner.y0 - 10, box.x1, box.y1)
    return [x for x in dr if col(x) == BLACK and box.contains(pymupdf.Rect(x['rect']))]

def footer_word_paths(page):
    dr = page.get_drawings()
    return [x for x in dr if col(x) == BLACK and x['rect'].y0 > 750 and x['rect'].x0 > 125]

def circle_paths(page, circles):
    dr = page.get_drawings()
    out = []
    for c in circles:
        box = c + (-1.5, -1.5, 1.5, 1.5)
        out.append([x for x in dr if box.contains(pymupdf.Rect(x['rect']))])
    return out

ETALON = '/mnt/user-data/uploads/obrazec-lista.pdf'
_ETALON_DECOR = None


def etalon_decor():
    """Corner leaves copied from the approved sample sheet, exactly as they are.

    The same two drawings go on every sheet, at their original size and place,
    so all sheets match the sample instead of inheriting whatever background
    the book page happened to have.
    """
    global _ETALON_DECOR
    if _ETALON_DECOR is None:
        d = pymupdf.open(ETALON)
        _ETALON_DECOR = [x for x in d[0].get_drawings()
                         if vec.col(x) == (0.72, 0.72, 0.72)]
    return _ETALON_DECOR


def ink_frac(paths, n=60):
    """How much of its own box the drawing actually covers.

    A shell or a flag covers a good part of it; a length of string or a
    stray curve covers almost nothing, and must not be used as corner art.
    """
    import numpy as np
    b = vec.bbox(paths)
    if b.width <= 0 or b.height <= 0:
        return 0.0
    sc = n / max(b.width, b.height)
    W = max(int(b.width*sc), 2)
    H = max(int(b.height*sc), 2)
    doc = pymupdf.open()
    pg = doc.new_page(width=W, height=H)
    m = pymupdf.Matrix(sc, 0, 0, sc, -b.x0*sc, -b.y0*sc)
    vec.replay2(pg, paths, m, fill=(0, 0, 0), color=(0, 0, 0), width=0.6)
    pix = pg.get_pixmap(colorspace=pymupdf.csGRAY, alpha=False)
    a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width)
    return float((a < 200).mean())


def top_decor(page):
    """One clean object for each top corner, taken from the same book page.

    Not the whole tangle of background: just the single main drawing in that
    corner (a shell, a starfish, a cloud) together with its own inner details,
    so it reads clearly once it is scaled down to the corner of the sheet.
    """
    dr = page.get_drawings()
    dec = [x for x in dr if col(x) == DEC]
    if not dec:
        return {}
    pr = page.rect
    W, H = pr.width, pr.height
    out = {}
    for key, lo, hi in (('tl', 0.0, W/2), ('tr', W/2, W)):
        cands = []
        for x in dec:
            b = pymupdf.Rect(x['rect'])
            cx, cy = (b.x0+b.x1)/2, (b.y0+b.y1)/2
            if cy > H/2 or not (lo <= cx < hi):
                continue
            vis = b & pr
            if vis.is_empty:
                continue
            if min(b.width, b.height) < 25 or b.get_area() < 2000:
                continue
            if vis.get_area() < 0.5 * b.get_area():
                continue
            if max(b.width, b.height) > 2.5 * min(b.width, b.height):
                continue
            box = b + (-3, -3, 3, 3)
            inner = [y for y in dec
                     if y is not x and box.contains(pymupdf.Rect(y['rect']))]
            compact = 1 if max(b.width, b.height) < 1.4 * min(b.width, b.height) else 0
            cands.append((compact, len(inner), vis.get_area(), x, inner))
        if not cands:
            return {}
        cands.sort(key=lambda t: (-t[0], -t[1], -t[2]))
        _, _, _, x, inner = cands[0]
        out[key] = [x] + inner
    return out


def decor(page):
    dr = page.get_drawings()
    dec = [x for x in dr if col(x) == DEC]
    groups = detect.cluster(dec, pad=10)
    W, H = page.rect.width, page.rect.height
    corners = {'tl': None, 'tr': None, 'bl': None, 'br': None}
    for g in groups:
        b = vec.bbox(g)
        cx, cy = (b.x0+b.x1)/2, (b.y0+b.y1)/2
        k = ('t' if cy < H/2 else 'b') + ('l' if cx < W/2 else 'r')
        if corners[k] is None or b.get_area() > vec.bbox(corners[k]).get_area():
            corners[k] = g
    return corners


def word_metrics(paths):
    """baseline, cap top, x-height top of the outlined word (source coords)."""
    import statistics
    items = sorted([pymupdf.Rect(p['rect']) for p in paths], key=lambda r: r.x0)
    groups = []
    for r in items:
        if groups and r.x0 <= groups[-1].x1 + 0.6:
            groups[-1] = groups[-1] | r
        else:
            groups.append(pymupdf.Rect(r))
    bottoms = sorted(g.y1 for g in groups)
    baseline = statistics.median(bottoms)
    cap_top = min(g.y0 for g in groups)
    cap_h = baseline - cap_top
    short = [g.y0 for g in groups if (baseline - g.y0) < 0.82 * cap_h]
    x_top = statistics.median(short) if short else cap_top
    return baseline, cap_top, x_top, groups


def bottom_decor(page):
    """Risunok iz nizhney chasti stranicy knigi: po odnomu predmetu v kazhdyy
    nizhniy ugol. Nuzhen, chtoby rebenok mog ego raskrasit."""
    dr = page.get_drawings()
    dec = [x for x in dr if col(x) == DEC]
    if not dec:
        return {}
    pr = page.rect
    W, H = pr.width, pr.height
    out = {}
    for key, lo, hi in (('bl', 0.0, W/2), ('br', W/2, W)):
        g = [x for x in dec
             if (x['rect'].y0 + x['rect'].y1)/2 > H*0.62
             and lo <= (x['rect'].x0 + x['rect'].x1)/2 < hi]
        if not g:
            continue
        gs = detect.cluster(g, pad=10)
        gs = [q for q in gs if vec.bbox(q).get_area() > 900]
        if not gs:
            continue
        gs.sort(key=lambda q: -vec.bbox(q).get_area())
        out[key] = gs[0]
    return out
