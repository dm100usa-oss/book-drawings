# -*- coding: utf-8 -*-
"""Linejka. Meryaet gotovyy list i sravnivaet s etalonnymi ciframi.

Rabotaet s lyuboy knigoy i lyubym yazykom: meryaetsya raskladka, a ne slova.
Nuzhen tam, gde etalonnyy list so lvom sravnit ne s chem: vtoraya ispanskaya
kniga, angliyskie knigi.

Zapusk:
    python3 proverka_lista.py kniga.pdf 1

Vtoroy argument - nomer lista, schet ot edinicy. Esli ne ukazan, beretsya 1.
Pechataet kazhduyu merku: chto najdeno, chto dolzhno byt, i vyvod.
"""
import sys
import numpy as np
import pymupdf

DPI = 300
K = DPI / 72.0

# Etalonnye cifry. Vzyaty s pervoy ispanskoy knigi, list 1.
ETALON = {
    'stroka imeni, vysota':        (44.0, 1.5),
    'polosa shagov, verh':         (176.0, 1.5),
    'polosa shagov, niz':          (316.0, 1.5),
    'razdelitel':                  (328.0, 2.0),
    'ramka risovaniya, verh':      (360.0, 1.5),
    'ramka risovaniya, niz':       (628.0, 1.5),
    'ramka risovaniya, levyy kray': (212.0, 1.5),
    'ramka risovaniya, pravyy kray': (597.0, 1.5),
    # verhnyaya linejka propisi podnimaetsya u dlinnyh nazvaniy:
    # bukvy stanovyatsya nizhe, i linejki shodyatsya. Eto normalno.
    'propis, verhnyaya linejka':   (668.0, 10.0),
    'propis, nizhnyaya linejka':   (702.0, 1.5),
    'nomer stranicy, seredina':    (763.0, 2.0),
}


def load(path, page_no):
    doc = pymupdf.open(path)
    pg = doc[page_no - 1]
    pix = pg.get_pixmap(dpi=DPI)
    a = np.frombuffer(pix.samples, dtype=np.uint8)
    a = a.reshape(pix.height, pix.width, -1).mean(axis=2)
    return a < 200           # chernoe i seroe: ramki i punktir tozhe


def gorizontali(m, min_len_pt=150, sploshnaya=True):
    """Vysoty vseh dlinnyh gorizontalnyh linij na liste.

    sploshnaya: trebovat nepreryvnyy kusok nuzhnoy dliny. Dlya punktira
    i dlya ryada kletok eto trebovanie snimaetsya.
    """
    need = int(min_len_pt * K)
    out = []
    for y in range(m.shape[0]):
        row = m[y]
        if row.sum() < need:
            continue
        if sploshnaya:
            idx = np.where(row)[0]
            runs = np.split(idx, np.where(np.diff(idx) > int(6*K))[0] + 1)
            if max(len(r) for r in runs) < need:
                continue
        out.append(y / K)
    # sosednie stroki odnoy linii szhimaem v odnu
    res = []
    for y in out:
        if not res or y - res[-1] > 2:
            res.append(y)
    return res


def vertikali(m, y0, y1, min_len_pt=150):
    """Polozheniya dlinnyh vertikalnyh linij v poloce ot y0 do y1."""
    need = int(min_len_pt * K)
    band = m[int(y0*K):int(y1*K)]
    out = []
    for x in range(band.shape[1]):
        col = band[:, x]
        if col.sum() < need:
            continue
        out.append(x / K)
    res = []
    for x in out:
        if not res or x - res[-1] > 2:
            res.append(x)
    return res


def blizhayshaya(znacheniya, cel):
    if not znacheniya:
        return None
    return min(znacheniya, key=lambda v: abs(v - cel))


def main():
    path = sys.argv[1]
    page = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    m = load(path, page)

    # ryad kletok i ramki: eto ne odna nepreryvnaya liniya, poetomu
    # nepreryvnost ne trebuem
    gs = gorizontali(m, 150, sploshnaya=False)
    vs = vertikali(m, 380, 610, 200)

    print('Proverka lista %d iz %s' % (page, path))
    print('-' * 62)

    naydeno = {
        'stroka imeni, vysota': blizhayshaya(gorizontali(m, 100, sploshnaya=False), 44.0),
        'polosa shagov, verh': blizhayshaya(gs, 176.0),
        'polosa shagov, niz': blizhayshaya(gs, 316.0),
        'razdelitel': blizhayshaya(gorizontali(m, 300, sploshnaya=False), 328.0),
        'ramka risovaniya, verh': blizhayshaya(gs, 360.0),
        'ramka risovaniya, niz': blizhayshaya(gs, 628.0),
        'ramka risovaniya, levyy kray': blizhayshaya(vs, 212.0),
        'ramka risovaniya, pravyy kray': blizhayshaya(vs, 597.0),
        'propis, verhnyaya linejka': blizhayshaya(gs, 662.0),
        'propis, nizhnyaya linejka': blizhayshaya(gs, 702.0),
    }

    # nomer stranicy: kruzhok po centru lista
    # kruzhok nomera: eto beloe pyatno vnutri chernogo koltsa po centru lista.
    # Ishchem imenno beloe pyatno nuzhnogo razmera, togda trava podlozhki
    # ne meshaet zameru.
    from scipy import ndimage as _nd
    zona = m[int(730*K):int(795*K), int(275*K):int(337*K)]
    lab, n = _nd.label(~zona)
    naydeno['nomer stranicy, seredina'] = None
    for i in range(1, n + 1):
        ys_, xs_ = np.where(lab == i)
        h = (ys_.max() - ys_.min()) / K
        w = (xs_.max() - xs_.min()) / K
        if 24 < h < 40 and 24 < w < 46:
            naydeno['nomer stranicy, seredina'] = \
                (ys_.min() + ys_.max()) / 2 / K + 730
            break

    ploho = 0
    for k, (cel, dopusk) in ETALON.items():
        v = naydeno.get(k)
        if v is None:
            print('%-32s NE NAYDENO   dolzhno byt %.1f' % (k, cel))
            ploho += 1
            continue
        ok = abs(v - cel) <= dopusk
        print('%-32s %7.1f   dolzhno %6.1f   %s'
              % (k, v, cel, 'ok' if ok else 'NE SHODITSYA'))
        if not ok:
            ploho += 1

    # tolshchina chernogo i serogo v polose shagov
    pix = pymupdf.open(path)[page-1].get_pixmap(
        dpi=DPI, clip=pymupdf.Rect(10, 176, 602, 316))
    a = np.frombuffer(pix.samples, dtype=np.uint8)
    a = a.reshape(pix.height, pix.width, -1).mean(axis=2)
    from scipy import ndimage
    for name, mask, cel in (('chernoe v shagah', a < 90, 0.85),
                            ('seroe v shagah', (a >= 90) & (a < 200), 0.62)):
        if not mask.any():
            print('%-32s NE NAYDENO' % name)
            ploho += 1
            continue
        d = ndimage.distance_transform_edt(mask)
        t = 2 * d[d > 0].mean() / K
        ok = abs(t - cel) <= 0.12
        print('%-32s %7.2f   dolzhno %6.2f   %s'
              % (name, t, cel, 'ok' if ok else 'NE SHODITSYA'))
        if not ok:
            ploho += 1

    print('-' * 62)
    if ploho == 0:
        print('Raskladka sovpadaet s etalonom polnostyu.')
    else:
        print('Ne sovpadaet merok: %d. Iskat prichinu do prodolzheniya raboty.'
              % ploho)


if __name__ == '__main__':
    main()
