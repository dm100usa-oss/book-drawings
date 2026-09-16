import sys; sys.path.insert(0, '/home/claude/work')
import numpy as np, os
from story import *
from layout_cfg import CFG
from reportlab.pdfgen import canvas

CACHE = '/home/claude/work/pages'
SIZES = (16, 15)
os.makedirs(CACHE, exist_ok=True)

def page_jpeg(p_old):
    path = f'{CACHE}/src_{p_old}.jpg'
    if not os.path.exists(path):
        img, kind = extend_top(page_source(p_old))
        img.save(path, quality=94, subsampling=0, dpi=(300, 300))
    return path

def draw_story(c, p_old, report):
    path = page_jpeg(p_old)
    c.drawImage(path, 0, 0, PAGE_W, PAGE_H)
    groups = CFG.get(p_old, [])
    if not groups:
        return
    img = Image.open(path)
    arr = np.asarray(img).astype(float)
    left = (p_old % 2 == 0)
    dx0, dx1 = (200, 2390) if left else (198, 2388)
    for g in groups:
        x0 = g['x0'] if g['x0'] is not None else dx0
        x1 = g['x1'] if g['x1'] is not None else dx1
        ex0, ex1 = g.get('es_x') or (x0, x1)
        width_pt = (x1 - x0) / PX * 72
        width_es = (ex1 - ex0) / PX * 72
        region = arr[g['y0']:g['y1'], x0:x1].reshape(-1, 3).mean(0)
        es_col = ES_SKY if (region[2] - region[0]) > 40 else ES_WHITE
        placed = False
        for size in SIZES:
            items, total = layout(g['frags'], width_pt, size, es_col, width_es)
            need = total / 72 * PX
            free = g['y1'] - g['y0']
            if need <= free:
                if g['align'] == 'center' or free - need <= 400:
                    top_px = g['y0'] + (free - need) / 2
                elif g['align'] == 'top0':
                    top_px = g['y0']
                else:
                    top_px = g['y0'] + 160
                y = PAGE_H - top_px / PX * 72
                for fl, gap, h, lang in items:
                    y -= gap
                    xx = (x0 if lang == 'en' else ex0) / PX * 72
                    fl.drawOn(c, xx, y - h)
                    y -= h
                report.append((p_old, size, int(need), free, es_col))
                placed = True
                break
        if not placed:
            items, total = layout(g['frags'], width_pt, 15, es_col, width_es)
            report.append((p_old, 'НЕ ВЛЕЗ', int(total / 72 * PX), g['y1'] - g['y0'], es_col))
