import os
import pymupdf, json, sys, build as B, sobrat_knigu as S, level1

OFF = int(__import__("os").environ.get("OFF", "0"))


def main(out_path):
    starts = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'start%d.json' % B.BOOK)))
    doc = pymupdf.open(B.SRC)
    out = pymupdf.open()
    for i, (spi, name) in enumerate(B.THEMES):
        png = S.SCENA.get(S.key(name))
        level1.sheet(out, doc, spi, name, png, page_no=i+1+OFF, start=starts[str(spi)])
        level1.podpis(out[-1], 'Level 1')
        print(i+1, name, 'ok', flush=True)
    out.save(out_path, garbage=4, deflate=True)
    print('sohraneno', out_path)

main(sys.argv[1] if len(sys.argv) > 1 else '/home/claude/level1-vse.pdf')
