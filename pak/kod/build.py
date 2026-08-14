import pymupdf, vec, detect, parts, skel, textpath, ribbon_shape
from vec import fit, bbox, replay, replay2

SRC = '/mnt/user-data/uploads/book_eng_print.pdf'
W, H = 612.0, 792.0
BLACK = (0.0, 0.0, 0.0)
vec.FATB = 0.35   # plotnost chernyh linij risunka
vec.GDARK = 0.67  # serye linii na tret temnee, tolshchina ta zhe
GRAY = (0.62, 0.62, 0.62)
LGRAY = (0.72, 0.72, 0.72)

FB = pymupdf.Font(fontfile='f/Quicksand-Bold.ttf')
FM = pymupdf.Font(fontfile='f/Quicksand-Medium.ttf')
FH = pymupdf.Font(fontfile='/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf')

THEMES_1 = [
    # KNIGA 1 EN. Temy i ih poryadok povtoryayut pervuyu ispanskuyu knigu:
    # stranicy angliyskogo istochnika sovpadayut s ispanskim odin v odin.
    # Chislo v skobkah = nomer stranicy shagov, schet ot nulya.
    # Land animals (20)
    (9, u'Lion'), (11, u'Elephant'), (13, u'Zebra'), (15, u'Parrot'),
    (17, u'Crocodile'), (19, u'Monkey'), (21, u'Kangaroo'), (23, u'Rhino'),
    (25, u'Flamingo'), (27, u'Lemur'), (29, u'Hummingbird'), (31, u'Chameleon'),
    (33, u'Giraffe'), (35, u'Koala'), (37, u'Frog'), (39, u'Alpaca'),
    (41, u'Bunny'), (43, u'Owl'), (45, u'Hedgehog'), (47, u'Goat'),
    # Aquatic animals (8)
    (87, u'Shark'), (89, u'Dolphin'), (91, u'Whale'), (93, u'Crab'),
    (95, u'Octopus'), (97, u'Jellyfish'), (99, u'Sea turtle'), (101, u'Angelfish'),
    # Fantasy (5)
    (119, u'Mermaid'), (121, u'Unicorn'), (123, u'Dragon'), (125, u'Crown'),
    (127, u'Dwarf'),
    # Vehicles (4)
    (141, u'Car'), (143, u'Helicopter'), (145, u'Airplane'),
    (147, u'Hot air balloon'),
    # Sports and hobbies (4)
    (157, u'Skateboard'), (159, u'Kite'), (161, u'Badminton'),
    (163, u'American Football'),
    # Things (3)
    (173, u'Beach umbrella'), (175, u'Beach hat'), (177, u'Globe'),
    # Nature (5)
    (183, u'Maple Leaf'), (185, u'Rose'), (187, u'Mushroom'), (189, u'Clover'),
    (191, u'Sunflower'),
    # Food (6)
    (203, u'Cake'), (205, u'Ice cream'), (207, u'Watermelon'), (209, u'Carrot'),
    (211, u'Broccoli'), (213, u'Orange'),
]

THEMES_2 = [
    # KNIGA 2 EN. Ostavshiesya 56 tem. Poryadok povtoryaet vtoruyu ispanskuyu
    # knigu: pervye tri temy postavleny po prosbe zakazchika.
    # Land animals (14)
    (53, u'Bear'), (55, u'Fox'), (49, u'Bat'), (51, u'Raccoon'),
    (57, u'Chicken'), (59, u'Cow'), (61, u'Beaver'), (63, u'Eagle'),
    (65, u'Hamster'), (67, u'Cat'), (69, u'Dog'), (71, u'Squirrel'),
    (73, u'Duck'), (75, u'Deer'),
    # Insects and bugs (5)
    (77, u'Mouse'), (79, u'Bee'), (81, u'Dragonfly'), (83, u'Snail'),
    (85, u'Butterfly'),
    # Aquatic animals (8)
    (103, u'Seahorse'), (105, u'Seal'), (107, u'Clown fish'), (109, u'Shellfish'),
    (111, u'Axolotl'), (113, u'Pufferfish'), (115, u'Shrimp'), (117, u'Manta ray'),
    # Fantasy (6)
    (129, u'Griffin'), (131, u'Troll'), (133, u'Fairy'), (135, u'Magic cauldron'),
    (137, u"Wizard's hat"), (139, u'Magic potion'),
    # Vehicles (4)
    (149, u'Ship'), (151, u'Submarine'), (153, u'Rocket'), (155, u'Scooter'),
    # Sports and hobbies (4)
    (165, u'Camera'), (167, u'Drum'), (169, u'Beach Ball'), (171, u'Sunglasses'),
    # Things (2)
    (179, u'Present'), (181, u'Gamepad'),
    # Nature (5)
    (193, u'Pine cone'), (195, u'Cactus'), (197, u'Lily of the valley'),
    (199, u'Lotus'), (201, u'Tulip'),
    # Food (8)
    (215, u'Cherry'), (217, u'Avocado'), (219, u'Strawberry'), (221, u'Pear'),
    (223, u'Pineapple'), (225, u'Lemon'), (227, u'Pumpkin'), (229, u'Donut'),
]

# Kakuyu knigu sobiraem. Zadaetsya peremennoy okruzheniya BOOK.
import os
BOOK = int(os.environ.get('BOOK', '1'))
THEMES = THEMES_1 if BOOK == 1 else THEMES_2

# Rod slova beretsya iz knigi, ne ugadyvaetsya. Zdes tolko zhenskiy rod.
FEM = {
    u'gallina', u'vaca', u'ardilla', u'abeja', u'lib\u00e9lula', u'mariposa',
    u'foca', u'raya',
    u'caldera m\u00e1gica', u'poci\u00f3n m\u00e1gica', u'nave', u'c\u00e1mara',
    u'pelota de playa',
    u'guinda', u'fresa', u'pera', u'pi\u00f1a', u'calabaza',
}

# Slova vo mnozhestvennom chisle: u nih artikl los ili las.
PLURAL_F = {u'gafas'}
PLURAL_M = {u'gamepads'}

# geometry taken from the sample worksheet
MX0, MX1 = 10.0, 602.0
STEP_Y0, STEP_Y1 = 159.0, 304.0
DIV1, DIV2 = 317.0, 620.0
VDIV = 230.0
BOX = pymupdf.Rect(240, 367, 593, 644)
FRAME = pymupdf.Rect(10, 668, 602, 786)
ROW = 40.0
LY1 = 762.0
LX0, LX1 = 22.0, 488.0
TRACE_FONT = 'f/JosefinSans.ttf'
HEAD_FONT = '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'


# Corners. By default every sheet gets the leaves from the approved sample.
# The list below is the exception: pages whose own corner art I checked by eye
# and which suits the theme better than leaves.
OWN_CORNERS = {
    u'Tiburón', u'Delfín', u'Ballena', u'Cangrejo', u'Pulpo', u'Medusa', u'Tortuga', u'Pez ángel',
    u'Sirena', u'Unicornio', u'Dragón', u'Corona', u'Gnomo',
    u'Máquina', u'Helicóptero', u'Avión', u'Globo',
    u'Monopatín', u'Cometa', u'Bádminton', u'Fútbol americano',
    u'Sombrilla de playa', u'Sombrero',
}


def txt(page, x, y, s, font, size, color=BLACK, center=None):
    if center is not None:
        x = center - font.text_length(s, size) / 2
    tw = pymupdf.TextWriter(page.rect)
    tw.append((x, y), s, font=font, fontsize=size)
    tw.write_text(page, color=color)


def manual_dashes(page, a, b, y, origin, dash=4.5, gap=13.8, color=(0.6, 0.6, 0.6), width=1.1):
    """Dashes drawn as real segments on a single grid, identical on every sheet."""
    per = dash + gap
    k = int((a - origin) // per)
    x = origin + k*per
    sh = page.new_shape()
    while x < b:
        s0, s1 = max(x, a), min(x + dash, b)
        if s1 > s0:
            sh.draw_line((s0, y), (s1, y))
        x += per
    sh.finish(color=color, width=width)
    sh.commit()


def dashed_line(page, x0, y0, x1, y1, color=GRAY, width=0.9, d="[4 4] 0"):
    sh = page.new_shape()
    sh.draw_line((x0, y0), (x1, y1))
    sh.finish(color=color, width=width, dashes=d)
    sh.commit()


def ribbon(page, cx, y0, y1, tw_):
    """Lenta beretsya gotovoy formoy s obrazca zakazchika."""
    return ribbon_shape.draw(page, cx, (y0 + y1) / 2.0,
                             inner_h=52.0, inner_w=max(tw_ + 42, 196),
                             color=BLACK)


STEP_ORDER = {
    # Gamepad, page 182: the book numbers the drawings row by row, but the
    # drawing itself goes down the left column first and then the right one.
    # The grey lines prove it: step 3 repeats step 1, not step 2.
    181: [1, 3, 5, 2, 4, 6],
    # Edinorog, stranica 122: v knige shagi 2 i 3, a takzhe 4 i 5 stoyat
    # ne v tom poryadke, v kakom risuetsya loshadka.
    121: [1, 3, 5, 2, 4, 6],
    # Mashina, stranica 142: nomera stoyat ne v tom poryadke, v kakom
    # risuetsya mashina.
    141: [1, 3, 5, 2, 4, 6],
}

# Temy, u kotoryh chast shagov v knige narisovana slishkom melko,
# rebenok po nim nichego ne razberet. Takie shagi ubirayutsya,
# ostalnye ot etogo stanovyatsya krupnee.
DROP_STEPS = {
    133: [1],         # KNIGA 2. Hada: pervyy shag pochti tochka, po prosbe
                      # zakazchika ubran, ostalos sem shagov i oni krupnee
    119: [1, 3],      # Sirena: pervyy i tretiy shag pochti tochki
    185: [1, 3],      # Rosa: devyat shagov dlya lista mnogo
    189: [1, 3],      # Trebol: devyat shagov dlya lista mnogo
}

# Ruchnaya popravka vysoty otdelnyh shagov. Nuzhna tam, gde kniga narisovala
# seryy sled predydushchego shaga inache, chem sam shag, i sovmeshchenie idet
# ne po figure, a po krayu risunka. Klyuch: stranica shagov. Znachenie: nomer
# shaga i na skolko ego opustit, v edinicah knigi.
STEP_SHIFT = {
    81: {1: 74, 2: 74},    # Libelula: golova pervyh dvuh shagov stoyala vyshe
}

# Gotovaya figura v uglu lista: gde nuzhno, ee mozhno umenshit i razvernut.
# Klyuch: stranica shagov. Znachenie: vo skolko raz umenshit, i razvorachivat li.
FIG_FIX = {
    145: (0.85, True),   # Avion pikiroval na doma, razvernut v druguyu storonu
    # KNIGA 2. Razmer figury v uglu podognan po prosbe zakazchika:
    # gorodskie temy naezzhali na doma, a neskolko figur bylo melkovato.
    155: (0.85, False),  # Scooter
    165: (0.85, False),  # Camara
    181: (0.80, False),  # Gamepads
    153: (1.15, False),  # Cohete
    131: (1.10, False),  # Trole
    133: (1.10, False),  # Hada
}

SHORT = {'American Football': 'Football',
         'Beach umbrella': 'Umbrella',
         'Hot air balloon': 'Balloon'}

# pages whose own background gives no usable corner art (bunting on a string):
# these sheets take the leaves from the approved sample instead

A_EXCEPT = {'unicorn', 'unicycle', 'uniform', 'universe'}

# plural names take no article: "draw sunglasses", not "draw a sunglasses"
PLURAL = {'sunglasses'}


def article(name):
    """V angliyskom pered nazvaniem stoit the: 'draw the lion'.
    Podhodit i mnozhestvennomu chislu: 'draw the sunglasses'."""
    return u'the'


# Slova, kotorye v nazvanii vsegda pishutsya s bolshoy bukvy.
KEEP_CAPS = {'american'}


def low(name):
    """Nazvanie so strochnoy bukvy, no sobstvennye slova ostayutsya s bolshoy:
    'American Football' -> 'American football'."""
    return ' '.join(w if w.lower() in KEEP_CAPS else w.lower()
                    for w in name.split(' '))


def build_page(out, doc, spi, name):
    sp, pp = doc[spi], doc[spi+1]
    circles, steps, _ = detect.analyze_steps_page(sp, doc)
    order = STEP_ORDER.get(spi)
    if order and len(order) == len(steps):
        steps = [steps[j-1] for j in order]
    cpaths = parts.circle_paths(sp, circles)
    tpaths = parts.title_paths(sp)
    wpaths = parts.footer_word_paths(sp)
    trace = detect.trace_paths(pp)

    low, art = name.lower(), article(name)

    pg = out.new_page(width=W, height=H)

    dec = parts.top_decor(sp) if name in OWN_CORNERS else {}
    if dec:
        for k, dst in (('tl', pymupdf.Rect(-8, -10, 96, 92)),
                       ('tr', pymupdf.Rect(520, -10, 624, 88))):
            g = dec[k]
            replay2(pg, g, fit(bbox(g), dst), fill=LGRAY, color=None)
    else:
        replay2(pg, parts.etalon_decor(), pymupdf.Matrix(1, 0, 0, 1, 0, 0),
                fill=LGRAY, color=None)

    txt(pg, 14, 42, u'Nombre:', FB, 12.5)
    nx = 14 + FB.text_length(u'Nombre:', 12.5) + 8
    pg.draw_line((nx, 44), (250, 44), color=BLACK, width=1)

    tb = bbox(tpaths)
    th = 38.0
    tw_ = tb.width * (th / tb.height)
    inner = ribbon(pg, W/2, 54, 124, tw_)
    ty = (inner.y0 + inner.y1)/2 - th/2
    replay2(pg, tpaths, fit(tb, pymupdf.Rect(inner.x0, ty, inner.x1, ty+th)), fill=BLACK)

    txt(pg, 0, 152, f'Sigue los pasos para dibujar {art} {low}.'.replace('  ', ' '),
        FB, 13, center=W/2)

    # ---- steps: common scale, figure registered so it never jumps ----
    n = len(steps)
    gap = 5.0
    bw = (MX1 - MX0 - gap*(n-1)) / n
    inner_w = bw - 14
    inner_h = (STEP_Y1 - STEP_Y0) - 34

    # grey paths of step k are exactly the whole drawing of step k-1
    offs = [pymupdf.Point(0, 0)]
    ok = True
    for k in range(1, n):
        gp = [p for p in steps[k][1] if vec.col(p) in (vec.GRAY, vec.GRAY2)]
        prev, cur = steps[k-1][0], steps[k][0]
        a = bbox(gp) if gp else None
        same = a is not None and prev is not None and \
            abs(a.width - prev.width) < 0.35*max(a.width, prev.width) + 4 and \
            abs(a.height - prev.height) < 0.35*max(a.height, prev.height) + 4
        if same:
            # the grey lines of this step are the previous drawing; line the two
            # up by their centres, so a step stays put even where the book
            # redrew the figure at a slightly different size
            d = pymupdf.Point((prev.x0 + prev.x1)/2 - (a.x0 + a.x1)/2,
                              (prev.y0 + prev.y1)/2 - (a.y0 + a.y1)/2)
            offs.append(offs[k-1] + d)
        else:
            ok = False
            offs.append(offs[k-1] + pymupdf.Point(prev.x0 - cur.x0, prev.y0 - cur.y0))

    frame = None
    placed = []
    for k, (r, ps) in enumerate(steps):
        pr = pymupdf.Rect(r) + (offs[k].x, offs[k].y, offs[k].x, offs[k].y)
        placed.append(pr)
        frame = pr if frame is None else frame | pr
    mw = max(r.width for r, _ in steps)
    mh = max(r.height for r, _ in steps)
    if not ok or frame.width > 1.45*mw or frame.height > 1.45*mh:
        placed = [pymupdf.Rect((mw-r.width)/2, 0, (mw+r.width)/2, r.height) for r, _ in steps]
        frame = pymupdf.Rect(0, 0, mw, mh)
        offs = [pymupdf.Point(placed[k].x0 - steps[k][0].x0,
                              placed[k].y0 - steps[k][0].y0) for k in range(n)]

    import math
    ang, s = 0.0, min(inner_w/frame.width, inner_h/frame.height)
    for a in range(5, 50, 5):
        t = math.radians(a)
        rw = frame.width*math.cos(t) + frame.height*math.sin(t)
        rh = frame.width*math.sin(t) + frame.height*math.cos(t)
        sa = min(inner_w/rw, inner_h/rh)
        if sa > s*1.001:
            ang, s = float(a), sa
    if ang and s < 1.30*min(inner_w/frame.width, inner_h/frame.height):
        ang, s = 0.0, min(inner_w/frame.width, inner_h/frame.height)
    fcx, fcy = (frame.x0+frame.x1)/2, (frame.y0+frame.y1)/2

    for i, (r, ps) in enumerate(steps):
        bx = MX0 + i*(bw+gap)
        box = pymupdf.Rect(bx, STEP_Y0, bx+bw, STEP_Y1)
        pg.draw_rect(box, color=BLACK, width=1.2, radius=0.07)
        if ps:
            bcx = bx + bw/2
            bcy = STEP_Y0 + 27 + inner_h/2
            m = (pymupdf.Matrix(1, 0, 0, 1, offs[i].x - fcx, offs[i].y - fcy)
                 * pymupdf.Matrix(ang)
                 * pymupdf.Matrix(s, 0, 0, s, 0, 0)
                 * pymupdf.Matrix(1, 0, 0, 1, bcx, bcy))
            replay(pg, ps, m)
        cb = pymupdf.Rect(circles[i])
        replay(pg, cpaths[i], fit(cb, pymupdf.Rect(bx+5, STEP_Y0+5, bx+25, STEP_Y0+25)))

    dashed_line(pg, MX0, DIV1, MX1, DIV1)

    txt(pg, 0, 345, f'Repasa {art} {low}.', FB, 13, center=(MX0+VDIV)/2)
    txt(pg, 0, 345, u'¡Ahora te toca a ti!', FB, 13, center=(VDIV+MX1)/2)
    txt(pg, 0, 362, f'Dibuja {art} {low} tú solo.', FM, 11.5, center=(VDIV+MX1)/2)
    dashed_line(pg, VDIV, 322, VDIV, 650)
    if trace:
        replay(pg, trace, fit(bbox(trace), pymupdf.Rect(20, 372, 220, 642)))

    pg.draw_rect(BOX, color=(0.75, 0.75, 0.75), width=1.2, radius=0.04)

    # ---- bottom block: trace & write ----
    pg.draw_rect(FRAME, color=BLACK, width=1.3, radius=0.075)

    head1 = u'Repasa y escribe la palabra '
    w1 = FH.text_length(head1, 14)
    w2 = FH.text_length(name, 18)
    hx = (FRAME.x0 + FRAME.x1)/2 - (w1 + w2)/2
    txt(pg, hx, 694, head1, FH, 14, color=(0.45, 0.45, 0.45))
    txt(pg, hx + w1, 694, name, FH, 18)

    polys, capH, ascH, xH, adv = skel.text_polylines(name, TRACE_FONT)
    sc = ROW / capH
    word_w = adv * sc
    z1w = max(140.0, word_w + 40)
    if (LX1 - LX0) - z1w - 18 < 120:
        z1w = (LX1 - LX0) - 138
        sc = (z1w - 40) / adv
        word_w = adv * sc

    z1 = (LX0, LX0 + z1w)
    vsp = z1[1] + 9
    z2 = (vsp + 9, LX1)

    ly0 = LY1 - capH * sc
    lym = (ly0 + LY1) / 2.0

    for (a, b) in (z1, z2):
        pg.draw_line((a, ly0), (b, ly0), color=BLACK, width=1.2)
        manual_dashes(pg, a, b, lym, LX0)
        pg.draw_line((a, LY1), (b, LY1), color=BLACK, width=1.2)
    dashed_line(pg, vsp, ly0 - 14, vsp, LY1 + 14, color=BLACK, width=1.0, d="[5 5] 0")

    wx = (z1[0] + z1[1])/2 - word_w/2
    sh = pg.new_shape()
    for p in polys:
        sh.draw_polyline([pymupdf.Point(wx + x*sc, LY1 - y*sc) for (x, y) in p])
    sh.finish(color=(0.225, 0.225, 0.225), width=2.6, dashes="[2.3 1.75] 0", closePath=False)
    sh.commit()

    fr, fps = steps[-1]
    if fps:
        m = fit(fr, pymupdf.Rect(502, 672, 594, 782))
        for p in fps:
            c = vec.col(p)
            if c in (vec.GRAY, vec.GRAY2):
                # seryy cvet menyaetsya na chernyy tam, gde on stoit v knige:
                # u odnih figur eto zalivka, u drugih obvodka. Esli vsegda
                # stavit zalivku, figura zakrashivaetsya celikom (medusa).
                if p.get('fill') is not None:
                    replay2(pg, [p], m, fill=BLACK, color=None)
                else:
                    replay2(pg, [p], m, color=BLACK)
            else:
                replay(pg, [p], m)


def main():
    doc = pymupdf.open(SRC)
    out = pymupdf.open()
    for spi, name in THEMES:
        build_page(out, doc, spi, name)
    out.save('book2.pdf', garbage=4, deflate=True)
    print('saved')

#main()
