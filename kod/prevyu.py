# -*- coding: utf-8 -*-
"""Prevyu dlya ploshchadki: stranica uchitelya, dva lista oglavleniya i tri
lista zadaniy s vodyanym znakom. Pokazany oba urovnya odnogo risunka."""
import pymupdf, math, build as B

N = len(B.THEMES)
# Vtoraya tema v dvuh urovnyah i poslednyaya tema obychnym urovnem.
LISTY = [5, 5 + N, 3 + N + N]


def znak(pg, text='PREVIEW', size=54, ugol=-20.0, cx=404.0, cy=500.0,
         cvet=(0.72, 0.72, 0.72)):
    """Vodyanoy znak poperek polya risovaniya."""
    f = pymupdf.Font(fontfile=B.HEAD_FONT)
    w = f.text_length(text, size)
    tw = pymupdf.TextWriter(pg.rect)
    tw.append((cx - w / 2, cy), text, font=f, fontsize=size)
    t = math.radians(ugol)
    m = (pymupdf.Matrix(1, 0, 0, 1, -cx, -cy)
         * pymupdf.Matrix(math.cos(t), math.sin(t), -math.sin(t), math.cos(t), 0, 0)
         * pymupdf.Matrix(1, 0, 0, 1, cx, cy))
    tw.write_text(pg, color=cvet, morph=None, matrix=m)


def main(kniga, out_path):
    kn = pymupdf.open(kniga)
    out = pymupdf.open()
    out.insert_pdf(kn, from_page=0, to_page=2)        # uchitel i dva lista oglavleniya
    for nomer in LISTY:
        out.insert_pdf(kn, from_page=nomer - 1, to_page=nomer - 1)
        znak(out[-1])
    out.save(out_path, garbage=4, deflate=True)
    print('sohraneno', out_path, out.page_count, 'stranic')


if __name__ == '__main__':
    if B.BOOK == 1:
        main('/mnt/user-data/outputs/directed-drawing-worksheets-grades-k-2-letter-8.5x11.pdf',
             '/mnt/user-data/outputs/EN-book-1-PREVIEW.pdf')
    else:
        main('/mnt/user-data/outputs/directed-drawing-worksheets-grades-k-2-volume-2-letter-8.5x11.pdf',
             '/mnt/user-data/outputs/EN-book-2-PREVIEW.pdf')
