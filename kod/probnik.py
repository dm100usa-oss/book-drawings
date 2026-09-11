# -*- coding: utf-8 -*-
"""Besplatnyy probnik pervoy angliyskoy knigi: oblozhka, stranica s opisaniem
i vosem zadaniy, kazhdoe srazu v dvuh urovnyah."""
import pymupdf, build as B

W, H = 612.0, 792.0
HEAD = B.HEAD_FONT
# Nomera tem v knige. Vzyaty iz uzhe opublikovannyh probnikov: po odnomu
# zadaniyu iz kazhdoy temy.
TEMY = ([1, 24, 30, 35, 41, 42, 47, 50] if B.BOOK == 1 else
        [2, 18, 22, 32, 36, 40, 42, 48, 49])
VSEGO = len(B.THEMES)                       # skolko zadaniy v polnoy knige
TEMY_SPISOK = ('Animals 20, Sea Life 8, Fantasy 5, Vehicles 4, Sports and Hobbies 4, '
               'Things 3, Nature 5, and Food 6' if B.BOOK == 1 else
               'Animals 14, Bugs and Little Creatures 5, Sea Life 8, Fantasy 6, '
               'Vehicles 4, Sports and Hobbies 4, Things 2, Nature 5, and Food 8')
SKOLKO = ('%d activities' % VSEGO if B.BOOK == 1
          else '%d activities plus 1 bonus activity' % (VSEGO - 1))
ITOG = ('%d Activities' % VSEGO if B.BOOK == 1
        else '%d Activities + 1 Bonus' % (VSEGO - 1))


def tekst_stranica(out):
    pg = out.new_page(width=W, height=H)
    x0, x1 = 56.0, W - 56.0
    y = 80.0

    def para(t, size=11.0, lead=14.2, font='f/Quicksand-Medium.ttf', name='Q', gap=7):
        nonlocal y
        r = pymupdf.Rect(x0, y, x1, y + 500)
        used = pg.insert_textbox(r, t, fontsize=size, fontfile=font, fontname=name,
                                 lineheight=lead / size, align=0)
        y += (500 - used) + gap

    def head(t, size=14.2, gap=6):
        nonlocal y
        y += gap
        pg.insert_text((x0, y), t, fontsize=size, fontfile=HEAD, fontname='H')
        y += 19

    n = len(TEMY)
    pg.insert_text((x0, 60), 'FREE SAMPLE | %d ACTIVITIES | 2 LEVELS' % n,
                   fontsize=24, fontfile=HEAD, fontname='H')
    para('This free sample includes %d step-by-step directed drawing activities from '
         'the full resource of %s for students in Grades K-2 (ages 5-8). Every '
         'activity comes with two worksheets, so this sample holds %d worksheets in '
         'all. No prep needed. Choose a page, print, and go.' % (n, SKOLKO, 2 * n))
    para('The %d activities are one from each theme in the book, so you can see the '
         'full range before you decide.' % n, gap=6)

    head('Two Levels of the Same Activity')
    para('Level 1: the drawing area holds a light gray starting shape. Students trace '
         'it and add the rest, so their drawing looks like the sample and they finish '
         'the page on their own.', gap=5)
    para('Level 2: the drawing area is empty. Students build the whole drawing '
         'themselves, step by step.', gap=5)
    para('Every worksheet is marked Level 1 or Level 2 in the top right corner.', gap=5)
    para('You decide which level each student gets. Many teachers use Level 1 early '
         'in the year and Level 2 later, which makes growth easy to show.')

    head('How Each Activity Works')
    para('1. Follow the Steps: Students see how a drawing is built step by step using '
         'simple lines and shapes.', gap=5)
    para('2. Trace: Students trace the completed drawing, reinforcing hand movements '
         'and building confidence before drawing independently.', gap=5)
    para('3. Draw & Color: Students recreate the drawing on their own and then color it.', gap=5)
    para('4. Trace & Write: Students trace and independently write the English word, '
         'reinforcing vocabulary and handwriting.')

    head('For Early Finishers')
    para('Small themed illustrations and lettering on each page can also be colored, '
         'and there is room around the finished drawing to add a scene: trees, grass, '
         'rocks, the sun, clouds, or anything students imagine.')

    head('Perfect For')
    para('English Classes | ESL & Newcomer Support | Art Centers | Independent Work | '
         'Morning Work | Learning Centers | Early Finishers | Sub Plans')

    head('Skills Practiced')
    para('English Vocabulary | Handwriting | Fine Motor Skills | Hand-Eye Coordination | '
         'Following Step-by-Step Visual Directions | Independent Work | Drawing Confidence')

    y += 4
    pg.insert_text((x0, y), '%d FREE ACTIVITIES | 2 LEVELS | %d WORKSHEETS | GRADES K-2 | NO PREP'
                   % (n, 2 * n), fontsize=12, fontfile=HEAD, fontname='H')
    y += 22
    head('Like This Free Sample?', gap=0)
    para('The complete resource has %s and %d worksheets across those same themes: '
         '%s. Available in our store.' % (ITOG, 2 * VSEGO, TEMY_SPISOK))


def main(kniga, staryy_probnik, out_path):
    kn = pymupdf.open(kniga)
    st = pymupdf.open(staryy_probnik)
    out = pymupdf.open()
    out.insert_pdf(st, from_page=0, to_page=0)      # oblozhka prezhnyaya
    tekst_stranica(out)
    for t in TEMY:
        out.insert_pdf(kn, from_page=t + 2, to_page=t + 2)                    # Level 1
        out.insert_pdf(kn, from_page=t + 2 + VSEGO, to_page=t + 2 + VSEGO)    # Level 2
    out.save(out_path, garbage=4, deflate=True)
    print('sohraneno', out_path, out.page_count, 'stranic')


if __name__ == '__main__':
    if B.BOOK == 1:
        main('/mnt/user-data/outputs/directed-drawing-worksheets-grades-k-2-letter-8.5x11.pdf',
             '/home/claude/sait/public/free/directed-drawing-k2-en-free-sample.pdf',
             '/mnt/user-data/outputs/directed-drawing-k2-en-free-sample.pdf')
    else:
        main('/mnt/user-data/outputs/directed-drawing-worksheets-grades-k-2-volume-2-letter-8.5x11.pdf',
             '/home/claude/sait/public/free/directed-drawing-k2-2-en-free-sample.pdf',
             '/mnt/user-data/outputs/directed-drawing-k2-2-en-free-sample.pdf')
