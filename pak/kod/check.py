import pymupdf, detect, vec, build as B
doc = pymupdf.open(B.SRC)
for spi, name in B.THEMES:
    c, steps, _ = detect.analyze_steps_page(doc[spi], doc)
    ws = [round(r.width) if r else 0 for r, _ in steps]
    hs = [round(r.height) if r else 0 for r, _ in steps]
    ns = [len(p) for _, p in steps]
    flag = []
    if any(n == 0 for n in ns): flag.append('EMPTY')
    mw, mh = max(ws), max(hs)
    # step sizes must not shrink after growing much / final should be largest-ish
    if ws[-1] < 0.8*mw or hs[-1] < 0.8*mh: flag.append('LAST-SMALL')
    for k in range(1, len(steps)):
        if ws[k] < ws[k-1]-6 or hs[k] < hs[k-1]-6: flag.append(f'SHRINK@{k+1}')
    # gray of step k should equal whole drawing of k-1
    for k in range(1, len(steps)):
        gp = [p for p in steps[k][1] if vec.col(p) in (vec.GRAY, vec.GRAY2)]
        if not gp: flag.append(f'NOGRAY@{k+1}'); continue
        a = vec.bbox(gp); prev = steps[k-1][0]
        if abs(a.width-prev.width) > 0.08*max(a.width, prev.width)+4 or \
           abs(a.height-prev.height) > 0.08*max(a.height, prev.height)+4:
            flag.append(f'MISMATCH@{k+1}')
    print(f'{name:16s} n={len(c)} {"; ".join(flag) if flag else "ok"}')
