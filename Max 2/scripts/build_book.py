import sys; sys.path.insert(0, '/home/claude/work')
from reportlab.pdfgen import canvas
from render_story import draw_story, CFG
from extras import *

OUT = '/home/claude/work/book.pdf'
c = canvas.Canvas(OUT, pagesize=(PAGE_W, PAGE_H), initialFontName='Bal', initialFontSize=12)
c.setTitle('Where Have You Been, Little Max? / ¿Dónde has estado, Pequeño Max?')
c.setAuthor('Ricardo Demi')
plan = []
rep = []
def add(desc, fn):
    fn()
    n = len(plan) + 1
    if n > 1:
        page_number(c, n)
    c.showPage(); plan.append(desc)

add('титул', lambda: page_title(c))
add('обращение', lambda: page_dear(c, 2))
add('эта книга принадлежит', lambda: page_belongs(c))
add('содержание', lambda: page_contents(c, 4))
old_ranges = [(4, 17), (18, 29), (30, 43), (44, 51)]
for i, (a, b) in enumerate(old_ranges):
    add(f'заголовок истории {i+1}', lambda i=i: page_chapter(c, CH[i], i, len(plan) + 1))
    for p in range(a, b + 1):
        add(f'история {i+1}, стр. {p} оригинала', lambda p=p: draw_story(c, p, rep))
    add(f'слова и вопросы {i+1}', lambda i=i: page_words(c, CH[i], i))
add('конец', lambda: page_end(c, len(plan) + 1))
add('права', lambda: page_copyright(c, len(plan) + 1))
c.save()
for n, d in enumerate(plan, 1):
    side = 'Л' if n % 2 == 0 else 'П'
    print(n, side, d)
print('не влезло:', [r for r in rep if r[1] != 16])
starts = [i + 1 for i, d in enumerate(plan) if d.startswith('заголовок')]
print('начала историй', starts, 'в содержании', CH_PAGES)
assert starts == CH_PAGES
