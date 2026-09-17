# Правка лиц на рисунках для книги Build a Sentence.
# face: стереть все линии, которые целиком лежат в рамке (глаза, брови, щеки, улыбка)
# dots: глаза с белками или бликами в рамке заменить круглыми точками, как у львенка
# Рамка задается долями от размера рисунка после обрезки полей: (x0, y0, x1, y1).
import numpy as np
from PIL import Image
from scipy import ndimage as nd


def crop_content(im):
    a = np.asarray(im)
    ys, xs = np.where(a < 200)
    return im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))


def _inside(sl, box, h, w, pad=0.0):
    y0, y1 = (box[1] - pad) * h, (box[3] + pad) * h
    x0, x1 = (box[0] - pad) * w, (box[2] + pad) * w
    return sl[0].start >= y0 and sl[0].stop <= y1 and sl[1].start >= x0 and sl[1].stop <= x1


def apply(im, edits):
    im = crop_content(im.convert('L'))
    a = np.array(im)
    h, w = a.shape
    dark = a < 160
    for kind, box in edits:
        lab, n = nd.label(dark, np.ones((3, 3)))
        sls = nd.find_objects(lab)
        ids = [i + 1 for i, sl in enumerate(sls) if sl is not None and _inside(sl, box, h, w, 0.05)]
        if kind == 'face':
            for i in ids:
                m = nd.binary_dilation(lab == i, iterations=6)
                a[m] = 255
                dark[m] = False
        elif kind == 'dots':
            im2 = eyes_to_dots(Image.fromarray(a), box)
            a = np.array(im2)
            dark = a < 160
    return Image.fromarray(a)


def find_eyes(im, box=(0, 0, 1, 1), amin=0.8):
    """ищет глаза с белками или бликами; возвращает список (x, y, d, маска)"""
    a = np.asarray(im) < 160
    h, w = a.shape
    lab, n = nd.label(a, np.ones((3, 3)))
    sls = nd.find_objects(lab)
    lim = h * w * 0.012
    found, used = [], set()
    for i, sl in enumerate(sls):
        if sl is None or not _inside(sl, box, h, w):
            continue
        m = lab[sl] == i + 1
        bh, bw = m.shape
        if not (0.45 < bh / bw < 2.2):
            continue
        f = nd.binary_fill_holes(m)
        fa, ink = int(f.sum()), int(m.sum())
        if fa > lim or fa < h * w * 0.00008:
            continue
        holes = f & ~m
        if not holes.any():
            continue
        # что лежит внутри: другие линии (зрачок)
        inner = np.unique(lab[sl][holes])
        inner = [j for j in inner if j and j != i + 1]
        ratio = holes.sum() / fa
        if inner:
            kind = 'ring'
        elif ratio < 0.35 and ink / (bh * bw) > 0.45 and amin <= bh / bw < 1.8:
            kind = 'shine'
        else:
            continue
        mask = np.zeros(a.shape, bool)
        mask[sl] = f
        cy, cx = nd.center_of_mass(f)
        found.append((sl[1].start + cx, sl[0].start + cy, bw, bh, kind, mask, i + 1))
        used.add(i + 1)
    # глаз-кольцо внутри другого кольца не считаем отдельно
    out = []
    for e in found:
        if any(o is not e and o[5][int(e[1]), int(e[0])] and o[5].sum() > e[5].sum() for o in found):
            continue
        out.append(e)
    return out


def eyes_to_dots(im, box=(0, 0, 1, 1), skip=(), amin=0.8):
    im = crop_content(im.convert('L'))
    a = np.array(im)
    h, w = a.shape
    base = 0.05 * np.sqrt(h * w)
    for k, (x, y, bw, bh, kind, mask, _) in enumerate(find_eyes(im, box, amin)):
        if k in skip:
            continue
        if kind == 'shine' and max(bw, bh) <= base * 1.25:
            a[mask] = 0           # точка с бликом: просто залить
            continue
        d = min(base, 0.75 * min(bw, bh))
        m = nd.binary_dilation(mask, iterations=4)
        a[m] = 255
        yy, xx = np.ogrid[:h, :w]
        a[(xx - x) ** 2 + (yy - y) ** 2 <= (d / 2) ** 2] = 0
    return Image.fromarray(a)
