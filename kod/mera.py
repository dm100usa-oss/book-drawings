import os
import pymupdf, detect, vec, build as B, json

def seglen(items):
    t = 0.0
    for it in items:
        k = it[0]
        if k == 'l':
            t += abs(pymupdf.Point(it[1]) - pymupdf.Point(it[2]))
        elif k == 'c':
            pts = [pymupdf.Point(it[i]) for i in (1, 2, 3, 4)]
            prev = pts[0]
            for i in range(1, 9):
                u = i / 8.0
                x = ((1-u)**3*pts[0].x + 3*(1-u)**2*u*pts[1].x
                     + 3*(1-u)*u*u*pts[2].x + u**3*pts[3].x)
                y = ((1-u)**3*pts[0].y + 3*(1-u)**2*u*pts[1].y
                     + 3*(1-u)*u*u*pts[2].y + u**3*pts[3].y)
                p = pymupdf.Point(x, y); t += abs(p - prev); prev = p
        elif k == 're':
            r = pymupdf.Rect(it[1]); t += 2*(r.width + r.height)
        elif k == 'qu':
            q = it[1]
            t += abs(q.ul-q.ur)+abs(q.ur-q.lr)+abs(q.lr-q.ll)+abs(q.ll-q.ul)
    return t

def ink(paths):
    s = 0.0
    for p in paths:
        f = p.get('fill')
        if f is not None and min(f) > 0.95 and p.get('color') is None:
            continue
        s += seglen(p['items'])
    return s

def coverage(doc, spi):
    """Doli gotovogo risunka po shagam, uzhe s uchetom perestanovki i vybroshennyh
    shagov. Vozvrashchaet spisok doley i spisok ishodnyh nomerov shagov."""
    circles, steps, _ = detect.analyze_steps_page(doc[spi], doc)
    idx = list(range(1, len(steps)+1))
    o = B.STEP_ORDER.get(spi)
    if o and len(o) == len(steps):
        steps = [steps[j-1] for j in o]
        idx = o[:]
    d = B.DROP_STEPS.get(spi)
    if d:
        keep = [i for i, j in enumerate(idx) if j not in d]
        steps = [steps[i] for i in keep]
        idx = [idx[i] for i in keep]
    tot = ink(steps[-1][1]) or 1
    return [ink(s[1])/tot for s in steps], idx

if __name__ == '__main__':
    import os
    doc = pymupdf.open(B.SRC)
    res = {}
    for spi, name in B.THEMES:
        fr, idx = coverage(doc, spi)
        res[str(spi)] = {'name': name, 'fr': fr, 'idx': idx}
        print(f'{name:22s} {len(fr)} shagov  ' + ' '.join(f'{v*100:4.0f}' for v in fr), flush=True)
    json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mera%d.json' % B.BOOK), 'w'))
