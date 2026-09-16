import sys; sys.path.insert(0, '/home/claude/work')
import numpy as np
from PIL import Image, ImageDraw
from common import half
from story import extend_top, PAGE_W, PAGE_H, EN, ES_WHITE, ES_SKY, PX
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.colors import HexColor

W = '/home/claude/work/'
ES = ES_WHITE
RING = '#4FB3E8'
MAX2 = '/home/claude/max2/'

# ---------- общие элементы ----------
_b = np.asarray(half('2795', 'R')).copy()
_b[_b.min(axis=2) >= 240] = 255
Image.fromarray(_b).save(W + 'bg_plants.jpg', quality=92)

def plants(c, shift=-80):
    c.setFillColor(HexColor('#FFFFFF')); c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    c.drawImage(W + 'bg_plants.jpg', 0, shift, PAGE_W, 630)

def circle_img(img, box, name, size=700):
    cimg = img.crop(box).resize((size, size), Image.LANCZOS)
    mask = Image.new('L', (size * 4, size * 4), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size * 4, size * 4), fill=255)
    mask = mask.resize((size, size), Image.LANCZOS)
    out = Image.new('RGBA', (size, size), (0, 0, 0, 0)); out.paste(cimg, (0, 0), mask)
    p = f'{W}circ_{name}.png'; out.save(p); return p

def rounded_img(img, box, name, w=1400, radius=70):
    cimg = img.crop(box)
    h = round(w * cimg.height / cimg.width)
    cimg = cimg.resize((w, h), Image.LANCZOS)
    mask = Image.new('L', (w * 3, h * 3), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w * 3, h * 3), radius=radius * 3, fill=255)
    mask = mask.resize((w, h), Image.LANCZOS)
    out = Image.new('RGBA', (w, h), (0, 0, 0, 0)); out.paste(cimg, (0, 0), mask)
    p = f'{W}round_{name}.png'; out.save(p); return p

def spread(f):
    s = Image.open(f'{MAX2}IMG_{f}.png').convert('RGBA')
    bg = Image.new('RGBA', s.size, 'white'); bg.alpha_composite(s)
    return bg.convert('RGB')

def centered(c, y, parts, font, size, x0, x1):
    total = sum(pdfmetrics.stringWidth(t, font, size) for t, _ in parts)
    x = x0 + (x1 - x0 - total) / 2
    for t, col in parts:
        c.setFont(font, size); c.setFillColor(HexColor(col)); c.drawString(x, y, t)
        x += pdfmetrics.stringWidth(t, font, size)

def fit_size(text, font, size, maxw):
    while pdfmetrics.stringWidth(text, font, size) > maxw and size > 10:
        size -= 0.5
    return size

def xrange_for(page_no):
    left = page_no % 2 == 0
    return ((200, 2390) if left else (198, 2388))

def pt(px):
    return px / PX * 72

cover = Image.open(W + 'orig-01.png').convert('RGB')

# ---------- данные глав ----------
CH = [
 dict(num='Story One', num_es='Primera historia', en='The Zoo', es='El zoológico',
      title_img=('half', '2775', 'R', (150, 150, 2437, 1917)),
      icon=('half', '2775', 'R', (350, 100, 2250, 2000)),
      words=[('Lion', 'El león', ('half', '2735', 'R', (335, 200, 1540, 1405))),
             ('Giraffe', 'La jirafa', ('half', '2777', 'R', (900, 0, 2480, 1580))),
             ('Elephant', 'El elefante', ('half', '2778', 'R', (100, 0, 1773, 1673))),
             ('Monkey', 'El mono', ('half', '2374', 'L', (1004, 200, 2342, 1538))),
             ('Zebra', 'La cebra', ('half', '2780', 'R', (736, 268, 2007, 1539))),
             ('Parrot', 'El loro', ('half', '2780', 'L', (736, 803, 2342, 2409)))],
      qs=[('Which animal is the king of the animals?', '¿Qué animal es el rey de los animales?'),
          ('Why did Little Max climb a ladder?', '¿Por qué Pequeño Max subió una escalera?'),
          ('What can the Elephant do with his trunk?', '¿Qué puede hacer el elefante con su trompa?'),
          ('What did the Parrot say to Little Max?', '¿Qué le dijo el loro a Pequeño Max?')]),
 dict(num='Story Two', num_es='Segunda historia', en='The Beach', es='La playa',
      title_img=('spread', '2208', None, (400, 250, 3506, 2650)),
      icon=('half', '2208', 'L', (300, 450, 2100, 2250)),
      words=[('Dolphin', 'El delfín', ('half', '2209', 'L', (250, 1150, 1400, 2300))),
             ('Sand castle', 'El castillo de arena', ('half', '2209', 'R', (150, 1350, 1250, 2450))),
             ('Crab', 'El cangrejo', ('half', '2210', 'L', (1400, 1450, 2500, 2550))),
             ('Turtle', 'La tortuga', ('half', '2210', 'R', (250, 850, 1850, 2450))),
             ('Ship', 'El barco', ('half', '2211', 'R', (200, 250, 2300, 2350))),
             ('Seashell', 'La concha', ('half', '2213', 'R', (1750, 1225, 2450, 1925)))],
      qs=[('What did Little Max build on the beach?', '¿Qué construyó Pequeño Max en la playa?'),
          ('What is the Turtle’s house called?', '¿Cómo se llama la casita de la tortuga?'),
          ('What can you hear if you put a shell to your ear?', '¿Qué puedes escuchar si acercas una concha a tu oído?'),
          ('What does Little Max want to be when he grows up?', '¿Qué quiere ser Pequeño Max cuando crezca?')]),
 dict(num='Story Three', num_es='Tercera historia', en='The Fair', es='La feria',
      title_img=('half', '2792', 'L', (0, 300, 2588, 2300)),
      icon=('half', '2792', 'L', (1000, 650, 2300, 1950)),
      words=[('Ferris wheel', 'La rueda de la fortuna', ('half', '2789', 'R', (1950, 0, 2587, 637))),
             ('Cotton candy', 'El algodón de azúcar', ('cover', None, None, (1920, 1140, 2580, 1800))),
             ('Horse', 'El caballo', ('half', '2790', 'R', (1100, 800, 2500, 2200))),
             ('Clown', 'El payaso', ('half', '2791', 'R', (300, 450, 1500, 1650))),
             ('Balloon', 'El globo', ('half', '2791', 'L', (250, 50, 2450, 2250))),
             ('Drum', 'El tambor', ('half', '2793', 'R', (420, 1480, 1560, 2620)))],
      qs=[('What is the big wheel at the fair called?', '¿Cómo se llama la gran rueda de la feria?'),
          ('What did the clown give Little Max?', '¿Qué le regaló el payaso a Pequeño Max?'),
          ('What toy did Little Max get?', '¿Qué juguete le regalaron a Pequeño Max?'),
          ('What is the largest instrument called?', '¿Cómo se llama el instrumento más grande?')]),
 dict(num='Story Four', num_es='Cuarta historia', en='The Picnic', es='El pícnic',
      title_img=('half', '2796', 'R', (0, 400, 2587, 2399)),
      icon=('half', '2797', 'R', (600, 100, 2200, 1700)),
      words=[('Basket', 'La canasta', ('half', '2795', 'L', (1500, 1000, 2550, 2050))),
             ('Blanket', 'La manta', ('half', '2798', 'R', (250, 350, 1850, 1950))),
             ('Squirrel', 'La ardilla', ('half', '2796', 'L', (1150, 0, 2350, 1200))),
             ('Swing', 'El columpio', ('half', '2797', 'L', (250, 200, 1950, 1900))),
             ('Slide', 'El tobogán', ('half', '2797', 'R', (400, 500, 2525, 2625))),
             ('Cloud', 'La nube', ('half', '2798', 'R', (100, 1430, 1275, 2605)))],
      qs=[('What do you need to take on a picnic?', '¿Qué necesitas llevar a un pícnic?'),
          ('Which animals did Little Max see in the park?', '¿Qué animales vio Pequeño Max en el parque?'),
          ('What did Little Max do at the playground?', '¿Qué hizo Pequeño Max en la zona de juegos?'),
          ('What did the clouds look like?', '¿A qué se parecían las nubes?')]),
]

def get_img(spec):
    kind, f, side, box = spec
    if kind == 'half':
        return half(f, side), box
    if kind == 'spread':
        return spread(f), box
    return cover, box

# ---------- страницы ----------
def page_words(c, ch, idx):
    plants(c)
    x0, x1 = pt(200), pt(2390); cw = x1 - x0
    y = PAGE_H - 95
    centered(c, y, [(ch['en'], EN), ('  ·  ', RING), (ch['es'], ES)], 'BalB', 28, x0, x1)
    y -= 42
    centered(c, y, [('New Words', EN), ('  ·  ', RING), ('Palabras nuevas', ES)], 'BalB', 19, x0, x1)
    D = 92; y_top = y - 22; col_w = cw / 3
    for i, (en, es, spec) in enumerate(ch['words']):
        from circles import cropped
        img = cropped(en)
        path = circle_img(img, (0, 0, img.width, img.height), f'w{idx}_{i}')
        r, k = divmod(i, 3)
        cx = x0 + col_w * (k + 0.5); top = y_top - r * 150
        c.drawImage(path, cx - D / 2, top - D, D, D, mask='auto')
        c.setStrokeColor(HexColor(RING)); c.setLineWidth(2.5); c.circle(cx, top - D / 2, D / 2 + 1, stroke=1, fill=0)
        s1 = fit_size(en, 'Bal', 17, col_w - 8); s2 = fit_size(es, 'Bal', 17, col_w - 8)
        s = min(s1, s2)
        c.setFont('Bal', s); c.setFillColor(HexColor(EN)); c.drawCentredString(cx, top - D - 20, en)
        c.setFillColor(HexColor(ES)); c.drawCentredString(cx, top - D - 39, es)
    y = y_top - 2 * 150 - 42
    centered(c, y, [('Questions', EN), ('  ·  ', RING), ('Preguntas', ES)], 'BalB', 19, x0, x1)
    se = ParagraphStyle('e', fontName='Bal', fontSize=16, leading=19, textColor=HexColor(EN), leftIndent=20, firstLineIndent=-20)
    ss = ParagraphStyle('s', fontName='Bal', fontSize=16, leading=19, textColor=HexColor(ES), leftIndent=20, spaceAfter=11)
    yy = y - 22
    for n, (e, s) in enumerate(ch['qs'], 1):
        for txt, st, after in ((f'{n}.&nbsp;&nbsp;{e}', se, 0), (s, ss, 11)):
            p = Paragraph(txt, st); _, h = p.wrap(cw - 40, 500)
            p.drawOn(c, x0 + 40, yy - h); yy -= h + after
    return yy

def page_chapter(c, ch, idx, page_no):
    plants(c, shift=-90)
    x0, x1 = map(pt, xrange_for(page_no))
    y = PAGE_H - 110
    centered(c, y, [(ch['num'], EN), ('  ·  ', RING), (ch['num_es'], ES)], 'Bal', 20, x0, x1)
    centered(c, y - 62, [(ch['en'], EN)], 'BalB', 46, x0, x1)
    centered(c, y - 114, [(ch['es'], ES)], 'BalB', 46, x0, x1)
    img, box = get_img(ch['title_img'])
    path = rounded_img(img, box, f't{idx}')
    w = 470; h = w * (box[3] - box[1]) / (box[2] - box[0])
    cx = (x0 + x1) / 2; top = y - 150
    c.drawImage(path, cx - w / 2, top - h, w, h, mask='auto')
    c.setStrokeColor(HexColor(RING)); c.setLineWidth(3)
    c.roundRect(cx - w / 2, top - h, w, h, 70 / 1400 * w, stroke=1, fill=0)
    return top - h

CH_PAGES = [5, 21, 35, 51]

CONTENTS_STYLE = 'plain'

def _cloud(c, x, y, w, h):
    c.setStrokeColor(HexColor(RING)); c.setLineWidth(2); c.setFillColor(HexColor('#FFFFFF'))
    p = c.beginPath()
    bumps = [(-0.30, 0.05, 0.30), (0.0, 0.18, 0.36), (0.30, 0.05, 0.30), (-0.15, -0.20, 0.30), (0.17, -0.20, 0.30)]
    for dx, dy, r in bumps:
        c.circle(x + dx * w, y + dy * h, r * h, stroke=1, fill=1)
    for dx, dy, r in bumps:
        c.circle(x + dx * w, y + dy * h, r * h - 1.2, stroke=0, fill=1)

def page_contents(c, page_no):
    plants(c, shift=-110)
    x0, x1 = map(pt, xrange_for(page_no))
    y = PAGE_H - 100
    centered(c, y, [('In This Book', EN), ('  ·  ', RING), ('En este libro', ES)], 'BalB', 30, x0, x1)
    D = 104; row = 132; top = y - 40
    for i, ch in enumerate(CH):
        img, box = get_img(ch['icon'])
        path = circle_img(img, box, f'i{i}')
        cx = x0 + 80
        t = top - i * row
        c.drawImage(path, cx - D / 2, t - D, D, D, mask='auto')
        c.setStrokeColor(HexColor(RING)); c.setLineWidth(2.5); c.circle(cx, t - D / 2, D / 2 + 1, stroke=1, fill=0)
        tx = cx + D / 2 + 26
        c.setFont('Bal', 15); c.setFillColor(HexColor(EN)); c.drawString(tx, t - 30, ch['num'] + '  ·  ')
        c.setFillColor(HexColor(ES)); c.drawString(tx + pdfmetrics.stringWidth(ch['num'] + '  ·  ', 'Bal', 15), t - 30, ch['num_es'])
        c.setFont('BalB', 26); c.setFillColor(HexColor(EN)); c.drawString(tx, t - 62, ch['en'])
        c.setFillColor(HexColor(ES)); c.drawString(tx, t - 92, ch['es'])
        nx = x1 - 30; ny = t - D / 2
        num = str(CH_PAGES[i])
        if CONTENTS_STYLE == 'cloud':
            _cloud(c, nx, ny, 62, 44)
            c.setFont('BalB', 22); c.setFillColor(HexColor(EN)); c.drawCentredString(nx, ny - 8, num)
        else:
            c.setFont('BalB', 28); c.setFillColor(HexColor(EN)); c.drawRightString(x1 - 6, ny - 13, num)
    return top - 4 * row

TITLE_BLUE = '#0547B2'
TITLE_LIGHT = '#4095DD'

def _prep_title():
    t = np.asarray(Image.open('/mnt/user-data/uploads/Little_Max_Title_Final_8_5x11_300dpi.png').convert('RGB')).copy()
    t[t.min(axis=2) >= 248] = 255
    Image.fromarray(t).save(W + 'title_art.png')
    e = np.asarray(Image.open(W + 'emblem.png').convert('RGB')).copy()
    e[e.min(axis=2) >= 235] = 255
    Image.fromarray(e).save(W + 'emblem_clean.png')

def page_title(c):
    _prep_title()
    c.setFillColor(HexColor('#FFFFFF')); c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    scale = 0.9
    w_px, h_px = 2550 * scale, 3300 * scale
    cx_px = 1275                      # центр страницы без запаса (правая страница)
    top_px = 38 + 60
    c.drawImage(W + 'title_art.png', pt(cx_px - w_px / 2), PAGE_H - pt(top_px + h_px), pt(w_px), pt(h_px))
    # издательство внизу: две строки по центру
    cx = pt(cx_px)
    y1 = PAGE_H - pt(2990)
    c.setFont('BalB', 17); c.setFillColor(HexColor(TITLE_BLUE)); c.drawCentredString(cx, y1, '© Magic of Discoveries · 2026')
    c.setFont('Bal', 13); c.setFillColor(HexColor(TITLE_LIGHT)); c.drawCentredString(cx, y1 - 20, 'magicofdiscoveries.com')
    ybot = y1 - 20
    return ybot

DEAR = [
 ('This is the second book in the Little Max series. It is a bilingual book for children and their parents: every page tells the story in both English and Spanish.',
  'Este es el segundo libro de la serie Pequeño Max. Es un libro bilingüe para niños y sus padres: en cada página, la historia aparece en inglés y en español.'),
 ('Little Max shares four short stories about the zoo, the beach, the fair, and a picnic.',
  'Pequeño Max cuenta cuatro historias cortas sobre el zoológico, la playa, la feria y un pícnic.'),
 ('After each story, you will find a page with new words and a few simple questions. They will help your child remember the words and talk about what they have read.',
  'Después de cada historia, encontrarás una página con palabras nuevas y algunas preguntas sencillas. Ayudarán a tu hijo a recordar las palabras y a conversar sobre lo que ha leído.'),
 ('Read in one language or both — together with your child!',
  '¡Lean en un idioma o en los dos, juntos!'),
 ('Bright, colorful illustrations make each story even more enjoyable. I hope you and your child enjoy reading and discovering new things together. I wish you great success!',
  'Las ilustraciones alegres y llenas de color hacen que cada historia sea aún más divertida. ¡Espero que disfruten leyendo y descubriendo cosas nuevas juntos! ¡Les deseo mucho éxito!'),
]

def page_dear(c, page_no):
    c.setFillColor(HexColor('#FFFFFF')); c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    x0, x1 = map(pt, xrange_for(page_no)); cw = x1 - x0
    st = lambda col, al, f, s: ParagraphStyle('x', fontName=f, fontSize=s, leading=round(s * 1.3, 1), textColor=HexColor(col), alignment=al)
    top_lim = PAGE_H - pt(200); bot_lim = pt(3375 - 3120)
    avail = top_lim - bot_lim
    for size in (16, 15.5, 15, 14.5, 14, 13.5, 13):
        g_par = size * 1.1; g_lang = size * 0.3
        flows = [(Paragraph('Dear Reader,', st(EN, TA_CENTER, 'BalB', size + 5)), 0),
                 (Paragraph('Querido lector:', st(ES, TA_CENTER, 'BalB', size + 5)), 3)]
        for e, sp in DEAR:
            flows += [(Paragraph(e, st(EN, TA_LEFT, 'Bal', size)), g_par), (Paragraph(sp, st(ES, TA_LEFT, 'Bal', size)), g_lang)]
        flows += [(Paragraph('Best wishes,', st(EN, TA_RIGHT, 'Bal', size)), g_par * 1.4),
                  (Paragraph('Con mis mejores deseos,', st(ES, TA_RIGHT, 'Bal', size)), g_lang),
                  (Paragraph('Ricardo Demi', st(EN, TA_RIGHT, 'BalB', size + 1)), size * 0.5)]
        hs = []; total = 0
        for f, g in flows:
            _, h = f.wrap(cw, 1000); hs.append(h); total += g + h
        if total <= avail:
            break
    y = top_lim - (avail - total) / 2
    for (f, g), h in zip(flows, hs):
        y -= g; f.drawOn(c, x0, y - h); y -= h
    print('dear size', size, 'total', round(total), 'avail', round(avail))
    return total

def page_belongs(c):
    a = np.asarray(Image.open(W + 'orig-03.png').convert('RGB')).copy()
    bgc = a[100, 100].copy()
    a[520:860, :] = bgc
    img, kind = extend_top(Image.fromarray(a))
    img.save(W + 'belongs_full.jpg', quality=94, subsampling=0)
    c.drawImage(W + 'belongs_full.jpg', 0, 0, PAGE_W, PAGE_H)
    x0, x1 = map(pt, xrange_for(3))
    ybase = PAGE_H - pt(750 + 1132)
    centered(c, ybase + 130, [('This book belongs to', EN)], 'Bal', 32, x0, x1)
    centered(c, ybase + 86, [('Este libro pertenece a', ES_SKY)], 'Bal', 32, x0, x1)

def page_end(c, page_no):
    plants(c, shift=-90)
    x0, x1 = map(pt, xrange_for(page_no))
    y = PAGE_H - 130
    centered(c, y, [('The End', EN), ('  ·  ', RING), ('Fin', ES)], 'BalB', 48, x0, x1)
    img = half('2794', 'L')
    path = circle_img(img, (250, 350, 2450, 2550), 'end', size=1200)
    D = 330; cx = (x0 + x1) / 2; top = y - 45
    c.drawImage(path, cx - D / 2, top - D, D, D, mask='auto')
    c.setStrokeColor(HexColor(RING)); c.setLineWidth(3.5); c.circle(cx, top - D / 2, D / 2 + 1.5, stroke=1, fill=0)
    yb = top - D - 42
    centered(c, yb, [('See you soon!', EN)], 'BalB', 24, x0, x1)
    centered(c, yb - 32, [('¡Hasta pronto!', ES)], 'BalB', 24, x0, x1)
    return yb - 32

COPY_EN = ("All rights reserved. No part of this publication may be reproduced, distributed, or transmitted in any form or by any means, "
           "including photocopying, recording, or other electronic or mechanical methods, without the prior written permission of the publisher, "
           "except in the case of brief quotations embodied in critical reviews and certain other noncommercial uses permitted by copyright law.")
COPY_ES = ("Todos los derechos reservados. Ninguna parte de esta publicación o de la información que contiene puede ser citada o reproducida "
           "de ninguna forma por medios como la impresión, el escaneo, la fotocopia o cualquier otro, sin el permiso previo por escrito "
           "del titular de los derechos de autor.")

def page_copyright(c, page_no):
    c.setFillColor(HexColor('#FFFFFF')); c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    x0, x1 = map(pt, xrange_for(page_no)); cw = x1 - x0
    st = lambda col, f='Bal', s=10: ParagraphStyle('x', fontName=f, fontSize=s, leading=s * 1.35, textColor=HexColor(col), alignment=TA_CENTER)
    L = [
     ('Spanish-English Bilingual Short Stories for Kids and Beginners', EN, 'BalB', 12, 0),
     ('Where Have You Been, Little Max? / <font color="#1B44A0">¿Dónde has estado, Pequeño Max?</font>', EN, 'BalB', 12, 1),
     ('Full Color Illustrations', EN, 'Bal', 10, 1),
     ('Spanish – English Bilingual Edition · Edición bilingüe español – inglés', EN, 'Bal', 10, 3),
     ('Magic of Discoveries Series · Serie “La Magia de los Descubrimientos”', EN, 'Bal', 10, 3),
     ('Copyright © 2026 Ricardo Demi · Derechos de autor © 2026 Ricardo Demi', EN, 'Bal', 10, 3),
     (COPY_EN, EN, 'Bal', 10, 12),
     (COPY_ES, ES, 'Bal', 10, 6),
     ('Published by Magic of Discoveries LLC. · Publicado por Magic of Discoveries LLC.', EN, 'Bal', 10, 12),
     ('For permissions contact · Para la obtención de permisos, escríbenos: magicofdiscoveries@gmail.com', EN, 'Bal', 10, 3),
     ('ISBN: 978-1-963328-02-8', EN, 'BalB', 10, 3),
     ('First bilingual edition 2026 · Primera edición bilingüe 2026', EN, 'Bal', 10, 3),
     ('Disclaimer and Terms of Use: The author and the publisher do not hold any responsibility for errors, omissions or contrary interpretation of the subject matter herein. This book is presented solely for motivational and informational purposes only.', EN, 'Bal', 10, 12),
     ('Descargo de responsabilidad y condiciones de uso: El autor y la editorial no se responsabilizan de los errores, omisiones o interpretaciones contrarias del contenido de este libro. Este libro se presenta únicamente con fines motivadores e informativos.', ES, 'Bal', 10, 6),
    ]
    y = PAGE_H - 150
    for t, col, f, s, g in L:
        p = Paragraph(t, st(col, f, s)); _, h = p.wrap(cw, 500)
        y -= g; p.drawOn(c, x0, y - h); y -= h
    y -= 34
    centered(c, y, [('Also in the collection', EN), ('  ·  ', RING), ('También en la colección', ES)], 'BalB', 13, x0, x1)
    th = Image.open(W + 'book1_front.jpg')
    th.resize((1200, round(1200 * th.height / th.width)), Image.LANCZOS).save(W + 'thumb_book1.jpg', quality=95)
    w = 140; h = w * th.height / th.width
    tx = (x0 + x1) / 2 - w / 2; ty = y - 14 - h
    c.drawImage(W + 'thumb_book1.jpg', tx, ty, w, h)
    c.setStrokeColor(HexColor(RING)); c.setLineWidth(1.5); c.rect(tx, ty, w, h, stroke=1, fill=0)
    return ty


def page_number(c, n):
    left = n % 2 == 0
    cx = pt(165) if left else PAGE_W - pt(165)
    cy = pt(3375 - 3210)
    r = pt(40)
    c.setStrokeColor(HexColor(RING)); c.setLineWidth(1.5); c.setFillColor(HexColor('#FFFFFF'))
    c.circle(cx, cy, r, stroke=1, fill=1)
    size = 11 if n < 100 else 9
    c.setFont('BalB', size); c.setFillColor(HexColor(EN))
    c.drawCentredString(cx, cy - size * 0.36, str(n))
