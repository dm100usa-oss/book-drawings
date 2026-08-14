# -*- coding: utf-8 -*-
"""SHABLON LISTA. Odna raskladka na vse knigi.

Vse razmery i polozheniya bloka zdes. Kartinka-podlozhka (pejzazh s lentoy
i nazvaniem) peredaetsya otdelno, poetomu odin i tot zhe shablon goditsya
dlya lyuboy serii: Afrika, more, fantaziya i tak dalee.

Ispolzovanie:
    import shablon
    shablon.sheet(out_doc, book_doc, spi, name, overlay_png, page_no)
"""
import pymupdf, vec, detect, parts, skel
import build as B
from vec import fit, bbox, replay, replay2

W, H = 612.0, 792.0
SY0, SY1 = 176.0, 316.0    # polosa shagov
VD = 202.0                 # granica mezhdu obvodkoy i polem risovaniya
LY1 = 702.0                # nizhnyaya linejka propisi
TRACE_RECT = pymupdf.Rect(16, 398, 198, 602)    # figura dlya obvodki
DRAW_RECT = pymupdf.Rect(212, 360, 597, 628)    # pole dlya risovaniya
FIG_RECT = pymupdf.Rect(498, 642, 602, 732)     # gotovaya figura vnizu sprava
GROUND_Y = 688.0           # otsyuda vniz idet zemlya: ona kladetsya poverh figury
PAGENO_XY = (W/2, 763.0)   # kameshek s nomerom stranicy
PAGENO_R = 17.0
# vnutrennee beloe pole lenty na podlozhke: syuda stavitsya nazvanie iz knigi
RIBBON = None              # esli None, beloe pole lenty ishchetsya samo
TITLE_H = 38.0             # vysota bukv nazvaniya


_RIB = {}


def ribbon_rect(overlay):
    """Nahodit beloe pole vnutri lenty na lyuboy podlozhke."""
    if overlay in _RIB:
        return _RIB[overlay]
    import numpy as np
    from PIL import Image
    from skimage import measure
    a = np.array(Image.open(overlay))
    gray = a[:, :, :3].mean(axis=2)
    if a.shape[2] == 4:
        ink = (a[:, :, 3] > 40) & (gray < 160)
    else:
        ink = gray < 160
    h, w = ink.shape
    from skimage.morphology import closing, disk
    top = closing(ink[:int(h * 0.32)], disk(3))
    lab = measure.label(~top)
    best = None
    for r in measure.regionprops(lab):
        y0, x0, y1, x1 = r.bbox
        if x0 == 0 or y0 == 0 or x1 >= top.shape[1] or y1 >= top.shape[0]:
            continue          # eto fon vokrug, a ne dyrka vnutri lenty
        if r.area < 20000:
            continue
        if best is None or r.area > best.area:
            best = r
    if best is None:
        raise ValueError('ne nashel lentu na podlozhke ' + overlay)
    y0, x0, y1, x1 = best.bbox
    k = W / w
    # vysotu polya berem po seredine lenty: u izognutoy lenty kraya uhodyat
    # vniz, i esli schitat po vsey shirine, nazvanie saditsya slishkom nizko
    mid = ink[:int(h * 0.32)]
    cx0, cx1 = int((x0 + x1) / 2 - (x1 - x0) * 0.15), int((x0 + x1) / 2 + (x1 - x0) * 0.15)
    tops, bots = [], []
    for x in range(cx0, cx1, max(1, (cx1 - cx0) // 40)):
        col = np.where(mid[:, x])[0]
        col = col[(col > y0 - 40) & (col < y1 + 40)]
        if len(col) < 2:
            continue
        runs = np.split(col, np.where(np.diff(col) > 3)[0] + 1)
        if len(runs) < 2:
            continue
        tops.append(runs[0].max())
        bots.append(runs[-1].min())
    if tops and bots:
        y0 = float(np.median(tops))
        y1 = float(np.median(bots))
    rect = pymupdf.Rect(x0 * k + 4, y0 * k + 3, x1 * k - 4, y1 * k - 3)
    _RIB[overlay] = rect
    return rect


def sheet(out, doc, spi, name, overlay, page_no=None):
    """Sobiraet odin gotovyy list i vozvrashchaet ego."""
    sp, pp = doc[spi], doc[spi + 1]
    pg = out.new_page(width=W, height=H)
    pg.insert_image(pymupdf.Rect(0, 0, W, H), filename=overlay)

    # nazvanie beretsya gotovym risunkom bukv iz knigi i stavitsya v lentu
    tpaths = parts.title_paths(sp)
    if tpaths:
        tb = bbox(tpaths)
        rib = RIBBON if RIBBON is not None else ribbon_rect(overlay)
        k = min(TITLE_H / tb.height, (rib.width - 26) / tb.width)
        w2, h2 = tb.width * k, tb.height * k
        cx2, cy2 = (rib.x0 + rib.x1) / 2, (rib.y0 + rib.y1) / 2
        replay2(pg, tpaths,
                fit(tb, pymupdf.Rect(cx2 - w2/2, cy2 - h2/2, cx2 + w2/2, cy2 + h2/2)),
                fill=B.BLACK)
    circles, steps, _ = detect.analyze_steps_page(sp, doc)
    # u neskolkih tem v knige shagi pronumerovany ne v tom poryadke,
    # v kakom risuetsya figura: takie temy perestavlyayutsya po spisku
    _ord = B.STEP_ORDER.get(spi)
    if _ord and len(_ord) == len(steps):
        steps = [steps[j-1] for j in _ord]
    # slishkom melkie shagi ubirayutsya, chtoby ostalnye stali krupnee
    _drop = B.DROP_STEPS.get(spi)
    if _drop:
        steps = [s for k, s in enumerate(steps) if k+1 not in _drop]
    cpaths = parts.circle_paths(sp, circles)
    trace = detect.trace_paths(pp)
    low, art = name.lower(), B.article(name)

    # --- shagi: obshchiy masshtab i sovmeshchenie, kak v osnovnom liste ---
    # ---- steps: common scale, figure registered so it never jumps ----
    n = len(steps)
    gap = 5.0
    bw = (B.MX1 - B.MX0 - gap*(n-1)) / n
    inner_w = bw - 14
    inner_h = (SY1 - SY0) - 34

    # grey paths of step k are exactly the whole drawing of step k-1
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
            # the grey lines of this step are the previous drawing; line the two
            # up by their centres, so a step stays put even where the book
            # redrew the figure at a slightly different size
            d = pymupdf.Point((prev.x0 + prev.x1)/2 - (a.x0 + a.x1)/2,
                              (prev.y0 + prev.y1)/2 - (a.y0 + a.y1)/2)
            offs.append(offs[k-1] + d)
        else:
            ok = False
            offs.append(offs[k-1] + pymupdf.Point(prev.x0 - cur.x0, prev.y0 - cur.y0))

    frame = None
    placed = []
    for k, (r, ps) in enumerate(steps):
        pr = pymupdf.Rect(r) + (offs[k].x, offs[k].y, offs[k].x, offs[k].y)
        placed.append(pr)
        frame = pr if frame is None else frame | pr
    mw = max(r.width for r, _ in steps)
    mh = max(r.height for r, _ in steps)
    if not ok or frame.width > 1.45*mw or frame.height > 1.45*mh:
        placed = [pymupdf.Rect((mw-r.width)/2, 0, (mw+r.width)/2, r.height) for r, _ in steps]
        frame = pymupdf.Rect(0, 0, mw, mh)
        offs = [pymupdf.Point(placed[k].x0 - steps[k][0].x0,
                              placed[k].y0 - steps[k][0].y0) for k in range(n)]

    _sh = B.STEP_SHIFT.get(spi)
    if _sh:
        # ruchnaya popravka: otdelnye shagi opuskayutsya, chtoby figura stoyala
        # na odnoy vysote vo vseh kletkah
        for _i, _dy in _sh.items():
            offs[_i-1] = offs[_i-1] + pymupdf.Point(0, _dy)
        frame = None
        for k, (r, ps) in enumerate(steps):
            pr = pymupdf.Rect(r) + (offs[k].x, offs[k].y, offs[k].x, offs[k].y)
            frame = pr if frame is None else frame | pr

    import math
    ang, s = 0.0, min(inner_w/frame.width, inner_h/frame.height)
    for a in range(5, 50, 5):
        t = math.radians(a)
        rw = frame.width*math.cos(t) + frame.height*math.sin(t)
        rh = frame.width*math.sin(t) + frame.height*math.cos(t)
        sa = min(inner_w/rw, inner_h/rh)
        if sa > s*1.001:
            ang, s = float(a), sa
    if ang and s < 1.30*min(inner_w/frame.width, inner_h/frame.height):
        ang, s = 0.0, min(inner_w/frame.width, inner_h/frame.height)
    fcx, fcy = (frame.x0+frame.x1)/2, (frame.y0+frame.y1)/2

    for i, (r, ps) in enumerate(steps):
        bx = B.MX0 + i*(bw+gap)
        box = pymupdf.Rect(bx, SY0, bx+bw, SY1)
        pg.draw_rect(box, color=B.BLACK, width=1.2, radius=0.07)
        if ps:
            bcx = bx + bw/2
            bcy = SY0 + 27 + inner_h/2
            m = (pymupdf.Matrix(1, 0, 0, 1, offs[i].x - fcx, offs[i].y - fcy)
                 * pymupdf.Matrix(ang)
                 * pymupdf.Matrix(s, 0, 0, s, 0, 0)
                 * pymupdf.Matrix(1, 0, 0, 1, bcx, bcy))
            replay(pg, ps, m)
        cb = pymupdf.Rect(circles[i])
        replay(pg, cpaths[i], fit(cb, pymupdf.Rect(bx+5, SY0+5, bx+25, SY0+25)))

    # stroka dlya imeni v samom verhu sleva
    B.txt(pg, 24, 42, u'Nombre:', B.FB, 12.5, color=B.BLACK)
    _nx = 24 + B.FB.text_length(u'Nombre:', 12.5) + 8
    # liniya dlya imeni: punktirnaya i na 20 procentov svetlee chernogo
    B.dashed_line(pg, _nx, 44, _nx + 145, 44, color=(0.2, 0.2, 0.2),
                  width=1, d="[4 3] 0")
    B.txt(pg, 0, 168, f'Sigue los pasos para dibujar {B.article(name)} {name.lower()}.',
          B.FB, 13, center=W/2)
    B.dashed_line(pg, B.MX0, 328, B.MX1, 328)
    B.txt(pg, 0, 348, f'Repasa {art} {low}.', B.FB, 13, center=(B.MX0 + VD) / 2)
    # mezhdu dvumya predlozheniyami stavitsya zametnyy probel, inache oni
    # slivayutsya v odnu strochku
    B.txt(pg, 0, 348, u'\u00a1Ahora te toca a ti!' + u'\u00a0' * 5 + f'Dibuja {art} {low} t\u00fa solo.',
          B.FB, 13, center=(VD + B.MX1) / 2)
    # vertikalnaya cherta mezhdu zonami ubrana: ramka risovaniya uzhe delit list
    # B.dashed_line(pg, VD, 332, VD, 632)
    if trace:
        _m = fit(bbox(trace), TRACE_RECT)
        # figura stala menshe, poetomu shtrihi utonchilis: vozvrashchaem im
        # prezhnyuyu tolshchinu, obvodya kazhdyy shtrih ego zhe cvetom
        _k = (_m.a**2 + _m.b**2) ** 0.5      # vo skolko raz figura umenshilas
        for _p in trace:
            # figura, zalitaya belym s seroy obvodkoy, risuetsya cvetom obvodki
            _d = _p.get('dashes')
            if _d and _d.strip('[] 0'):
                # punktir iz knigi sohranyaetsya i szhimaetsya vmeste s figuroy
                _nums = [float(v) * _k for v in _d[_d.index('[')+1:_d.index(']')].split()]
                _d = '[' + ' '.join('%.2f' % v for v in _nums) + '] 0'
            else:
                _d = None
            # tolshchina shtriha beretsya svoya, umenshennaya vmeste s figuroy,
            # chtoby obvodka vyglyadela tak zhe, kak na etalonnom liste so lvom
            _w = _p.get('width') or 0
            _w = _w * _k + 0.55 if _w else 0.55
            # cvet zatemnyaetsya tak zhe, kak u vseh seryh linij knigi,
            # inache figura vyhodit svetlee, chem na etalonnom liste
            replay2(pg, [_p], _m, color=vec.grayer(detect.acol(_p)),
                    width=_w, dashes=_d)
    pg.draw_rect(DRAW_RECT, color=(0.75, 0.75, 0.75), width=1.2, radius=0.04)

    # --- propis nad nizhney polosoy ---
    head1 = u'Repasa y escribe la palabra '
    w1 = B.FH.text_length(head1, 14)
    w2 = B.FH.text_length(name, 18)
    hx = (B.LX0 + B.LX1) / 2 - (w1 + w2) / 2
    B.txt(pg, hx, 650, head1, B.FH, 14, color=(0.45, 0.45, 0.45))
    B.txt(pg, hx + w1, 650, name, B.FH, 18)

    polys, capH, ascH, xH, adv = skel.text_polylines(name, B.TRACE_FONT)
    sc = B.ROW / capH
    word_w = adv * sc
    # rebenku nuzhno mesto dlya pisma ne menshe, chem zanimaet samo slovo.
    # esli slovo dlinnoe, bukvy umenshayutsya, poka obe zony ne stanut ravny.
    MAXW = 175.0
    # Esli slovo vlezaet v polstroki hotya by s rostom bukv 26, delim stroku
    # popolam: sleva obvodka, sprava mesto dlya pisma. Esli net, bukvy stali
    # by slishkom melkimi, i togda vsya stroka idet pod obvodku.
    MIN_H = 26.0
    dlinnoe = word_w > MAXW * B.ROW / MIN_H
    if not dlinnoe and word_w > MAXW:
        sc *= MAXW / word_w
        word_w = MAXW
    if dlinnoe:
        # Slovo ne pomeshchaetsya dvazhdy v odnu stroku. Melkie bukvy rebenok
        # ne obvedet, poetomu vsya stroka otdaetsya pod obvodku, bez deleniya.
        full = (B.LX1 - B.LX0) - 44
        if word_w > full:
            sc *= full / word_w
            word_w = full
        z1 = (B.LX0, B.LX1)
        z2 = None
        vsp = None
    else:
        # zapas po bokam ot slova do kraev zony, chtoby bukvy ne upiralis
        z1w = max(140.0, word_w + 52)
        z1 = (B.LX0, B.LX0 + z1w)
        vsp = z1[1] + 9
        z2 = (vsp + 9, B.LX1)
    ly0 = LY1 - capH * sc
    lym = (ly0 + LY1) / 2.0
    for (a, b) in ([z1] if z2 is None else [z1, z2]):
        pg.draw_line((a, ly0), (b, ly0), color=B.BLACK, width=1.2)
        B.manual_dashes(pg, a, b, lym, B.LX0)
        pg.draw_line((a, LY1), (b, LY1), color=B.BLACK, width=1.2)
    if vsp is not None:
        B.dashed_line(pg, vsp, ly0 - 4, vsp, LY1 + 4, color=B.BLACK, width=1.0,
                      d="[5 5] 0")
    wx = (z1[0] + z1[1]) / 2 - word_w / 2
    sh = pg.new_shape()
    for p in polys:
        sh.draw_polyline([pymupdf.Point(wx + x * sc, LY1 - y * sc) for (x, y) in p])
    # tolshchina osevoy linii idet za rostom bukv: u melkih bukv tonshe,
    # inache u nih zatyagivayutsya dyrki
    tw = max(1.05, 2.6 * (capH * sc) / B.ROW)
    sh.finish(color=(0.225, 0.225, 0.225), width=tw, dashes="[2.3 1.75] 0", closePath=False)
    sh.commit()

    # gotovyy risunok v uglu, stoit na trave
    fr, fps = steps[-1]
    if fps:
        _fx = B.FIG_FIX.get(spi)
        _rect = FIG_RECT
        if _fx:
            _k = _fx[0]
            _cx = (_rect.x0+_rect.x1)/2
            _w, _h = _rect.width*_k/2, _rect.height*_k/2
            if _cx + _w > 602:          # ne vylezat za pravyy kray lista
                _cx = 602 - _w
            _rect = pymupdf.Rect(_cx-_w, _rect.y1-_h*2, _cx+_w, _rect.y1)
        m = fit(fr, _rect)
        if _fx and _fx[1]:
            # razvorot: figura smotrit v druguyu storonu
            _cx = (_rect.x0 + _rect.x1) / 2
            m = m * pymupdf.Matrix(-1, 0, 0, 1, 2*_cx, 0)
        _k = vec.mscale(m)          # vo skolko raz figura umenshilas
        for p in fps:
            # cvet beretsya po obvodke, esli zalivka belaya: inache figura,
            # zalitaya belym s seroy obvodkoy, ostaetsya seroy (gamepads)
            c = detect.acol(p)
            _w = (p.get('width') or 0) * _k
            if c in (vec.GRAY, vec.GRAY2):
                if vec.col(p) == vec.WHITE:
                    # belaya zalivka sohranyaetsya, ona zakryvaet lishnee,
                    # a obvodka stanovitsya chernoy
                    replay2(pg, [p], m, fill=(1, 1, 1), color=B.BLACK, width=_w)
                elif p.get('fill') is not None:
                    replay2(pg, [p], m, fill=B.BLACK, color=None)
                else:
                    # tolshchina linii umenshaetsya vmeste s figuroy. Inache
                    # u morskih tem, gde risunok zadan obvodkoy, linii
                    # ostayutsya knizhnoy tolshchiny i figura vyhodit gryaznoy
                    replay2(pg, [p], m, color=B.BLACK, width=_w)
            else:
                replay(pg, [p], m)

    # trava kladetsya poverh lva: on stoit za nej
    from PIL import Image as _IM
    _ov = _IM.open(overlay)
    _y0px = int(GROUND_Y / H * _ov.height)
    _bot = '/tmp/ov_bottom.png'
    _ov.crop((0, _y0px, _ov.width, _ov.height)).save(_bot)
    pg.insert_image(pymupdf.Rect(0, GROUND_Y, W, H), filename=_bot)

    # nomer stranicy: kameshek vnizu po centru
    PAGENO = str(page_no) if page_no is not None else ''
    _cx, _cy = PAGENO_XY
    _r = PAGENO_R
    sh = pg.new_shape()
    sh.draw_oval(pymupdf.Rect(_cx-_r*1.15, _cy-_r, _cx+_r*1.15, _cy+_r))
    sh.finish(color=B.BLACK, fill=(1, 1, 1), width=1.6)
    sh.commit()
    B.txt(pg, 0, _cy+5.5, PAGENO, B.FB, 16, center=_cx)


    return pg
