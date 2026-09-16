from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
SRC = '/mnt/user-data/uploads/Little_Max_KDP_Cover_5219x3375_300dpi_FIXED.png'
FONT = '/home/claude/fonts/BalsamiqSans-Regular.ttf'
cov = Image.open(SRC).convert('RGB')
a = np.asarray(cov).astype(float)

# ---- 1. имя автора: стираем и рисуем ниже и чуть меньше ----
x0, x1, y0, y1 = 3505, 4355, 40, 206
L = a[y0:y1, 3500]; R = a[y0:y1, 4360]
t = np.linspace(0, 1, x1 - x0)[None, :, None]
fill = L[:, None, :] * (1 - t) + R[:, None, :] * t
blend = np.ones((y1 - y0, 1, 1))
fe = 14
blend[-fe:, 0, 0] = np.linspace(1, 0, fe)          # мягкий переход внизу к свечению ленты
a[y0:y1, x0:x1] = fill * blend + a[y0:y1, x0:x1] * (1 - blend)
img = Image.fromarray(a.clip(0, 255).astype(np.uint8))

name = 'Ricardo Demi'
cx, baseline = 3930, 214
size = 150
font = ImageFont.truetype(FONT, size)
asc_top = font.getbbox('d')[1]; base_off = font.getbbox('R')[3]
# подбираем размер: верх букв не выше 118 px
size = 117
font = ImageFont.truetype(FONT, size); base_off = font.getbbox('R')[3]
assert baseline - (base_off - font.getbbox('Rd')[1]) >= 118
tw = font.getlength(name)
tx = cx - tw / 2; ty = baseline - base_off
glow = Image.new('L', img.size, 0)
ImageDraw.Draw(glow).text((tx, ty), name, font=font, fill=255, stroke_width=17, stroke_fill=255)
glow = glow.filter(ImageFilter.GaussianBlur(10)).point(lambda v: min(255, int(v * 1.1)))
img = Image.composite(Image.new('RGB', img.size, (255, 255, 255)), img, glow)
ImageDraw.Draw(img).text((tx, ty), name, font=font, fill=(7, 69, 146), stroke_width=2, stroke_fill=(7, 69, 146))
print('author width', tw)
print('author size', size, 'top px', ty + font.getbbox('Rd')[1], 'bottom', ty + base_off)

# ---- 2. «pequeño» -> «Pequeño» ----
d = ImageDraw.Draw(img)
d.rectangle((4301, 1462, 4361, 1556), fill=(253, 253, 253))
pf = ImageFont.truetype(FONT, 10)
cap = 88
s = 60
while True:
    pf = ImageFont.truetype(FONT, s)
    bb = pf.getbbox('P')
    if bb[3] - bb[1] >= cap: break
    s += 1
bb = pf.getbbox('P')
layer = Image.new('L', (bb[2] + 40, bb[3] + 40), 0)
ImageDraw.Draw(layer).text((20 - bb[0], 20), 'P', font=pf, fill=255, stroke_width=1, stroke_fill=255)
lb = layer.getbbox()
layer = layer.crop(lb)
angle = 4.5
rot = layer.rotate(angle, resample=Image.BICUBIC, expand=True)
rot = rot.crop(rot.getbbox())
pw, ph = rot.size
# левый нижний угол буквы у основания строки
base_y = 1522
px = 4295
py = base_y - ph + 3
red = Image.new('RGB', rot.size, (234, 16, 28))
img.paste(red, (px, py), rot)
print('P size', s, 'box', px, py, px + pw, py + ph)

# ---- 3. место под штрихкод: белое поле в углу, закрывающее старое ----
d = ImageDraw.Draw(img)
bx0, by0, bx1, by1 = 1724, 2834, 2528, 3277
d.rectangle((bx0, by0, bx1, by1), fill=(255, 255, 255), outline=(170, 170, 170), width=3)
print('barcode panel in', (bx1 - bx0) / 300, (by1 - by0) / 300, 'from spine', (2588 - bx1) / 300, 'from bottom trim', (3337 - by1) / 300)

img.save('/home/claude/work/cover_fixed.png')
