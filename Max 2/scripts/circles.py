import sys; sys.path.insert(0, '/home/claude/work')
from PIL import Image
from common import half
U = 258.8
TITLE = '/mnt/user-data/uploads/Little_Max_Title_Final_8_5x11_300dpi.png'

def crop_square(img, cx, cy, side, pad=False):
    """квадрат в десятых долях страницы; pad=True — белые поля за краем (для рисунков на белом)"""
    s = side * U
    x0 = cx * U - s / 2; y0 = cy * U - s / 2
    w, h = img.size
    if not pad:
        x0 = min(max(x0, 0), w - s); y0 = min(max(y0, 0), h - s)
        return img.crop(tuple(int(round(v)) for v in (x0, y0, x0 + s, y0 + s)))
    canvas = Image.new('RGB', (int(s), int(s)), 'white')
    canvas.paste(img, (int(round(-x0)), int(round(-y0))))
    return canvas

SPEC = {
 'Lion': ('2781', 'L', (6.25, 6.6, 7.6), False),
 'Giraffe': ('2777', 'R', (6.3, 2.4, 7.0), False),
 'Elephant': ('2778', 'L', (3.4, 6.55, 6.6), False),
 'Monkey': ('2374', 'L', (5.1, 4.3, 7.0), False),
 'Zebra': ('2780', 'R', (5.3, 3.5, 5.9), False),
 'Parrot': ('2780', 'L', (4.45, 6.35, 9.2), False),
 'Dolphin': ('2209', 'L', (2.85, 6.45, 5.4), False),
 'Sand castle': ('2209', 'R', (2.65, 7.3, 5.2), False),
 'Crab': ('2210', 'L', (2.25, 7.5, 4.8), False),
 'Turtle': ('2210', 'R', (4.35, 6.5, 8.0), False),
 'Ship': ('2211', 'R', (4.85, 4.4, 8.8), False),
 'Seashell': ('2213', 'R', (8.1, 5.9, 3.3), False),
 'Ferris wheel': ('2789', 'R', (9.1, 0.95, 1.9), False),
 'Cotton candy': ('title', None, None, False),
 'Horse': ('2790', 'L', (4.65, 5.3, 9.3), False),
 'Clown': ('2791', 'R', (4.1, 4.35, 5.2), False),
 'Balloon': ('2791', 'L', (5.25, 3.75, 11.0), True),
 'Drum': ('2793', 'R', (4.8, 6.35, 7.2), True),
 'Basket': ('titlebasket', None, None, False),
 'Blanket': ('2798', 'R', (4.9, 4.5, 8.4), False),
 'Squirrel': ('2796', 'L', (6.6, 2.05, 5.9), False),
 'Swing': ('2797', 'L', (4.25, 3.6, 7.6), True),
 'Slide': ('2797', 'R', (5.0, 4.95, 9.0), False),
 'Cloud': ('2798', 'R', (2.1, 7.5, 5.4), False),
}

def cropped(word):
    f, side, u, pad = SPEC[word]
    if f == 'titlebasket':
        import numpy as np
        a = np.asarray(Image.open(TITLE).convert('RGB')).copy()
        reg = a[2300:2540, 1400:1685]; reg[reg.min(2) < 250] = 255   # рука и палочка Макса
        reg = a[2840:3100, 1400:1545]; reg[reg.min(2) < 250] = 255   # ботинок Макса
        return Image.fromarray(a).crop((1470, 2405, 2090, 3025))
    if f == 'title':
        import numpy as np
        a = np.asarray(Image.open(TITLE).convert('RGB').crop((1590, 1950, 2070, 2430))).copy()
        z = a[:170, :130].astype(int)
        grey = (z.max(2) - z.min(2) < 40) & (z.min(2) < 245)
        z[grey] = 255
        a[:170, :130] = z
        return Image.fromarray(a.astype('uint8'))
    return crop_square(half(f, side), *u, pad=pad)
