"""Подгонка толщины линии новых рисунков под старые.

У рисунков из репозитория toddler-coloring-book толщина линии
в пересчёте на размер 420 px равна примерно 6.0. У новых рисунков
она обычно вдвое меньше, и на странице рядом со старыми они
выглядят бледными. Этот скрипт наращивает линию до нужного уровня.

Запуск:  python3 thicken.py  (обрабатывает всё в папке newart)
Результат: файлы *_fix.png рядом с исходниками.
"""
import glob
import os
import numpy as np
from PIL import Image
from scipy import ndimage

TARGET = 6.0


def line_width(mask, size):
    runs = []
    for row in mask[::5]:
        c = 0
        for v in row:
            if v:
                c += 1
            elif c:
                runs.append(c)
                c = 0
        if c:
            runs.append(c)
    runs = [x for x in runs if x < 80]
    return np.median(runs) / size * 420 if runs else 0


def process(path, out):
    im = Image.open(path).convert('L')
    a = np.array(im)
    ys, xs = np.where(a < 200)
    im = im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    m = np.array(im) < 128
    size = max(im.size)
    cur = line_width(m, size)
    steps = 0
    while cur < TARGET and steps < 14:
        m = ndimage.binary_dilation(m, np.ones((3, 3)))
        steps += 1
        cur = line_width(m, size)
    Image.fromarray(np.where(m, 0, 255).astype('uint8')).save(out)
    return round(cur, 2), steps


if __name__ == '__main__':
    for p in sorted(glob.glob('newart/*.png')):
        if p.endswith('_fix.png'):
            continue
        out = p.replace('.png', '_fix.png')
        print(os.path.basename(p), process(p, out))
