"""Listy legkogo urovnya: v pole risovaniya stoit seraya osnova, a v ryadu
naverhu ostayutsya tolko te shagi, kotorye rebenku eshche predstoit sdelat.
Nomera kartochek nachinayutsya s edinicy."""
import pymupdf, build as B, shablon, detect, vec, proba
from vec import fit, bbox

TONE = (0.576, 0.576, 0.576)   # na 20 procentov temnee prezhnego 0.72


def ordered(doc, spi):
    """Shagi v poryadke risovaniya, so sdvigami, kak eto delaet shablon:
    snachala perestanovka, potom sovmeshchenie, i tolko potom vybros lishnih."""
    circles, steps, _ = detect.analyze_steps_page(doc[spi], doc)
    steps = B.ochistit(spi, steps)
    o = B.STEP_ORDER.get(spi)
    if o and len(o) == len(steps):
        steps = [steps[j-1] for j in o]
    # vazhno: shablon vybrasyvaet shagi po MESTU v uzhe perestavlennom ryadu,
    # a ne po nomeru iz knigi. Poetomu i zdes schet vedetsya po mestam, inache
    # u mashiny i edinoroga v pole stanovitsya odin risunok, a pervoy
    # kartochkoy pokazyvaetsya sovsem drugoy.
    idx = list(range(1, len(steps) + 1))
    offs, fr, ok = proba.align(steps)
    d = B.DROP_STEPS.get(spi)
    if d:
        keep = [i for i, j in enumerate(idx) if j not in d]
        steps = [steps[i] for i in keep]
        offs = [offs[i] for i in keep]
        idx = [idx[i] for i in keep]
    return steps, offs, idx


def base_matrix(doc, spi, steps, offs):
    """Geroy v pole toy zhe velichiny, chto i punktirnyy risunok sleva.
    Schitaetsya po gotovoy figure, a ne po masshtabu istochnika."""
    trace = detect.trace_paths(doc[spi+1])
    tb = bbox(trace)
    tr = tb * fit(tb, shablon.TRACE_RECT)
    fin = pymupdf.Rect(steps[-1][0]) + (offs[-1].x, offs[-1].y,
                                        offs[-1].x, offs[-1].y)
    s = min(tr.width / fin.width, tr.height / fin.height)
    fcx, fcy = (fin.x0 + fin.x1) / 2, (fin.y0 + fin.y1) / 2
    pcx = (proba.FRAME.x0 + proba.FRAME.x1) / 2
    pcy = (proba.FRAME.y0 + proba.FRAME.y1) / 2
    return (pymupdf.Matrix(1, 0, 0, 1, -fcx, -fcy)
            * pymupdf.Matrix(s, 0, 0, s, 0, 0)
            * pymupdf.Matrix(1, 0, 0, 1, pcx, pcy))


def kusochki(p):
    """Razbivaet put na otdelnye kusochki: tam, gde liniya obryvaetsya i
    nachinaetsya zanovo. Vozvrashchaet razmer kazhdogo kusochka po diagonali."""
    out, prev = [], None
    for it in p['items']:
        if it[0] == 'l':
            pts = [pymupdf.Point(it[1]), pymupdf.Point(it[2])]
        elif it[0] == 'c':
            pts = [pymupdf.Point(it[i]) for i in (1, 2, 3, 4)]
        else:
            prev = None
            continue
        a0, b0 = pts[0], pts[-1]
        if prev is None or abs(a0 - prev) > 0.6:
            out.append([a0.x, a0.y, a0.x, a0.y])
        box = out[-1]
        for q in pts:
            box[0] = min(box[0], q.x); box[1] = min(box[1], q.y)
            box[2] = max(box[2], q.x); box[3] = max(box[3], q.y)
        prev = b0
    return [((x1-x0)**2 + (y1-y0)**2) ** 0.5 for x0, y0, x1, y1 in out]


def punktir(p, fig):
    """Punktirnaya liniya-podskazka iz knigi. Uznaetsya po dvum priznakam
    srazu: liniya razorvana na neskolko kusochkov, i kazhdyy kusochek kroshechnyy
    ryadom s figuroy. Zavitok shersti u alpaki eto odna nepreryvnaya liniya, a
    klyuv kolibri hot i razorvan, no kusochki u nego bolshie. V gotovom risunke
    podskazok net, i v osnovu oni popadat ne dolzhny: rebenok obvel by ih."""
    ks = kusochki(p)
    if len(ks) < 2:
        return False
    D = (fig.width**2 + fig.height**2) ** 0.5
    if D <= 0:
        return False
    big = max(ks)
    return len(ks) >= 3 and big < 0.09 * D


def sheet(out, doc, spi, name, png, page_no, start):
    """start - s kakogo shaga nachinaetsya legkiy uroven, schet po poryadku
    risovaniya posle perestanovki i vybrosa."""
    steps, offs, idx = ordered(doc, spi)
    old = B.DROP_STEPS.get(spi)
    drop = sorted(set(list(old or []) + idx[:start-1]))
    B.DROP_STEPS[spi] = drop
    try:
        shablon.sheet(out, doc, spi, name, png, page_no=page_no)
    finally:
        if old is None:
            B.DROP_STEPS.pop(spi, None)
        else:
            B.DROP_STEPS[spi] = old
    pg = out[-1]
    m = base_matrix(doc, spi, steps, offs)
    k = start - 1
    fig = pymupdf.Rect(steps[-1][0])
    ps = [p for p in steps[k][1] if not punktir(p, fig)]
    proba.draw_gray(pg, ps,
                    pymupdf.Matrix(1, 0, 0, 1, offs[k].x, offs[k].y) * m, TONE)


def podpis(pg, text, razmer=13.5):
    """Podpis urovnya v pravom verhnem uglu lista. Otstup ot kraya takoy zhe,
    kak sleva u slova Name."""
    f = pymupdf.Font(fontfile='f/Quicksand-Bold.ttf')
    w = f.text_length(text, razmer)
    tw = pymupdf.TextWriter(pg.rect)
    tw.append((588 - w, 42), text, font=f, fontsize=razmer)
    tw.write_text(pg, color=(0.45, 0.45, 0.45))
