"""Tochnoe sovmeshchenie shaga s predydushchim.

Obychno hvataet sovmeshcheniya po centram ramok: seroe v shage eto risunok
predydushchego shaga, i ramki u nih odinakovye. No inogda kniga risuet seroe
inache: u mashiny ono na polovinu vyshe, u samoleta na tret nizhe. Togda centry
ramok ne sovpadayut s figuroy, i risunok v kartochke uezzhaet vverh ili vniz.

Zdes sovmeshchenie schitaetsya po samim liniyam: seroe nakladyvaetsya na
predydushchiy risunok i sdvigaetsya do nailuchshego sovpadeniya.
"""
import numpy as np
import pymupdf


def tochki(paths, shag=3.0):
    """Tochki vdol vseh liniy puti."""
    out = []
    for p in paths:
        for it in p['items']:
            k = it[0]
            if k == 'l':
                a, b = pymupdf.Point(it[1]), pymupdf.Point(it[2])
                n = max(2, int(abs(a - b) / shag))
                for i in range(n + 1):
                    t = i / n
                    out.append((a.x + (b.x - a.x) * t, a.y + (b.y - a.y) * t))
            elif k == 'c':
                q = [pymupdf.Point(it[i]) for i in (1, 2, 3, 4)]
                for i in range(9):
                    t = i / 8.0
                    x = ((1-t)**3*q[0].x + 3*(1-t)**2*t*q[1].x
                         + 3*(1-t)*t*t*q[2].x + t**3*q[3].x)
                    y = ((1-t)**3*q[0].y + 3*(1-t)**2*t*q[1].y
                         + 3*(1-t)*t*t*q[2].y + t**3*q[3].y)
                    out.append((x, y))
            elif k == 're':
                r = pymupdf.Rect(it[1])
                for a, b in ((r.tl, r.tr), (r.tr, r.br), (r.br, r.bl), (r.bl, r.tl)):
                    n = max(2, int(abs(a - b) / shag))
                    for i in range(n + 1):
                        t = i / n
                        out.append((a.x + (b.x - a.x) * t, a.y + (b.y - a.y) * t))
            elif k == 'qu':
                q = it[1]
                for pt in (q.ul, q.ur, q.lr, q.ll):
                    out.append((pt.x, pt.y))
    return np.array(out) if out else np.zeros((0, 2))


def sdvig(seroe, predydushchiy, nachalo=(0.0, 0.0), predel=45.0):
    """Na skolko sdvinut seroe, chtoby ono leglo na predydushchiy risunok.
    Vozvrashchaet (dx, dy) ili None, esli schitat ne iz chego."""
    A = tochki(seroe)
    B = tochki(predydushchiy)
    if len(A):
        A = A + np.array(nachalo, dtype=float)   # gruboe sovmeshchenie po ramkam
    if len(A) < 20 or len(B) < 20:
        return None
    pole = 4.0                     # dopusk: liniya schitaetsya sovpavshey
    x0 = min(A[:, 0].min(), B[:, 0].min()) - predel - pole
    y0 = min(A[:, 1].min(), B[:, 1].min()) - predel - pole
    x1 = max(A[:, 0].max(), B[:, 0].max()) + predel + pole
    y1 = max(A[:, 1].max(), B[:, 1].max()) + predel + pole
    W, H = int(x1 - x0) + 1, int(y1 - y0) + 1
    if W * H > 4_000_000:
        return None
    maska = np.zeros((H, W), dtype=bool)
    bi = np.clip(((B - [x0, y0]) + 0.5).astype(int), [0, 0], [W-1, H-1])
    maska[bi[:, 1], bi[:, 0]] = True
    # rasshiryaem liniyu na dopusk, chtoby sovpadenie schitalos ne pikselem v piksel
    r = int(pole)
    rast = maska.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dx*dx + dy*dy > r*r:
                continue
            rast |= np.roll(np.roll(maska, dy, axis=0), dx, axis=1)
    ai = ((A - [x0, y0]) + 0.5).astype(int)
    best, bd = -1, (0.0, 0.0)
    for krupno in (4, 1):
        if krupno == 4:
            diap = range(-int(predel), int(predel) + 1, 4)
            cx, cy = 0, 0
        else:
            diap = range(-4, 5)
            cx, cy = int(bd[0]), int(bd[1])
        for dy in diap:
            for dx in diap:
                xx = ai[:, 0] + cx + dx
                yy = ai[:, 1] + cy + dy
                ok = (xx >= 0) & (xx < W) & (yy >= 0) & (yy < H)
                s = int(rast[yy[ok], xx[ok]].sum())
                if s > best:
                    best, bd = s, (cx + dx, cy + dy)
    if best < 0.35 * len(A):
        return None
    return float(bd[0]) + nachalo[0], float(bd[1]) + nachalo[1]
