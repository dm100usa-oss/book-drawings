# -*- coding: utf-8 -*-
"""Sborka vtoroy ispanskoy knigi: 56 listov."""
import pymupdf, shablon, build as B

P = '/home/claude/podlozhka_%s.png'
ZEMLYA, LES, MORE, SKAZKA, GOROD, KUHNYA = (P % s for s in
    ('zemlya', 'les', 'more', 'skazka', 'gorod', 'kuhnya'))

# kakaya podlozhka na kakuyu temu
SCENA = {
    # Les i polyana: lesnye i domashnie zveri, nasekomye, vsya priroda
    'Murcielago': LES, 'Mapache': LES, 'Oso': LES, 'Zorro': LES,
    'Gallina': LES, 'Vaca': LES, 'Castor': LES, 'Aguila': LES,
    'Hamster': LES, 'Gato': LES, 'Perro': LES, 'Ardilla': LES,
    'Pato': LES, 'Ciervo': LES,
    'Raton': LES, 'Abeja': LES, 'Libelula': LES, 'Caracol': LES, 'Mariposa': LES,
    'Chichon': LES, 'Cacto': LES, 'Muguete': LES, 'Loto': LES, 'Tulipan': LES,
    # More: vodnye zhiteli, korabli i plyazhnye veshchi
    'Hipocampo': MORE, 'Foca': MORE, 'Pez payaso': MORE, 'Molusco': MORE,
    'Ajolote': MORE, 'Pez globo': MORE, 'Camaron': MORE, 'Raya': MORE,
    'Nave': MORE, 'Submarino': MORE, 'Pelota de playa': MORE, 'Gafas': MORE,
    # Skazka
    'Grifo': SKAZKA, 'Trole': SKAZKA, 'Hada': SKAZKA, 'Caldera magica': SKAZKA,
    'Sombrero de mago': SKAZKA, 'Pocion magica': SKAZKA,
    # Gorod: transport, veshchi, uvlecheniya
    'Cohete': GOROD, 'Scooter': GOROD, 'Camara': GOROD, 'Tambor': GOROD,
    'Regalo': GOROD, 'Gamepads': GOROD,
    # Kuhnya: eda
    'Guinda': KUHNYA, 'Aguacate': KUHNYA, 'Fresa': KUHNYA, 'Pera': KUHNYA,
    'Pina': KUHNYA, 'Limon': KUHNYA, 'Calabaza': KUHNYA, 'Bunuelo': KUHNYA,
}

import unicodedata


def key(name):
    return unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode()


def main(a=0, b=55, out_path='/home/claude/kniga2.pdf'):
    doc = pymupdf.open(B.SRC)
    out = pymupdf.open()
    for i in range(a, b):
        spi, name = B.THEMES[i]
        k = key(name)
        # Globo vstrechaetsya dvazhdy: vozdushnyy shar i globus
        png = SCENA.get(k)
        if png is None:
            print('NET SCENY:', name)
            continue
        shablon.sheet(out, doc, spi, name, png, page_no=i + 1)
        print(i + 1, name, 'ok', flush=True)
    out.save(out_path, garbage=4, deflate=True)
    print('sohraneno', out_path)


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        main(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3])
    else:
        main()
