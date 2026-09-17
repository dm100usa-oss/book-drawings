# Черновик новой книги Build a Sentence: 5 листов на букву, 130 листов.
# Запуск из корня book-drawings:  python3 scripts/build_cvc.py
# Нужны рядом папки repos/toddler-coloring-book, repos/magic-of-discoveries,
# repos/MOY-PROEKT- (рисунки Макса, испанская рукопись, новые рисунки).
# Оформление листа берется из scripts/build_book.py без изменений.
import os
import re
import sys
import zlib
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
import build_book as bb
import face_edit as fe

CVC = 'repos/MOY-PROEKT-/Kniga CVC Words'
MAX1 = CVC + '/Risunki Max 1'
MAX2 = CVC + '/Risunki Max 2'
NEWMAX = CVC + '/Risunki New Max/Pequeno-Max-Letter-2.pdf'
NEW = CVC + '/Novye risunki'
WORDS = 'repos/magic-of-discoveries/public/words'
PRINT = 'repos/magic-of-discoveries/public/printables'
PREP = 'cvcart'          # подготовленные рисунки: белый фон, без подписи
OUT = 'out/Build-a-Sentence-130-DRAFT.pdf'

# третий образец предложения, только для слова up
bb.FRAMES.append(('Where do they go?', ['Balloons', 'go']))

# буква: [(источник, слово, артикль, образец)]
# источник: T:номер (раскраска 111), K:ключ (нынешняя книга), M1:файл, M2:файл,
# NM:страница (испанская рукопись), W:имя (сайт, words), PR:имя (сайт, printables),
# NEW:имя (новые рисунки), TODO:имя (рисунок еще не нарисован)
# образец: 0 = What do you see? I see ...   1 = What is this? This is ...
BOOK = [
    ('A', [('W:apple', 'apple', 'an', 0), ('M2:IMG_1645.png', 'anchor', 'an', 1),
           ('T:015', 'alpaca', 'an', 0), ('T:105', 'avocado', 'an', 1),
           ('T:052', 'axolotl', 'an', 0)]),
    ('B', [('T:020', 'bat', 'a', 0), ('M1:IMG_2971.png', 'bug', 'a', 1),
           ('NM:94', 'bed', 'a', 0), ('W:bus', 'bus', 'a', 1),
           ('T:022', 'bear', 'a', 0)]),
    ('C', [('T:030', 'cat', 'a', 0), ('W:cup', 'cup', 'a', 1),
           ('M2:IMG_1627.png', 'cap', 'a', 0), ('T:043', 'crab', 'a', 1),
           ('T:026', 'cow', 'a', 0)]),
    ('D', [('T:031', 'dog', 'a', 0), ('W:doll', 'doll', 'a', 1),
           ('T:033', 'duck', 'a', 0), ('T:080', 'drum', 'a', 1),
           ('T:034', 'deer', 'a', 0)]),
    ('E', [('NM:50', 'egg', 'an', 0), ('M1:IMG_2952.png', 'envelope', 'an', 1),
           ('NEW:elf', 'elf', 'an', 0), ('T:002', 'elephant', 'an', 1),
           ('T:028', 'eagle', 'an', 0)]),
    ('F', [('T:023', 'fox', 'a', 0), ('T:014', 'frog', 'a', 1),
           ('T:050', 'fish', 'a', 0), ('M2:IMG_1634.png', 'flag', 'a', 1),
           ('M1:IMG_2954.png', 'fork', 'a', 0)]),
    ('G', [('T:019', 'goat', 'a', 0), ('T:086', 'gift', 'a', 1),
           ('PR:food-grapes', 'grapes', '', 0), ('T:085', 'globe', 'a', 1),
           ('M1:IMG_3004.png', 'goose', 'a', 0)]),
    ('H', [('M1:IMG_2967.png', 'hen', 'a', 0), ('T:084', 'hat', 'a', 1),
           ('T:029', 'hamster', 'a', 0), ('T:018', 'hedgehog', 'a', 1),
           ('T:068', 'helicopter', 'a', 0)]),
    ('I', [('TODO:igloo', 'igloo', 'an', 0), ('M1:IMG_2970.png', 'insect', 'an', 1),
           ('M1:IMG_2972.png', 'inchworm', 'an', 0),
           ('K:M:ocean-island', 'island', 'an', 1), ('T:099', 'ice cream', '', 0)]),
    ('J', [('M1:IMG_3011.png', 'jam', '', 0), ('M2:IMG_1604.png', 'jar', 'a', 1),
           ('M1:IMG_2923.png', 'jug', 'a', 0), ('T:069', 'jet', 'a', 1),
           ('T:045', 'jellyfish', 'a', 0)]),
    ('K', [('M1:IMG_2927.png', 'kite', 'a', 0), ('W:key', 'key', 'a', 1),
           ('T:013', 'koala', 'a', 0), ('T:007', 'kangaroo', 'a', 1),
           ('M2:IMG_1587.png', 'kiwi', 'a', 0)]),
    ('L', [('W:lamp', 'lamp', 'a', 0), ('T:001', 'lion', 'a', 1),
           ('T:109', 'lemon', 'a', 0), ('M1:IMG_2938.png', 'leaf', 'a', 1),
           ('M2:IMG_1602.png', 'lollipop', 'a', 0)]),
    ('M', [('W:milk', 'milk', '', 0), ('NM:84', 'mug', 'a', 1),
           ('M1:IMG_3018.png', 'mittens', '', 0), ('T:006', 'monkey', 'a', 1),
           ('T:035', 'mouse', 'a', 0)]),
    ('N', [('M2:IMG_1635.png', 'net', 'a', 0), ('M2:IMG_1575.png', 'nut', 'a', 1),
           ('M1:IMG_2958.png', 'needle', 'a', 0), ('K:N:ninja', 'ninja', 'a', 1),
           ('K:N:nurse', 'nurse', 'a', 0)]),
    ('O', [('NEW:ox', 'ox', 'an', 0), ('NEW:ostrich', 'ostrich', 'an', 1),
           ('T:044', 'octopus', 'an', 0), ('PR:ocean-otter', 'otter', 'an', 1),
           ('T:103', 'orange', 'an', 0)]),
    ('P', [('M1:IMG_3006.png', 'pig', 'a', 0), ('M2:IMG_1638.png', 'pan', 'a', 1),
           ('M2:IMG_1637.png', 'pot', 'a', 0), ('T:004', 'parrot', 'a', 1),
           ('T:110', 'pumpkin', 'a', 0)]),
    ('Q', [('K:N:queen', 'queen', 'a', 0), ('K:N:quilt', 'quilt', 'a', 1),
           ('NEW:quail', 'quail', 'a', 0), ('TODO:quarter', 'quarter', 'a', 1),
           ('M1:IMG_2955.png', 'quill', 'a', 0)]),
    ('R', [('T:073', 'rocket', 'a', 0), ('T:008', 'rhino', 'a', 1),
           ('T:021', 'raccoon', 'a', 0), ('M1:IMG_2941.png', 'rainbow', 'a', 1),
           ('NM:9', 'rooster', 'a', 0)]),
    ('S', [('W:socks', 'socks', '', 0), ('W:sun', 'sun', 'the', 1),
           ('T:072', 'sub', 'a', 0), ('T:049', 'seal', 'a', 1),
           ('T:038', 'snail', 'a', 0)]),
    ('T', [('W:truck', 'truck', 'a', 0), ('M1:IMG_2937.png', 'tomato', 'a', 1),
           ('M1:IMG_2995.png', 'teddy', 'a', 0), ('T:046', 'turtle', 'a', 1),
           ('T:097', 'tulip', 'a', 0)]),
    ('U', [('M2:IMG_1633.png', 'up', '', 2), ('NEW:umpire', 'umpire', 'an', 1),
           ('NEW:ukulele', 'ukulele', 'a', 0), ('T:083', 'umbrella', 'an', 1),
           ('T:057', 'unicorn', 'a', 0)]),
    ('V', [('NEW:van', 'van', 'a', 0), ('NEW:valentine', 'valentine', 'a', 1),
           ('M1:IMG_3026.png', 'vase', 'a', 0), ('K:N:violin', 'violin', 'a', 1),
           ('K:N:volcano', 'volcano', 'a', 0)]),
    ('W', [('M1:IMG_2917.png', 'windmill', 'a', 0), ('M2:IMG_1573.png', 'wave', 'a', 1),
           ('T:042', 'whale', 'a', 0), ('T:100', 'watermelon', 'a', 1),
           ('PR:ocean-walrus', 'walrus', 'a', 0)]),
    ('X', [('K:N:xray', 'x-ray', 'an', 0), ('K:N:xylophone', 'xylophone', 'a', 1),
           ('M1:IMG_3008.png', 'fox', 'a', 0), ('TODO:box', 'box', 'a', 1),
           ('NEW:ox', 'ox', 'an', 0)]),
    ('Y', [('M1:IMG_2919.png', 'yarn', '', 0), ('K:N:yacht', 'yacht', 'a', 1),
           ('K:N:yeti', 'yeti', 'a', 0), ('TODO:yak', 'yak', 'a', 1),
           ('TODO:yo-yo', 'yo-yo', 'a', 0)]),
    ('Z', [('T:003', 'zebra', 'a', 0), ('K:N:zeppelin', 'zeppelin', 'a', 1),
           ('TODO:zipper', 'zipper', 'a', 0), ('TODO:zucchini', 'zucchini', 'a', 1),
           ('TODO:zigzag', 'zigzag', 'a', 0)]),
]


# ---------- правка лиц ----------
# face: стереть лицо на предмете; dots: глаза животного сделать точками
# рамка: доли ширины и высоты рисунка после обрезки полей (x0, y0, x1, y1)
EDITS = {
    'W:apple': [('face', (0.2, 0.42, 0.8, 0.8))],
    'M2:IMG_1645.png': [('face', (0.38, 0.7, 0.62, 0.9))],
    'T:105': [('face', (0.25, 0.32, 0.62, 0.47))],
    'NM:94': [('face', (0.46, 0.2, 0.68, 0.39))],
    'W:cup': [('face', (0.15, 0.4, 0.6, 0.78))],
    'T:080': [('face', (0.28, 0.48, 0.65, 0.6))],
    'NM:50': [('face', (0.2, 0.42, 0.8, 0.8))],
    'M1:IMG_2954.png': [('face', (0.68, 0.48, 0.85, 0.72))],
    'T:086': [('face', (0.1, 0.6, 0.36, 0.8))],
    'T:085': [('face', (0.26, 0.44, 0.52, 0.54))],
    'T:084': [('face', (0.3, 0.15, 0.55, 0.32))],
    'T:068': [('face', (0.15, 0.35, 0.32, 0.5))],
    'T:099': [('face', (0.25, 0.45, 0.8, 0.62))],
    'M1:IMG_2923.png': [('face', (0.33, 0.3, 0.55, 0.5))],
    'T:069': [('face', (0.03, 0.58, 0.3, 0.8)), ('face', (0.0, 0.8, 0.14, 0.92))],
    'M1:IMG_2927.png': [('face', (0.18, 0.22, 0.42, 0.52))],
    'W:key': [('face', (0.15, 0.28, 0.85, 0.5))],
    'W:lamp': [('face', (0.3, 0.6, 0.7, 0.87))],
    'T:109': [('face', (0.15, 0.35, 0.7, 0.7))],
    'W:milk': [('face', (0.08, 0.43, 0.6, 0.7))],
    'NM:84': [('face', (0.15, 0.38, 0.62, 0.78))],
    'T:103': [('face', (0.05, 0.3, 0.6, 0.55))],
    'M2:IMG_1637.png': [('face', (0.5, 0.52, 0.85, 0.85))],
    'T:110': [('face', (0.35, 0.5, 0.65, 0.66))],
    'K:N:quilt': [('face', (0.42, 0.4, 0.62, 0.53))],
    'T:073': [('face', (0.08, 0.08, 0.35, 0.25))],
    'M1:IMG_2941.png': [('face', (0.4, 0.03, 0.65, 0.25))],
    'W:sun': [('face', (0.25, 0.4, 0.75, 0.7))],
    'T:072': [('face', (0.36, 0.31, 0.53, 0.42))],
    'M1:IMG_2937.png': [('face', (0.3, 0.45, 0.7, 0.8))],
    'T:097': [('face', (0.28, 0.2, 0.7, 0.35))],
    'T:083': [('face', (0.25, 0.2, 0.5, 0.35))],
    'NEW:valentine': [('face', (0.35, 0.42, 0.68, 0.65))],
    'M1:IMG_3026.png': [('face', (0.35, 0.72, 0.62, 0.9))],
    'K:N:volcano': [('face', (0.38, 0.6, 0.62, 0.76))],
    'T:100': [('face', (0.25, 0.55, 0.66, 0.7))],
    'K:N:xylophone': [('face', (0.38, 0.6, 0.62, 0.7))],
    'K:N:yacht': [('face', (0.73, 0.58, 0.9, 0.78))],
    'K:N:zeppelin': [('face', (0.42, 0.73, 0.62, 0.9))],
    'M1:IMG_2971.png': [('dots', (0, 0, 1, 1))],
    'W:doll': [('dots', (0, 0, 1, 1))],
    'T:031': [('dots', (0, 0, 1, 1), 0.45)],
    'M1:IMG_3004.png': [('dots', (0, 0, 1, 1))],
    'M1:IMG_2967.png': [('dots', (0.45, 0.142, 0.8, 0.3))],
    'M1:IMG_2972.png': [('dots', (0, 0, 1, 1))],
    'NEW:ox': [('dots', (0, 0, 1, 1))],
    'M1:IMG_3006.png': [('dots', (0, 0, 1, 1))],
    'NEW:quail': [('dots', (0.7, 0.1, 0.9, 0.25))],
    'NM:9': [('dots', (0, 0, 1, 1))],
    'M1:IMG_2995.png': [('dots', (0, 0, 1, 1))],
    'M1:IMG_3008.png': [('dots', (0, 0, 1, 1))],
}

# одинаковый размер: площадь рисунка на листе примерно одна и та же
TARGET = 180.0        # сторона квадрата той же площади, пунктов
MAX_H, MAX_W = 182.0, bb.CW * 0.68


# ---------- подготовка рисунков ----------
def on_white(im):
    im = im.convert('RGBA')
    bg = Image.new('RGBA', im.size, 'white')
    bg.alpha_composite(im)
    return bg.convert('L')


def drop_label(im):
    """убирает подпись или адрес сайта внизу картинки"""
    a = np.asarray(im) < 200
    rows = np.where(a.any(axis=1))[0]
    if not len(rows):
        return im
    gap = max(3, im.height // 100)
    blocks, s, p = [], rows[0], rows[0]
    for r in rows[1:]:
        if r - p > gap:
            blocks.append((s, p))
            s = r
        p = r
    blocks.append((s, p))
    keep = [b for b in blocks if not (b[0] > im.height * 0.80 and
                                      b[1] - b[0] < im.height * 0.12)]
    bottom = keep[-1][1] if keep else im.height - 1
    return im.crop((0, 0, im.width, bottom + 1))


def placeholder(name):
    im = Image.new('L', (1600, 900), 255)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((20, 20, 1580, 880), 40, outline=0, width=10)
    f1 = ImageFont.truetype('fonts/Baloo2-Variable.ttf', 190)
    f2 = ImageFont.truetype('fonts/Baloo2-Variable.ttf', 90)
    d.text((800, 360), name, font=f1, fill=0, anchor='mm')
    d.text((800, 620), 'picture coming soon', font=f2, fill=0, anchor='mm')
    return im


def load_source(src):
    kind, name = src.split(':', 1)
    if kind == 'T':
        return on_white(Image.open(os.path.join(bb.TOD, name + '.png')))
    k2, n2 = name.split(':', 1)
    if k2 == 'N':
        return on_white(Image.open(os.path.join('newart', n2 + '_fix.png')))
    return on_white(Image.open(os.path.join(bb.MAG, n2 + '.png')))


def prepare(src):
    """возвращает ключ для build_book"""
    key = prepare_plain(src)
    if src not in EDITS:
        return key
    safe = 'E_' + re.sub(r'[^A-Za-z0-9_-]', '_', src)
    out = os.path.join(PREP, safe + '.png')
    if not os.path.exists(out):
        if key.startswith('C:'):
            im = Image.open(os.path.join(PREP, key[2:] + '.png')).convert('L')
        else:
            im = load_source(src)
        for kind, box, *opt in EDITS[src]:
            if kind == 'face':
                im = fe.apply(im, [(kind, box)])
            else:
                im = fe.eyes_to_dots(im, box, amin=opt[0] if opt else 0.8)
        os.makedirs(PREP, exist_ok=True)
        im.save(out)
    return 'C:' + safe


def prepare_plain(src):
    kind, name = src.split(':', 1)
    if kind == 'T':
        return name
    if kind == 'K':
        return name
    os.makedirs(PREP, exist_ok=True)
    safe = re.sub(r'[^A-Za-z0-9_-]', '_', src)
    out = os.path.join(PREP, safe + '.png')
    if not os.path.exists(out):
        if kind == 'M1':
            im = on_white(Image.open(os.path.join(MAX1, name)))
        elif kind == 'M2':
            im = on_white(Image.open(os.path.join(MAX2, name)))
        elif kind == 'NEW':
            im = on_white(Image.open(os.path.join(NEW, name + '.png')))
        elif kind == 'W':
            im = drop_label(on_white(Image.open(os.path.join(WORDS, name + '-en.png'))))
        elif kind == 'PR':
            im = drop_label(on_white(Image.open(os.path.join(PRINT, name + '.png'))))
        elif kind == 'NM':
            subprocess.run(['pdftoppm', '-r', '200', '-png', '-singlefile',
                            '-f', name, '-l', name, NEWMAX, '/tmp/nm_page'], check=True)
            im = drop_label(on_white(Image.open('/tmp/nm_page.png')))
        elif kind == 'TODO':
            im = placeholder(name)
        else:
            raise ValueError(src)
        im.save(out)
    return 'C:' + safe


_orig_vectorize = bb.vectorize

# толщина линий на листе, пунктов (так измерена у большинства рисунков)
LINE_T = 2.7
LINE_MIN, LINE_MAX = 2.0, 3.4      # в этих пределах рисунок не трогаем
# толщину правим только у этих рисунков (волна, кастрюля, страус, бык)
LINE_FIX = {'M2:IMG_1573.png', 'M2:IMG_1637.png', 'NEW:ostrich', 'NEW:ox'}
LINE_FIX_KEYS = set()


def load_key(key):
    if key.startswith('C:'):
        return Image.open(os.path.join(PREP, key[2:] + '.png')).convert('L')
    if key.startswith('N:'):
        return on_white(Image.open(os.path.join('newart', key[2:] + '_fix.png')))
    if key.startswith('M:'):
        return on_white(Image.open(os.path.join(bb.MAG, key[2:] + '.png')))
    return on_white(Image.open(os.path.join(bb.TOD, key + '.png')))


def even_lines(bm):
    """линии рисунка приводятся к одной толщине на листе"""
    from scipy import ndimage as nd
    from skimage.morphology import skeletonize
    h, w = bm.shape
    sc = min(TARGET / (w * h) ** 0.5, MAX_H / h, MAX_W / w)   # пунктов на точку
    D = nd.distance_transform_edt(bm)
    wd = 2 * D[skeletonize(bm)]
    wd = wd[wd > 0]
    if not len(wd):
        return bm
    now = float(np.median(wd)) * sc
    if LINE_MIN <= now <= LINE_MAX:
        return bm
    r = LINE_T / 2 / sc                                      # половина нужной толщины, точек
    if now < LINE_T:
        # тонкие линии утолщаем равномерно
        return nd.distance_transform_edt(~bm) <= (LINE_T - now) / 2 / sc
    # толстые линии обрезаем до нужной толщины, тонкие и сплошные пятна не трогаем
    core = nd.distance_transform_edt(~skeletonize(bm)) <= r
    out = bm & core
    big = D > r * 1.3
    lab, n = nd.label(big)
    for i, sl in enumerate(nd.find_objects(lab)):
        comp = lab[sl] == i + 1
        bh, bw = comp.shape
        if max(bh, bw) * sc < 14 and comp.sum() / max(bh, bw) ** 2 > 0.3:
            # сплошное пятно (глаз, семечко): вернуть целиком
            g = np.zeros_like(bm)
            g[sl] = comp
            out |= bm & (nd.distance_transform_edt(~g) <= r * 1.3 + 1)
    return out


def vectorize(key, solid=False):
    fix = key in LINE_FIX_KEYS
    tag = ('U_' if fix else '') + key.replace(':', '_')
    out = os.path.join(bb.CACHE, tag + '.svg')
    if os.path.exists(out):
        return open(out).read()
    im = load_key(key)
    a = np.array(im)
    ys, xs = np.where(a < 200)
    im = im.crop((xs.min(), ys.min(), xs.max() + 1, ys.max() + 1))
    k = max(1, int(1800 / max(im.size)))
    im = im.resize((im.width * k, im.height * k), Image.LANCZOS)
    if max(im.size) > 3000:
        im.thumbnail((3000, 3000), Image.LANCZOS)
    bm = np.array(im) < 150
    if fix:
        bm = even_lines(bm)
    b = bm.astype(np.uint8) * 255
    Image.fromarray(255 - b).save('/tmp/t.pbm')
    subprocess.run(['potrace', '-s', '-o', '/tmp/t.svg', '--turdsize', '6',
                    '--alphamax', '1.0', '--opttolerance', '0.2', '/tmp/t.pbm'],
                   check=True)
    s = open('/tmp/t.svg').read()
    vb = re.search(r'viewBox="([\d\. ]+)"', s).group(1).split()
    g = s[s.find('<g '):s.rfind('</g>') + 4]
    res = '<!--%s %s-->%s' % (vb[2], vb[3], g)
    open(out, 'w').write(res)
    return res



_orig_art = bb.art


def art_even(key, solid=False):
    """рисунок с полями, чтобы на листе все были примерно одной площади"""
    aw, ah, grp = _orig_art(key, solid)
    sc = TARGET / (aw * ah) ** 0.5
    sc = min(sc, MAX_H / ah, MAX_W / aw)
    AH = MAX_H / sc
    py = (AH - ah) / 2
    return aw, AH, '<g transform="translate(0,%.2f)">%s</g>' % (py, grp)


def cover():
    s = bb.cover()
    s = s.replace('>Animals and More A to Z<', '>Simple Words A to Z<')
    s = s.replace('55 no-prep printable worksheets', '130 no-prep printable worksheets')
    s = s.replace('>Build a Sentence</text>', '>Build a Sentence</text>'
                  '<text x="%s" y="40" text-anchor="middle" font-family="Quicksand" '
                  'font-weight="700" font-size="12" fill="#9a9a9a">DRAFT</text>' % bb.CX, 1)
    return s


def terms():
    s = bb.terms()
    s = s.replace('55 worksheets: two for every letter A to Z, plus 3 bonus pages.',
                  '130 worksheets: five for every letter A to Z.')
    s = s.replace('Two sentence patterns:  I see a ...   and   This is a ...',
                  'Sentence patterns:  I see a ...   This is a ...')
    s = s.replace('Six sight words in total:  I, see, this, is, a, an.',
                  'Sight words:  I, see, this, is, a, an, the, go.')
    return s


if __name__ == '__main__':
    import cairosvg
    from pypdf import PdfWriter
    os.makedirs(bb.CACHE, exist_ok=True)
    os.makedirs('pages_cvc', exist_ok=True)
    os.makedirs('out', exist_ok=True)
    files = []
    for nm, svg in (('00-cover', cover()), ('01-terms', terms())):
        p = 'pages_cvc/%s.pdf' % nm
        cairosvg.svg2pdf(bytestring=svg.encode(), write_to=p)
        files.append(p)
    n = 0
    bb.art = art_even
    bb.vectorize = vectorize
    for letter, items in BOOK:
        assert len(items) == 5, letter
        for i, (src, word, article, fr) in enumerate(items):
            key = prepare(src)
            if src in LINE_FIX:
                LINE_FIX_KEYS.add(key)
            bb.NO_PATCH.add(key)
            seed = zlib.crc32(('%s%d' % (letter, i)).encode()) & 0xffff
            svg = bb.page(letter, key, word, article, fr, seed=seed)
            n += 1
            p = 'pages_cvc/%03d-%s%d.pdf' % (n + 1, letter, i + 1)
            cairosvg.svg2pdf(bytestring=svg.encode(), write_to=p)
            files.append(p)
            print(letter, i + 1, word, flush=True)
    w = PdfWriter()
    for f in files:
        w.append(f)
    w.write(OUT)
    print('страниц:', len(files))
