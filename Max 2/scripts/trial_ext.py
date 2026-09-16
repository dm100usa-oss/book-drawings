import sys; sys.path.insert(0, '/home/claude/work')
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from story import page_source, extend_top, layout, ES_SKY, ES_WHITE, PAGE_W, PAGE_H, PX, BAND, FEATHER
from layout_cfg import CFG, fr
from reportlab.pdfgen import canvas
from extras import page_number

def extend_bottom(img):
    a = np.asarray(img).astype(float)
    bot = a[-4:].mean(0)
    w = a.shape[1]
    med = np.median(bot, axis=0)
    F = np.tile(med, (w, 1))
    t = np.linspace(1, 0, FEATHER)[:, None, None]
    t = t * t * (3 - 2 * t)
    a[-FEATHER:] = a[-FEATHER:] * t + F[None] * (1 - t)
    band = np.repeat(F[None], BAND, axis=0)
    return Image.fromarray(np.vstack([a, band]).clip(0, 255).astype(np.uint8))

def cloud_edge(img, y_edge=800):
    im = img.convert('RGB'); W, H = im.size
    m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m)
    d.rectangle((0, 0, W, y_edge), fill=255)
    rng = np.random.default_rng(3)
    x = -60
    while x < W + 60:
        r = int(rng.integers(70, 130))
        d.ellipse((x - r, y_edge - r + int(rng.integers(20, 70)), x + r, y_edge + r - 20 + int(rng.integers(0, 40))), fill=255)
        x += int(r * 1.4)
    shadow = m.filter(ImageFilter.GaussianBlur(18)).point(lambda v: int(v * 0.35))
    shade = Image.new('RGB', (W, H), (150, 185, 215))
    im = Image.composite(shade, im, Image.fromarray(np.roll(np.asarray(shadow), 14, axis=0)))
    m2 = m.filter(ImageFilter.GaussianBlur(2))
    return Image.composite(Image.new('RGB', (W, H), (255, 255, 255)), im, m2)

def draw(c, img_path, groups, left, n):
    c.drawImage(img_path, 0, 0, PAGE_W, PAGE_H)
    arr = np.asarray(Image.open(img_path)).astype(float)
    dx0, dx1 = (200, 2390) if left else (198, 2388)
    for g in groups:
        x0 = g.get('x0') or dx0; x1 = g.get('x1') or dx1
        wpt = (x1 - x0) / PX * 72
        reg = arr[g['y0']:g['y1'], x0:x1].reshape(-1, 3).mean(0)
        es = ES_SKY if (reg[2] - reg[0]) > 40 else ES_WHITE
        items, total = layout(g['frags'], wpt, 16, es)
        need = total / 72 * PX; free = g['y1'] - g['y0']
        print('need', int(need), 'free', free)
        top = g['y0'] + (free - need) / 2
        y = PAGE_H - top / PX * 72
        for fl, gap, h, lang in items:
            y -= gap; fl.drawOn(c, x0 / PX * 72, y - h); y -= h
    page_number(c, n)

c = canvas.Canvas('/home/claude/work/trial_ext.pdf', pagesize=(PAGE_W, PAGE_H), initialFontName='Bal')
# 1) развороты с добавкой снизу: стр. 38–39 (старые 32–33)
for p_old, n in ((32, 38), (33, 39)):
    im = extend_bottom(page_source(p_old)); path = f'/home/claude/work/tb_{p_old}.jpg'
    im.save(path, quality=92)
    if p_old == 32:
        groups = [dict(y0=1560, y1=3215, x0=300, frags=CFG[32][0]['frags'])]
    else:
        groups = [dict(y0=2700, y1=3150, frags=CFG[33][0]['frags'])]
    draw(c, path, groups, p_old % 2 == 0, n); c.showPage()
# 2) страница с пароходом, добавка сверху + облачный край (стр. 29, старая 25)
im, _ = extend_top(page_source(25)); im = cloud_edge(im, 820)
path = '/home/claude/work/tc_25.jpg'; im.save(path, quality=92)
draw(c, path, [dict(y0=170, y1=800, frags=CFG[25][0]['frags'])], False, 29); c.showPage()
c.save()
