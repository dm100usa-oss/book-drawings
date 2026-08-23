BUILD A SENTENCE. Английская книга готова.

BRIEF.md
   Главный файл. Прочитать целиком перед началом работы.

Build-a-Sentence-Animals-A-Z.pdf
   Готовая книга: 57 страниц, из них 55 рабочих листов.
   Формат Letter, весь алфавит A-Z по два листа на букву,
   плюс три бонусных листа.

scripts/
   build_book.py        сборка всей книги в один PDF
   letters.py           скелеты букв с порядком написания
   thicken.py           подгонка толщины линии новых рисунков
   build_sentence2.py   одиночный лист, ранний черновик

fonts/
   SchoolPrint-Regular.ttf       обычный текст
   SchoolPrintBold-Regular.ttf   вопрос
   SchoolPrintHeavy-Regular.ttf  буква в уголке
   JosefinSans-Variable.ttf      исходник трёх предыдущих
   Baloo2-Variable.ttf           название листа
   Quicksand-Variable.ttf        мелкие служебные подписи

   Скопировать в ~/.fonts, затем fc-cache -f

newart/
   Новые рисунки от Рикардо. Файлы *_fix.png готовы к работе,
   у них уже подогнана толщина линии. Рядом лежат исходники.
