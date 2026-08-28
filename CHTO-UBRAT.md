# Две мелочи после выгрузки

## 1. Заменить один файл

`letter-corner/scripts/04-rebuild-letters.py`

В нём была ловушка. Если собрать не все буквы, а несколько, например
`python3 scripts/04-rebuild-letters.py "hn"`, то главный файл
`data/vec3/letters.json` перезаписывался только этими буквами,
а остальные пятьдесят пропадали.

Теперь программа дописывает собранные буквы в общий файл и в конце
показывает, сколько букв получилось. Должно быть 52.

## 2. Удалить лишнее

При выгрузке старые файлы остались рядом с новыми. Они не мешают работе,
но путают. Можно удалить прямо на сайте GitHub.

В папке `letter-corner/data/letters` удалить 27 файлов без приставки
up- или low-:

C.json F.json G.json J.json N.json Q.json R.json T.json U.json W.json
Y.json a.json b.json d.json e.json h.json i.json k.json l.json m.json
o.json p.json s.json v.json x.json z.json

Должно остаться 53 файла: 52 буквы с приставками и записка CHITAT.txt.

В папке `letter-corner/data` удалить папки `vec1` и `vec2`.
Это черновые сборки букв, они больше не нужны.

В папке `letter-corner/scripts` удалить старые программы:

addJ.py build2.py build_letters.py digits_map.py final_sheet.py
fixes.py limb.py measure.py mont.py norm2.py rebuild.py scan.py
thick.py zoom.py

Должно остаться шесть файлов с номерами от 01 до 06.

В папке `letter-corner` удалить `README.txt`, он от старой версии.
Актуальная записка это `CHITAT-PERVYM.md`.
