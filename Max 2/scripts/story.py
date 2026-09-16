import sys; sys.path.insert(0, '/home/claude/work')
import numpy as np
from PIL import Image, ImageFilter
from common import half
from spreads import SPREADS
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.colors import HexColor

pdfmetrics.registerFont(TTFont('Bal', '/home/claude/fonts/BalsamiqSans-Regular.ttf'))
pdfmetrics.registerFont(TTFont('BalB', '/home/claude/fonts/BalsamiqSans-Bold.ttf'))
EN = '#111111'; ES_WHITE = '#1B44A0'; ES_SKY = '#12327D'
PAGE_W, PAGE_H = 8.625 * inch, 11.25 * inch
PX = 300.0
BAND = 750
FEATHER = 180
H_PX = 3375

def page_source(p):
    """исходная чистая картинка страницы p (номер в старой книге)"""
    left = p if p % 2 == 0 else p - 1
    return half(SPREADS[left], 'L' if p % 2 == 0 else 'R')

def extend_top(img):
    a = np.asarray(img).astype(float)
    top = a[:4].mean(0)
    r, g, b = top[:, 0], top[:, 1], top[:, 2]
    w = a.shape[1]; xs = np.arange(w)
    blue = (b > 190) & (b - r > 40) & (top.min(1) < 215)
    light = top.min(1) > 150
    sel = None; kind = 'white'
    if blue.mean() >= 0.2:
        sel = blue; kind = 'sky'
    elif light.mean() >= 0.3:
        med = np.median(top[light], axis=0)
        sel = light & (np.abs(top - med).max(1) < 30); kind = 'light'
    if sel is None or sel.sum() < 50:
        F = np.full((w, 3), 255.0); kind = 'white'
    else:
        F = np.zeros((w, 3))
        for c in range(3):
            co = np.polyfit(xs[sel], top[sel, c], 2)
            F[:, c] = np.polyval(co, xs)
        F = F.clip(0, 255)
        if F.min() > 235:
            F[:] = 255.0; kind = 'white'
    t = np.linspace(0, 1, FEATHER)[:, None, None]
    t = t * t * (3 - 2 * t)
    a[:FEATHER] = a[:FEATHER] * t + F[None] * (1 - t)
    band = np.repeat(F[None], BAND, axis=0)
    out = np.vstack([band, a]).clip(0, 255).astype(np.uint8)
    return Image.fromarray(out), kind

def busy_rows(img, x0, x1):
    g = np.asarray(img.convert('L').resize((img.width // 4, img.height // 4))).astype(float)
    g = np.asarray(Image.fromarray(g.astype(np.uint8)).filter(ImageFilter.GaussianBlur(1)))
    gx = np.abs(np.diff(g.astype(float), axis=1))[:-1]
    gy = np.abs(np.diff(g.astype(float), axis=0))[:, :-1]
    mag = np.maximum(gx, gy)
    sub = mag[:, x0 // 4: x1 // 4]
    frac = (sub > 6).mean(1)
    rows = frac > 0.004
    return np.repeat(rows, 4)[:img.height]

def styles(size):
    lead = round(size * 1.35)
    j = lambda col: ParagraphStyle('j', fontName='Bal', fontSize=size, leading=lead, textColor=HexColor(col), alignment=TA_JUSTIFY)
    c = lambda col: ParagraphStyle('c', fontName='Bal', fontSize=size, leading=round(size * 1.25), textColor=HexColor(col), alignment=TA_CENTER)
    return j, c, lead

def layout(frags, width_pt, size, es_col, width_es=None):
    """список (flowable, gap_pt, h_pt, lang) и общая высота"""
    if width_es is None:
        width_es = width_pt
    j, c, lead = styles(size)
    items = []
    GAP_PARA, GAP_LANG, GAP_FRAG = 0.4 * size, 1.3 * size, 2.0 * size
    GAP_C_LANG, GAP_C = 0.15 * size, 0.75 * size
    prev = None
    for f in frags:
        if f[0] == 'p':
            first = True
            for t in f[1]:
                gap = 0 if prev is None else (GAP_FRAG if first else GAP_PARA)
                items.append((Paragraph(t, j(EN)), gap, 'en')); first = False; prev = 'p'
            first = True
            for t in f[2]:
                items.append((Paragraph(t, j(es_col)), GAP_LANG if first else GAP_PARA, 'es')); first = False
        else:
            gap = 0 if prev is None else (GAP_C if prev == 'c' else GAP_FRAG)
            items.append((Paragraph(f[1], c(EN)), gap, 'en'))
            items.append((Paragraph(f[2], c(es_col)), GAP_C_LANG, 'es')); prev = 'c'
    total = 0; out = []
    for fl, gap, lang in items:
        _, h = fl.wrap(width_pt if lang == 'en' else width_es, 10000)
        total += gap + h; out.append((fl, gap, h, lang))
    return out, total

def build(p, sizes=(17, 16, 15, 14)):
    src = page_source(p)
    img, kind = extend_top(src)
    left = (p % 2 == 0)
    x0, x1 = (200, 2390) if left else (198, 2388)
    width_pt = (x1 - x0) / PX * 72
    busy = busy_rows(img, x0, x1)
    placements = []
    groups = S_[p]
    for gi, (anchor, frags) in enumerate(groups):
        done = False
        for size in sizes:
            # цвет испанского определяем позже по фону; для расчёта высоты не важен
            items, total = layout(frags, width_pt, size, ES_WHITE)
            need = total / 72 * PX
            if anchor == 'top':
                y0 = 200
                y = y0
                while y < H_PX and not busy[y]: y += 1
                free_end = y - 70
                if gi + 1 < len(groups):
                    free_end = min(free_end, 1900)
                if free_end - y0 >= need:
                    start = min(360, y0 + (free_end - y0 - need) / 2) if free_end - y0 - need > 160 else y0
                    placements.append((start, items, size, total)); done = True; break
            else:
                yb = H_PX - 38 - 150
                y = yb
                while y > 0 and not busy[y]: y -= 1
                free_top = y + 70
                if yb - free_top >= need:
                    start = yb - need - min(80, (yb - free_top - need) / 2)
                    placements.append((start, items, size, total)); done = True; break
        if not done:
            placements.append(None)
    return img, kind, placements, (x0, x1)

import texts
S_ = texts.S
