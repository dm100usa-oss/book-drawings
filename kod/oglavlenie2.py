# -*- coding: utf-8 -*-
"""Stranica dlya uchitelya i oglavlenie na dvuh stranicah."""
import pymupdf, build as B, detect, vec
from vec import fit, bbox, replay2

import os
W, H = 612.0, 792.0
LANG = os.environ.get('LANG_BOOK', 'en')       # en ili es: yazyk slova v knige
OFF = int(os.environ.get('OFF', '3'))          # skolko stranic idet pered listami
WORD = 'Spanish' if LANG == 'es' else 'English'
CLASSES = ('Spanish Classes  |  Dual Language & Immersion Classrooms  |  Art Centers'
           if LANG == 'es' else
           'English Classes  |  ESL & Newcomer Support  |  Art Centers')

FB = B.FB
FM = B.FM
FH = B.FH


def fig_paths(doc, spi):
    """Gotovyy risunok temy: posledniy shag."""
    _, steps, _ = detect.analyze_steps_page(doc[spi], doc)
    _ord = B.STEP_ORDER.get(spi)
    if _ord and len(_ord) == len(steps):
        steps = [steps[j - 1] for j in _ord]
    return steps[-1]


def teacher_page(out, n):
    pg = out.new_page(width=W, height=H)
    x0, x1 = 56, W - 56
    y = 62
    pg.insert_text((x0, y), 'Ready to Use All Year Long',
                   fontsize=23, fontfile=B.HEAD_FONT, fontname='H', color=(0, 0, 0))
    y += 30

    def para(text, size=11.0, lead=14.8, font='f/Quicksand-Medium.ttf', name='Q', gap=8):
        nonlocal y
        r = pymupdf.Rect(x0, y, x1, y + 400)
        used = pg.insert_textbox(r, text, fontsize=size, fontfile=font,
                                 fontname=name, lineheight=lead / size, align=0)
        y += (400 - used) + gap

    def head(text):
        nonlocal y
        y += 10
        pg.insert_text((x0, y), text, fontsize=14.5, fontfile=B.HEAD_FONT,
                       fontname='H', color=(0, 0, 0))
        y += 22

    # Vo vtoroy knige zadaniy 56, no v tekstah oni vsegda pishutsya kak
    # 55 plyus odno bonusnoe, kak v uzhe opublikovannoy knige.
    skolko = ('%d step-by-step directed drawing activities plus 1 bonus activity'
              % (n - 1)) if B.BOOK == 2 else ('%d step-by-step directed drawing activities' % n)
    para('%s for students in Grades K-2 (ages 5-8). Every activity comes with two '
         'worksheets, so you can hand each student the version that fits: %d '
         'worksheets in all. No prep needed. Choose a page, print, and go.'
         % (skolko, 2 * n))
    para('Themes include animals, sea life, fantasy characters, vehicles, sports, '
         'nature, and food, so there is plenty of variety all year.')

    head('Two Levels of the Same Activity')
    para('Level 1: the drawing area holds a light gray starting shape. Students trace '
         'it and add the rest, so their drawing looks like the sample and they finish '
         'the page on their own.', gap=5)
    para('Level 2: the drawing area is empty. Students build the whole drawing '
         'themselves, step by step.', gap=5)
    para('Every worksheet is marked Level 1 or Level 2 in the top right corner, so '
         'printed pages are easy to sort.', gap=5)
    para('You decide which level each student gets. Many teachers use Level 1 early in '
         'the year and Level 2 later, which makes growth easy to show.')

    head('How Each Activity Works')
    para('1.  Follow the Steps: Students see how a drawing is built step by step using '
         'simple lines and shapes.', gap=6)
    para('2.  Trace: Students trace the completed drawing, reinforcing hand movements '
         'and building confidence before drawing independently.', gap=6)
    para('3.  Draw & Color: Students recreate the drawing on their own and then color it.', gap=6)
    para(('4.  Trace & Write: Students trace and independently write the %s word, '
          'reinforcing vocabulary and handwriting.') % WORD, gap=6)

    head('For Early Finishers')
    para('Small themed illustrations and lettering on each page can also be colored, '
         'giving early finishers more to do on their own.')

    head('Perfect For')
    para(CLASSES + '  |  Independent Work  |  Morning Work  |  Learning Centers  |  '
         'Early Finishers  |  Sub Plans')

    head('Skills Practiced')
    para(WORD + ' Vocabulary  |  Handwriting  |  Fine Motor Skills  |  Hand-Eye Coordination  |  '
         'Following Step-by-Step Visual Directions  |  Independent Work  |  Drawing Confidence')

    y += 12
    itog = ('%d Activities + 1 Bonus' % (n - 1)) if B.BOOK == 2 else ('%d Activities' % n)
    pg.insert_text((x0, y), '%s  |  2 Levels  |  %d Worksheets  |  '
                            'Grades K-2  |  No Prep  |  Print & Go' % (itog, 2 * n),
                   fontsize=12.5, fontfile=B.HEAD_FONT, fontname='H')


def draw_item(pg, doc, spi, name, num, cx, cy, cw, fig_h, num2=None):
    fr, fps = fig_paths(doc, spi)
    box = pymupdf.Rect(cx + 20, cy, cx + cw - 20, cy + fig_h)
    m = fit(fr, box)
    k = vec.mscale(m)
    for p in fps:
        c = detect.acol(p)
        w = (p.get('width') or 0) * k
        if c in (vec.GRAY, vec.GRAY2):
            if vec.col(p) == vec.WHITE:
                replay2(pg, [p], m, fill=(1, 1, 1), color=B.BLACK, width=w)
            elif p.get('fill') is not None:
                replay2(pg, [p], m, fill=B.BLACK, color=None, width=w)
            else:
                replay2(pg, [p], m, fill=None, color=B.BLACK, width=w)
        else:
            replay2(pg, [p], m,
                    fill=vec.col(p) if p.get('fill') is not None else None,
                    color=p.get('color'), width=w)
    # pod risunkom stoyat dva nomera: list Level 1 i list Level 2
    nums = str(num) if num2 is None else '%d \u00b7 %d' % (num, num2)
    tw = FM.text_length(name, 9.4)
    nw = FB.text_length(nums, 9.4)
    sx = cx + (cw - tw - nw - 6) / 2
    ty = cy + fig_h + 11
    pg.insert_text((sx, ty), name, fontsize=9.4,
                   fontfile='f/Quicksand-Medium.ttf', fontname='Q', color=(0, 0, 0))
    pg.insert_text((sx + tw + 6, ty), nums, fontsize=9.4,
                   fontfile=B.HEAD_FONT, fontname='H', color=(0, 0, 0))


SECTIONS_1 = [
    ('Animals', 20), ('Sea Life', 8), ('Fantasy', 5), ('Vehicles', 4),
    ('Sports and Hobbies', 4), ('Things', 3), ('Nature', 5), ('Food', 6),
]
SECTIONS_2 = [
    ('Animals', 14), ('Bugs and Little Creatures', 5), ('Sea Life', 8),
    ('Fantasy', 6), ('Vehicles', 4), ('Sports and Hobbies', 4), ('Things', 2),
    ('Nature', 5), ('Food', 8),
]
SECTIONS = SECTIONS_1 if B.BOOK == 1 else SECTIONS_2


def ranges_strip(pg, y, mx):
    """Razdely v strochku: nazvanie i nomera listov."""
    items, i = [], 1 + OFF
    n = sum(c for _, c in SECTIONS)
    for title, cnt in SECTIONS:
        items.append((title, '%d-%d \u00b7 %d-%d'
                      % (i, i + cnt - 1, i + n, i + cnt - 1 + n)))
        i += cnt
    fs, gap, sp = 11.5, 20.0, 5.0
    lines, cur, w = [], [], 0.0
    lim = W - 2 * mx
    for t, r in items:
        iw = FH.text_length(t, fs) + sp + FM.text_length(r, fs)
        if cur and w + gap + iw > lim:
            lines.append((cur, w)); cur, w = [], 0.0
        if cur:
            w += gap
        cur.append((t, r, iw)); w += iw
    if cur:
        lines.append((cur, w))
    for row, rw in lines:
        x = mx + (lim - rw) / 2
        for t, r, iw in row:
            pg.insert_text((x, y), t, fontsize=fs, fontfile=B.HEAD_FONT,
                           fontname='H', color=(0, 0, 0))
            pg.insert_text((x + FH.text_length(t, fs) + sp, y), r, fontsize=fs,
                           fontfile='f/Quicksand-Medium.ttf', fontname='Q',
                           color=(0.3, 0.3, 0.3))
            x += iw + gap
        y += 19
    return y


def contents_pages(out, doc, themes):
    per_row, rows = 4, 7
    per_page = per_row * rows
    mx = 40.0
    cw = (W - 2 * mx) / per_row
    for part in range(2):
        pg = out.new_page(width=W, height=H)
        top = 104.0
        if part == 0:
            t = "What's Inside"
            tw = FH.text_length(t, 23)
            pg.insert_text(((W - tw) / 2, 88), t, fontsize=23, fontfile=B.HEAD_FONT,
                           fontname='H', color=(0, 0, 0))
            note = 'Each activity has two worksheets. Page numbers below: Level 1 \u00b7 Level 2'
            nw_ = FM.text_length(note, 10.5)
            pg.insert_text(((W - nw_) / 2, 108), note, fontsize=10.5,
                           fontfile='f/Quicksand-Medium.ttf', fontname='Q',
                           color=(0.35, 0.35, 0.35))
            top = ranges_strip(pg, 134.0, mx) + 16.0
        ch = (H - top - 40) / rows
        fig_h = ch - 20
        for j in range(per_page):
            i = part * per_page + j
            if i >= len(themes):
                break
            spi, name = themes[i]
            cx = mx + (j % per_row) * cw
            cy = top + (j // per_row) * ch
            draw_item(pg, doc, spi, name, i + 1 + OFF, cx, cy, cw, fig_h,
                      num2=i + 1 + OFF + len(themes))


def main(out_path):
    doc = pymupdf.open(B.SRC)
    out = pymupdf.open()
    teacher_page(out, len(B.THEMES))
    contents_pages(out, doc, B.THEMES)
    out.save(out_path, garbage=4, deflate=True)
    print('sohraneno', out_path)


if __name__ == '__main__':
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else '/home/claude/nachalo.pdf')
