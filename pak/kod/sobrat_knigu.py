# -*- coding: utf-8 -*-
"""Sborka pervoy angliyskoy knigi: 55 listov."""
import pymupdf, shablon, build as B

P = '/home/claude/podlozhka_%s.png'
ZEMLYA, LES, MORE, SKAZKA, GOROD, KUHNYA = (P % s for s in
    ('zemlya', 'les', 'more', 'skazka', 'gorod', 'kuhnya'))

# kakaya podlozhka na kakuyu temu
SCENA = {
    # Pervaya angliyskaya kniga. Podlozhki vzyaty s utverzhdennoy pervoy
    # ispanskoy knigi: list v list.
    # Savanna i pole
    'Lion': ZEMLYA, 'Elephant': ZEMLYA, 'Zebra': ZEMLYA, 'Parrot': ZEMLYA,
    'Crocodile': ZEMLYA, 'Monkey': ZEMLYA, 'Rhino': ZEMLYA, 'Flamingo': ZEMLYA,
    'Lemur': ZEMLYA, 'Hummingbird': ZEMLYA, 'Chameleon': ZEMLYA,
    'Giraffe': ZEMLYA, 'Koala': ZEMLYA,
    # Les i polyana
    'Kangaroo': LES, 'Frog': LES, 'Alpaca': LES, 'Bunny': LES, 'Owl': LES,
    'Hedgehog': LES, 'Goat': LES,
    'Maple Leaf': LES, 'Rose': LES, 'Mushroom': LES, 'Clover': LES,
    'Sunflower': LES,
    # More i plyazh
    'Shark': MORE, 'Dolphin': MORE, 'Whale': MORE, 'Crab': MORE,
    'Octopus': MORE, 'Jellyfish': MORE, 'Sea turtle': MORE, 'Angelfish': MORE,
    'Beach umbrella': MORE, 'Beach hat': MORE,
    # Skazka
    'Mermaid': SKAZKA, 'Unicorn': SKAZKA, 'Dragon': SKAZKA, 'Crown': SKAZKA,
    'Dwarf': SKAZKA,
    # Gorod: transport, veshchi, uvlecheniya
    'Car': GOROD, 'Helicopter': GOROD, 'Airplane': GOROD,
    'Hot air balloon': GOROD, 'Skateboard': GOROD, 'Kite': GOROD,
    'Badminton': GOROD, 'American Football': GOROD, 'Globe': GOROD,
    # Kuhnya: eda
    'Cake': KUHNYA, 'Ice cream': KUHNYA, 'Watermelon': KUHNYA,
    'Carrot': KUHNYA, 'Broccoli': KUHNYA, 'Orange': KUHNYA,
    # --- Vtoraya angliyskaya kniga. Podlozhki vzyaty s utverzhdennoy vtoroy
    # ispanskoy knigi: list v list.
    # Les i polyana
    'Bat': LES, 'Raccoon': LES, 'Bear': LES, 'Fox': LES, 'Chicken': LES,
    'Cow': LES, 'Beaver': LES, 'Eagle': LES, 'Hamster': LES, 'Cat': LES,
    'Dog': LES, 'Squirrel': LES, 'Duck': LES, 'Deer': LES,
    'Mouse': LES, 'Bee': LES, 'Dragonfly': LES, 'Snail': LES, 'Butterfly': LES,
    'Pine cone': LES, 'Cactus': LES, 'Lily of the valley': LES, 'Lotus': LES,
    'Tulip': LES,
    # More i plyazh
    'Seahorse': MORE, 'Seal': MORE, 'Clown fish': MORE, 'Shellfish': MORE,
    'Axolotl': MORE, 'Pufferfish': MORE, 'Shrimp': MORE, 'Manta ray': MORE,
    'Ship': MORE, 'Submarine': MORE, 'Beach Ball': MORE, 'Sunglasses': MORE,
    # Skazka
    'Griffin': SKAZKA, 'Troll': SKAZKA, 'Fairy': SKAZKA,
    'Magic cauldron': SKAZKA, "Wizard's hat": SKAZKA, 'Magic potion': SKAZKA,
    # Gorod
    'Rocket': GOROD, 'Scooter': GOROD, 'Camera': GOROD, 'Drum': GOROD,
    'Present': GOROD, 'Gamepad': GOROD,
    # Kuhnya
    'Cherry': KUHNYA, 'Avocado': KUHNYA, 'Strawberry': KUHNYA, 'Pear': KUHNYA,
    'Pineapple': KUHNYA, 'Lemon': KUHNYA, 'Pumpkin': KUHNYA, 'Donut': KUHNYA,
}

import unicodedata


def key(name):
    return unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode()


def main(a=0, b=55, out_path='/home/claude/kniga_en.pdf'):
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
