import pymupdf, vec
from vec import col, DEC, GRAY, GRAY2, BLACK, WHITE


def acol(x):
    """Cvet risunka. Figura, zalitaya belym i obvedennaya liniey, eto ne
    pustoe mesto: takaya figura schitaetsya po cvetu svoey obvodki."""
    c = col(x)
    if c == WHITE and x.get('color'):
        return tuple(round(v, 3) for v in x['color'])
    return c

def is_square(r, lo=24, hi=38):
    return lo <= r.width <= hi and lo <= r.height <= hi and abs(r.width-r.height) < 4

def find_circles(dr):
    out = []
    for x in dr:
        r = pymupdf.Rect(x['rect'])
        if col(x) == BLACK and is_square(r):
            if any(col(y) == WHITE and abs(y['rect'].x0-r.x0) < 3 and abs(y['rect'].y0-r.y0) < 3
                   and is_square(pymupdf.Rect(y['rect'])) for y in dr):
                if not any(abs(r.x0-u.x0) < 3 and abs(r.y0-u.y0) < 3 for u in out):
                    out.append(r)
    return sorted(out, key=lambda r: (round(r.y0/40), r.x0))

def cluster(paths, pad=1):
    n = len(paths)
    parent = list(range(n))
    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]; i = parent[i]
        return i
    rects = [pymupdf.Rect(p['rect']) + (-pad, -pad, pad, pad) for p in paths]
    changed = True
    while changed:
        changed = False
        for i in range(n):
            for j in range(i+1, n):
                if find(i) == find(j):
                    continue
                if (rects[i] & rects[j]).get_area() > 0:
                    parent[find(i)] = find(j); changed = True
    g = {}
    for i, p in enumerate(paths):
        g.setdefault(find(i), []).append(p)
    return list(g.values())

# Temy, gde podbor zazora sklеivaet dva shaga v odin risunok.
# Klyuch: nomer stranicy shagov. Znachenie: zazor, kotoryy razdelyaet ih verno.
PAGE_PAD = {
    149: 1,   # Nave: tretiy i pyatyy shag slipalis v odnu kartinku
}


def analyze_steps_page(page, doc=None):
    dr = page.get_drawings()
    circles = find_circles(dr)
    if doc is not None:
        circles = order_circles(doc, page, circles)
    art = []
    # Verhnyaya granica. Ran'she vse vyshe 124 schitalos ukrasheniem, no u
    # nekotoryh tem risunok pervogo shaga nachinaetsya vyshe. Poetomu:
    # vybrasyvaem to, chto zadevaet lentu s nazvaniem, i to, chto celikom
    # lezhit vyshe pervogo ryada nomerov.
    rib = [pymupdf.Rect(x['rect']) for x in dr if col(x) == WHITE
           and pymupdf.Rect(x['rect']).y1 < 145
           and pymupdf.Rect(x['rect']).width > 120
           and 30 < pymupdf.Rect(x['rect']).height < 90]
    rib_box = None
    for r in rib:
        rib_box = r if rib_box is None else rib_box | r
    if rib_box is not None:
        rib_box = rib_box + (-14, -30, 14, 10)
    top_cut = min(124.0, min(c.y0 for c in circles) - 96) if circles else 124.0

    decboxes = [vec.bbox(g) for g in cluster([x for x in dr if col(x) == DEC], pad=10)] \
        if any(col(x) == DEC for x in dr) else []
    for x in dr:
        r = pymupdf.Rect(x['rect'])
        c = acol(x)
        if c is None or c == DEC:
            continue
        # a small piece sitting inside a background picture (the face of the
        # castle, a window) belongs to the background, not to a step
        if r.get_area() < 3000 and any(d.contains(r) for d in decboxes):
            continue
        if r.y0 < top_cut or r.y0 >= 748:
            continue
        if rib_box is not None and (r & rib_box).get_area() > 0.15*r.get_area():
            continue
        if r.y0 >= 748:
            continue
        if r.x0 < 6 or r.x1 > 634 or r.y1 > 800:
            continue
        if r.x1 < 135 and r.y0 > 710:
            continue
        if any((r & cc).get_area() > 0.5*r.get_area() for cc in circles):
            continue
        art.append(x)

    def make(pad):
        gs = cluster(art, pad=pad)
        return [g for g in gs if vec.bbox(g).get_area() > 300
                and not all(acol(p) == WHITE for p in g)]

    # Zazor pri otsevе kuskov po gruppam. Obychno podbiraetsya sam, no est
    # temy, gde podbor sklеivaet dva shaga v odin. Dlya nih zazor zadan.
    _fix_pad = PAGE_PAD.get(getattr(page, 'number', -1))
    if _fix_pad is not None:
        groups = make(_fix_pad)
    else:
        groups = make(1)
    if _fix_pad is None and len(groups) > len(circles):
        for pad in (4, 8, 12, 16, 20, 24):
            g2 = make(pad)
            if len(g2) == len(circles):
                groups = g2
                break
            if len(g2) < len(circles):
                break
    if _fix_pad is None and len(groups) < len(circles):
        g0 = [g for g in cluster(art, pad=0) if vec.bbox(g).get_area() > 300
              and not all(acol(p) == WHITE for p in g)]
        if len(g0) > len(groups):
            groups = g0

    def rdist(a, b):
        dx = max(b.x0-a.x1, a.x0-b.x1, 0)
        dy = max(b.y0-a.y1, a.y0-b.y1, 0)
        return (dx*dx+dy*dy)**0.5

    if circles:
        left_edge = min(c.x0 for c in circles) - 15
        groups = [g for g in groups if vec.bbox(g).x1 > left_edge]

    # a cluster that covers two rows of numbers holds two drawings: split it path by path
    def ccenter(c):
        return ((c.x0+c.x1)/2, (c.y0+c.y1)/2)

    split_groups = []
    for g in groups:
        b = vec.bbox(g)
        inside = [c for c in circles
                  if b.y0 - 20 < (c.y0+c.y1)/2 < b.y1 + 20
                  and ((c.x0+c.x1)/2 < (b.x0+b.x1)/2
                       or b.x0 - 20 < (c.x0+c.x1)/2 < b.x1 + 20)]
        rows = {round(((c.y0+c.y1)/2)/45) for c in inside}
        if len(inside) < 2 and len(rows) < 2:
            split_groups.append(g)
            continue
        buckets = {}
        for p in g:
            r = pymupdf.Rect(p['rect'])
            px, py = (r.x0+r.x1)/2, (r.y0+r.y1)/2

            def dd(c):
                cx, cy = ccenter(c)
                pen = 400 if cx > px + 8 else 0
                if cy < r.y0 - 80 or cy > r.y1 + 80:
                    pen += 200
                return ((cx-px)**2 + (cy-py)**2)**0.5 + pen
            k = min(range(len(circles)), key=lambda i: dd(circles[i]))
            buckets.setdefault(k, []).append(p)
        split_groups.extend(buckets.values())
    groups = split_groups
    boxes = [vec.bbox(g) for g in groups]

    def score(i, j):
        c, b = circles[i], boxes[j]
        ccx, bcx = (c.x0+c.x1)/2, (b.x0+b.x1)/2
        ccy = (c.y0+c.y1)/2
        pen = 250 if ccx > bcx else 0
        if ccy < b.y0 - 25 or ccy > b.y1 + 25:
            pen += 130
        return rdist(b, c) + pen

    pairs = sorted(((score(i, j), i, j) for i in range(len(circles))
                    for j in range(len(groups))), key=lambda t: t[0])
    taken_c, taken_g = set(), set()
    assign = {i: [] for i in range(len(circles))}
    main = {}
    for sc_, i, j in pairs:
        if i in taken_c or j in taken_g:
            continue
        taken_c.add(i); taken_g.add(j)
        assign[i].append(groups[j]); main[i] = boxes[j]
        if len(taken_c) == len(circles):
            break
    # leftovers: the grey part of step k+1 is exactly the whole drawing of step k,
    # so attach each stray piece where it makes those sizes agree
    def gray_bbox(i):
        ps = [p for g in assign[i] for p in g if acol(p) in (GRAY, GRAY2)]
        return vec.bbox(ps) if ps else None

    def size_gap(rect, i):
        nxt = i + 1
        if nxt not in main:
            return None
        gp = [p for g in assign[nxt] for p in g if acol(p) in (GRAY, GRAY2)]
        if not gp:
            return None
        gb = vec.bbox(gp)
        return abs(rect.width - gb.width) + abs(rect.height - gb.height)

    for j, g in enumerate(groups):
        if j in taken_g:
            continue
        best, bs = None, None
        for i in list(main):
            before = size_gap(main[i], i)
            after = size_gap(main[i] | boxes[j], i)
            gain = 60.0 if (before is None or after is None) else (after - before)
            b = boxes[j]
            cx, cy = (b.x0+b.x1)/2, (b.y0+b.y1)/2
            inside = main[i].x0 <= cx <= main[i].x1 and main[i].y0 <= cy <= main[i].y1
            sc_ = gain + 0.02*rdist(b, circles[i]) - (120 if inside else 0)
            # a drawing always sits to the right of its own number, and on the
            # same line as it: a stray piece that breaks either rule is not ours
            if (circles[i].x0 + circles[i].x1)/2 > cx + 8 and b.x1 < main[i].x0 + 8:
                sc_ += 600
            if b.y1 < main[i].y0 - 40 or b.y0 > main[i].y1 + 40:
                sc_ += 600
            if bs is None or sc_ < bs:
                best, bs = i, sc_
        if best is not None:
            assign[best].append(g)
            main[best] = main[best] | boxes[j]

    # circles left without artwork: split the nearest occupied cluster path by path
    for i in range(len(circles)):
        if i in main:
            continue
        cand = [k for k in main]
        if not cand:
            continue
        k = min(cand, key=lambda k: rdist(main[k], circles[i]))
        ps = [p for g in assign[k] for p in g]

        ci, ck = circles[i], circles[k]
        cix, ciy = (ci.x0+ci.x1)/2, (ci.y0+ci.y1)/2
        ckx, cky = (ck.x0+ck.x1)/2, (ck.y0+ck.y1)/2
        horiz = abs(cix - ckx) >= abs(ciy - cky)

        def key(p):
            r = pymupdf.Rect(p['rect'])
            return (r.x0 + r.x1)/2 if horiz else (r.y0 + r.y1)/2

        # a number circle always sits just before its own drawing,
        # so the second circle marks where the next drawing starts
        if horiz:
            first, second = (i, k) if cix < ckx else (k, i)
            cut = max(cix, ckx)
        else:
            first, second = (i, k) if ciy < cky else (k, i)
            cut = max(ciy, cky)

        def owner(p):
            return first if key(p) < cut else second

        a, b = [], []
        for p in ps:
            (a if owner(p) == i else b).append(p)
        if a and b:
            assign[i] = [a]
            assign[k] = [b]
            main[i] = vec.bbox(a)
            main[k] = vec.bbox(b)
        else:
            vals = sorted(key(p) for p in ps)
            cut2, gapmax = None, -1
            for t in range(len(vals)-1):
                g = vals[t+1] - vals[t]
                if g > gapmax:
                    gapmax, cut2 = g, (vals[t] + vals[t+1])/2
            if cut2 is not None:
                a = [p for p in ps if key(p) < cut2]
                b = [p for p in ps if key(p) >= cut2]
                if a and b:
                    assign[first] = [a]
                    assign[second] = [b]
                    main[first] = vec.bbox(a)
                    main[second] = vec.bbox(b)

    steps = []
    for i in range(len(circles)):
        ps = [p for g in assign[i] for p in g]
        steps.append((vec.bbox(ps) if ps else None, ps))
    steps = drop_strays(steps)
    steps = fix_pieces(steps, page.number, art)
    return circles, steps, art


# Redkie iskliucheniya po konkretnym stranicam knigi.
# Kluch: nomer stranicy shagov. Znachenie: levyy verhniy ugol kuska risunka
# i nomer shaga, kotoromu on na samom dele prinadlezhit.
# Delfin: hvost tretego shaga narisovan nizhe svoey kletki i popadaet v pyatuyu.
# Krome perekladki, spisok mozhet vernut kusok, kotoryy voobshche nikuda
# ne popal: takoy kusok zapisyvaetsya kak (koordinaty, nomer shaga, 'vzyat').
PIECE_OWNER = {
    89: [((258, 456), 3), ((498, 446), 4)],
    # Avion: verhniy plavnik tretego shaga narisovan vyshe svoey kletki
    # i popadal v pervyy shag
    145: [((273, 319), 3), ((278, 323), 3), ((245, 324), 3),
          ((525, 135), 2), ((557, 135), 2), ((552, 130), 2), ((558, 129), 2)],
    # KNIGA 2.
    # Pez globo: pravyy glaz pyatogo shaga poteryalsya pri razbore,
    # ryba vyhodila s odnim glazom
    113: [((254, 622), 5), ((319, 623), 5), ((333, 596), 5)],
    # Cacto: verhushka vosmogo shaga narisovana vyshe svoey kletki
    # i popadala v shestoy shag
    195: [((402, 519), 8), ((415, 522), 8), ((445, 534), 8), ((446, 553), 8),
          ((439, 569), 8), ((409, 524), 8), ((429, 525), 8), ((423, 524), 8),
          ((431, 520), 8), ((400, 543), 8)],
    # KNIGA 1 EN.
    # Unicorn: uho i chelka vtorogo shaga narisovany vyshe ego kletki,
    # pri razbore oni teryalis i shag vyhodil bez uha
    121: [((442.2, 150.2), 2), ((433.7, 143.9), 2), ((365.8, 131.1), 2)],
    # Muguete: dugu stebelka tretego shaga kniga narisovala vyshe ego kletki,
    # ona popadala v pervyy shag, a zavitok pervogo shaga uhodil v tretiy
    197: [((96, 212), 3),
          ((242, 195), 1), ((253, 194), 1), ((208, 191), 1), ((211, 193), 1),
          ((224, 193), 1), ((228, 199), 1), ((236, 195), 1)],
}


def fix_pieces(steps, page_no, art=None):
    """Perekladyvaet otdelnye kuski po spisku iskliucheniy."""
    rules = PIECE_OWNER.get(page_no)
    if not rules:
        return steps
    out = [(r, list(ps)) for r, ps in steps]
    if art:
        # kusok, poteryannyy pri razbore, vozvrashchaetsya v nuzhnyy shag
        have = {id(p) for _, ps in out for p in ps}
        for (x, y), owner in rules:
            for p in art:
                pr = pymupdf.Rect(p['rect'])
                if id(p) not in have and abs(pr.x0-x) < 3 and abs(pr.y0-y) < 3:
                    out[owner-1][1].append(p)
    for (x, y), owner in rules:
        for i, (_, ps) in enumerate(out):
            if i == owner - 1:
                continue
            for p in list(ps):
                pr = pymupdf.Rect(p['rect'])
                if abs(pr.x0 - x) < 3 and abs(pr.y0 - y) < 3:
                    out[i][1].remove(p)
                    out[owner-1][1].append(p)
    return [(vec.bbox(ps) if ps else None, ps) for _, ps in out]


def drop_strays(steps):
    """Ubiraet fon, prilipshiy k shagu (zamok, oblako).

    Razmer kazhdogo shaga izvesten po sosedyam: serye linii sleduyushchego
    shaga eto v tochnosti risunok etogo. Esli shag slishkom bolshoy, ego
    otdelnye kuski ubirayutsya po odnomu, poka razmer ne sojdetsya s tem,
    chto govoryat sosedi. Snyatyy kusok ne propadaet: on otdaetsya tomu shagu,
    gde on dovodit razmer do nuzhnogo.
    """
    n = len(steps)
    out = list(steps)
    for i in range(n):
        r, ps = out[i]
        if r is None or len(ps) < 2:
            continue
        ref = None
        if i + 1 < n and out[i+1][1]:
            gp = [p for p in out[i+1][1] if acol(p) in (GRAY, GRAY2)]
            if gp:
                ref = vec.bbox(gp)
        if ref is None and i > 0 and out[i-1][0] is not None:
            ref = out[i-1][0]
        if ref is None:
            continue
        if r.width < 1.3*ref.width and r.height < 1.3*ref.height:
            continue
        # kuski mogut stoyat vplotnuyu: probuem raznyy zazor, poka risunok
        # ne raspadetsya hotya by na dve chasti
        groups = []
        for pad in (8, 4, 2, 1, 0, -2, -5):
            groups = cluster(ps, pad=pad)
            if len(groups) >= 2:
                break
        if len(groups) < 2:
            continue
        groups.sort(key=lambda g: -vec.bbox(g).get_area())

        def gap(rect):
            return abs(rect.width - ref.width) + abs(rect.height - ref.height)

        keep = [groups[0]]
        base = vec.bbox(groups[0])
        for g in groups[1:]:
            merged = base | vec.bbox(g)
            if gap(merged) <= gap(base) + 6:
                keep.append(g)
                base = merged
        kept = [p for g in keep for p in g]
        if kept and gap(base) < gap(r) - 20:
            out[i] = (vec.bbox(kept), kept)
            for g in groups:
                if g not in keep:
                    give(out, i, g)
    return out


def _ref_size(out, i):
    """Kakogo razmera dolzhen byt shag i po slovam sosedey."""
    n = len(out)
    if i + 1 < n and out[i+1][1]:
        gp = [p for p in out[i+1][1] if acol(p) in (GRAY, GRAY2)]
        if gp:
            return vec.bbox(gp)
    if i > 0 and out[i-1][0] is not None:
        return out[i-1][0]
    return None


def give(out, i, g):
    """Otdaet snyatyy kusok tomu shagu, gde on na svoem meste."""
    b = vec.bbox(g)
    best, gain = None, 0.0
    for j in range(len(out)):
        if j == i:
            continue
        ref = _ref_size(out, j)
        r = out[j][0]
        if ref is None or r is None:
            continue

        def d(rect):
            return abs(rect.width - ref.width) + abs(rect.height - ref.height)

        win = d(r) - d(r | b)
        if win > gain:
            best, gain = j, win
    if best is not None and gain > 20:
        ps = out[best][1] + list(g)
        out[best] = (vec.bbox(ps), ps)


_REFS = None
_DR = {}


def _page_drawings(page):
    k = id(page.parent), page.number
    if k not in _DR:
        _DR[k] = page.get_drawings()
    return _DR[k]


def digit_thumb(page, c, n=26):
    """Render only the digit inside a number circle, normalised by its own bbox."""
    import numpy as np
    dr = _page_drawings(page)
    box = pymupdf.Rect(c) + (-1.5, -1.5, 1.5, 1.5)
    inner = [x for x in dr
             if box.contains(pymupdf.Rect(x['rect']))
             and x['rect'].width < 0.55*c.width
             and x['rect'].height < 0.85*c.height]
    if not inner:
        return np.ones((n, n))
    b = vec.bbox(inner)
    doc = pymupdf.open()
    pg = doc.new_page(width=n, height=n)
    pad = 2.0
    sc = (n - 2*pad) / b.height
    w = b.width * sc
    m = pymupdf.Matrix(sc, 0, 0, sc, (n - w)/2 - b.x0*sc, pad - b.y0*sc)
    vec.replay2(pg, inner, m, fill=(0, 0, 0), color=None)
    pix = pg.get_pixmap(colorspace=pymupdf.csGRAY, alpha=False)
    a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width).astype(float)
    return a[:n, :n] / 255.0


def _build_refs(doc):
    global _REFS
    if _REFS is not None:
        return _REFS
    _REFS = {}
    for pno, take in ((9, range(6)), (47, range(6, 8)), (185, range(8, 9))):
        page = doc[pno]
        cs = sorted(find_circles(_page_drawings(page)), key=lambda r: (round(r.y0/40), r.x0))
        for i in take:
            if i < len(cs):
                _REFS[i+1] = digit_thumb(page, cs[i])
    return _REFS


def order_circles(doc, page, circles):
    """Sort circles by the digit inside; drop false positives and duplicates."""
    import numpy as np
    refs = _build_refs(doc)
    best = {}
    for c in circles:
        t = digit_thumb(page, c)
        sc = {k: float(np.abs(refs[k] - t).sum()) for k in refs}
        d = min(sc, key=sc.get)
        if d not in best or sc[d] < best[d][0]:
            best[d] = (sc[d], c)
    out = []
    for d in sorted(best):
        if d != len(out) + 1:
            break
        out.append(best[d][1])
    return out


def dash_kind(paths):
    """Punktirom narisovana gruppa ili sploshnoy liniey."""
    n = sum(1 for p in paths if (p.get('dashes') or '').strip('[] 0'))
    return n * 2 >= len(paths)


# Tochechnyy vozvrat poteryannyh kuskov figury dlya obvodki.
# Klyuch: nomer stranicy s figuroy. Znachenie: pryamougolniki kuskov.
TRACE_KEEP = {
    114: [(400, 167, 424, 191)],   # Pufferfish: vtoroy glaz teryalsya
}


def trace_paths(page):
    dr = page.get_drawings()
    best_ps, best_area = [], -1
    for c in (GRAY, GRAY2):
        ps = [x for x in dr if acol(x) == c]
        if not ps:
            continue
        gs = cluster(ps, pad=6)
        gs.sort(key=lambda g: vec.bbox(g).get_area(), reverse=True)
        area = vec.bbox(gs[0]).get_area()
        if area > best_area:
            best_area, best_ps = area, gs
    if not best_ps:
        return []
    main = vec.bbox(best_ps[0])
    keep = list(best_ps[0])
    for g in best_ps[1:]:
        b = vec.bbox(g)

        def near(r1, r2):
            dx = max(r2.x0-r1.x1, r1.x0-r2.x1, 0)
            dy = max(r2.y0-r1.y1, r1.y0-r2.y1, 0)
            return (dx*dx+dy*dy)**0.5

        dmin = min(near(b, pymupdf.Rect(p['rect'])) for p in best_ps[0])
        if dmin < 6 or b.get_area() > 0.3*main.get_area():
            keep.extend(g)
    # melkie oblomki v storone ot figury eto ukrasheniya stranicy, a ne risunok.
    # Sobiraem ostavsheesya zanovo s malenkim zazorom i derzhim tolko to,
    # chto libo primykaet k figure, libo samo po sebe krupnoe.
    gs = cluster(keep, pad=1)
    if len(gs) > 1:
        gs.sort(key=lambda g: -vec.bbox(g).get_area())
        body = vec.bbox(gs[0])

        def gap(r1, r2):
            dx = max(r2.x0-r1.x1, r1.x0-r2.x1, 0)
            dy = max(r2.y0-r1.y1, r1.y0-r2.y1, 0)
            return (dx*dx+dy*dy)**0.5

        # gabarit vsey figury: vse chto lezhit gluboko vnutri nego eto sama
        # figura, a ne ukrashenie stranicy. Ukrasheniya stoyat sboku i kraem
        # vyhodyat naruzhu. Bez etogo u alpaki propadala chelka i brovi.
        whole = vec.bbox(keep)
        inside = pymupdf.Rect(whole.x0 + 6, whole.y0 + 6, whole.x1 - 6, whole.y1 - 6)

        out = list(gs[0])
        for g in gs[1:]:
            b = vec.bbox(g)
            if b.x0 >= inside.x0 and b.y0 >= inside.y0 and \
               b.x1 <= inside.x1 and b.y1 <= inside.y1:
                out.extend(g)
                continue
            # rasstoyanie meryaem do samih linij figury, a ne do ee ramki:
            # inache oblomok sboku schitaetsya prilezhashchim
            dmin = min(gap(pymupdf.Rect(p['rect']), b) for p in gs[0])
            # figura dlya obvodki narisovana punktirom. Kusok bez punktira
            # ryadom s ney eto ukrashenie stranicy, ego ne berem
            same_dash = (dash_kind(g) == dash_kind(gs[0]))
            if same_dash and (dmin < 8 or b.get_area() > 0.05*body.get_area()):
                out.extend(g)
        return _trace_add(page, dr, out)
    return _trace_add(page, dr, keep)


def _trace_add(page, dr, out):
    """Vozvrashchaet kuski, perechislennye v TRACE_KEEP, esli otsev ih vybrosil."""
    boxes = TRACE_KEEP.get(page.number)
    if not boxes:
        return out
    have = [pymupdf.Rect(p['rect']) for p in out]
    for bx in boxes:
        box = pymupdf.Rect(*bx)
        for x in dr:
            r = pymupdf.Rect(x['rect'])
            if r in box and not any(abs(r.x0-u.x0) < 0.5 and abs(r.y0-u.y0) < 0.5
                                    for u in have):
                out.append(x)
    return out
