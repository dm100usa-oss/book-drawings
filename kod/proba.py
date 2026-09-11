import pymupdf, detect, vec, sovmest
from vec import bbox, fit

SRC = '/home/claude/book-drawings/pak/ishodniki/book eng print.pdf'
BOOK = '/home/claude/sklad/directed-drawing-worksheets-grades-k-2-letter-8.5x11.pdf'
FRAME = pymupdf.Rect(212, 360, 597, 628)   # pustoe pole na liste
PAD = 12.0                                  # otstup ot ramki


def align(steps):
    """Sdvigi shagov drug otnositelno druga, kak v build.py."""
    n = len(steps)
    offs = [pymupdf.Point(0, 0)]
    ok = True
    for k in range(1, n):
        gp = [p for p in steps[k][1] if vec.col(p) in (vec.GRAY, vec.GRAY2)]
        prev, cur = steps[k-1][0], steps[k][0]
        a = bbox(gp) if gp else None
        same = a is not None and prev is not None and \
            abs(a.width - prev.width) < 0.35*max(a.width, prev.width) + 4 and \
            abs(a.height - prev.height) < 0.35*max(a.height, prev.height) + 4
        if same:
            d = pymupdf.Point((prev.x0 + prev.x1)/2 - (a.x0 + a.x1)/2,
                              (prev.y0 + prev.y1)/2 - (a.y0 + a.y1)/2)
            # esli kniga narisovala seroe drugoy vysoty, centr ramki vret i
            # risunok v kartochke uezzhaet. Togda sovmeshchaem po samim liniyam.
            if (abs(a.width/prev.width - 1) < 0.10
                    and abs(a.height/prev.height - 1) > 0.15):
                t = sovmest.sdvig(gp, steps[k-1][1], nachalo=(d.x, d.y))
                if t:
                    d = pymupdf.Point(t[0], t[1])
            offs.append(offs[k-1] + d)
        else:
            ok = False
            offs.append(offs[k-1] + pymupdf.Point(prev.x0 - cur.x0, prev.y0 - cur.y0))
    frame = None
    for k, (r, ps) in enumerate(steps):
        pr = pymupdf.Rect(r) + (offs[k].x, offs[k].y, offs[k].x, offs[k].y)
        frame = pr if frame is None else frame | pr
    return offs, frame, ok


def draw_gray(page, paths, m, tone, thin=1.0):
    """Risuet puti odnim serym tonom. Beluyu zalivku ostavlyaet beloy."""
    s = vec.mscale(m)
    for p in paths:
        f0, c0 = p.get('fill'), p.get('color')
        white = f0 is not None and min(f0) > 0.95
        sh = page.new_shape()
        for it in p['items']:
            k = it[0]
            if k == 'l':
                sh.draw_line(vec.tp(it[1], m), vec.tp(it[2], m))
            elif k == 'c':
                sh.draw_bezier(vec.tp(it[1], m), vec.tp(it[2], m),
                               vec.tp(it[3], m), vec.tp(it[4], m))
            elif k == 're':
                sh.draw_rect(pymupdf.Rect(it[1] * m))
            elif k == 'qu':
                q = it[1]
                sh.draw_polyline([vec.tp(q.ul, m), vec.tp(q.ur, m),
                                  vec.tp(q.lr, m), vec.tp(q.ll, m), vec.tp(q.ul, m)])
        fill = (1, 1, 1) if white else (tone if f0 is not None else None)
        color = tone if c0 is not None else None
        w = (p.get('width') or 0) * s * thin
        sh.finish(color=color, fill=fill, width=w,
                  even_odd=p.get('even_odd', False),
                  closePath=p.get('closePath', True))
        sh.commit()


def make(out_path, variant, spi=9, page_no=3):
    doc = pymupdf.open(SRC)
    circles, steps, _ = detect.analyze_steps_page(doc[spi], doc)
    offs, fr, ok = align(steps)

    book = pymupdf.open(BOOK)
    out = pymupdf.open()
    out.insert_pdf(book, from_page=page_no, to_page=page_no)
    pg = out[0]

    dst = pymupdf.Rect(FRAME.x0 + PAD, FRAME.y0 + PAD,
                       FRAME.x1 - PAD, FRAME.y1 - PAD)
    base = fit(fr, dst)

    def mat(k):
        return pymupdf.Matrix(1, 0, 0, 1, offs[k].x, offs[k].y) * base

    if variant == 'A':
        draw_gray(pg, steps[1][1], mat(1), (0.72, 0.72, 0.72))
    else:
        draw_gray(pg, steps[0][1], mat(0), (0.85, 0.85, 0.85))
        new = [p for p in steps[1][1] if vec.col(p) not in (vec.GRAY, vec.GRAY2)]
        draw_gray(pg, new, mat(1), (0.66, 0.66, 0.66))

    out.save(out_path, garbage=4, deflate=True)
    return out_path


if __name__ == '__main__':
    make('/home/claude/proba-A.pdf', 'A')
    make('/home/claude/proba-B.pdf', 'B')
    print('gotovo')
