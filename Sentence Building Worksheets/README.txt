BUILD A SENTENCE. Передача проекта, английская книга готова.

Что в архиве:

BRIEF.md
   Главный файл. Прочитать целиком перед началом работы.
   Состояние проекта, принятые решения, состав книги,
   план испанской версии, список задач.

Build-a-Sentence-Animals-A-Z.pdf
   Готовая английская книга, 46 страниц, формат Letter.

scripts/
   build_book.py       сборка всей книги в один PDF
   letters.py          скелеты букв с порядком написания
   build_sentence2.py  одиночный лист, черновик

fonts/
   SchoolPrint-Regular.ttf       обычный текст
   SchoolPrintBold-Regular.ttf   вопрос
   SchoolPrintHeavy-Regular.ttf  буква в уголке
   JosefinSans-Variable.ttf      исходник, из него сделаны первые три
   Baloo2-Variable.ttf           название листа
   Quicksand-Variable.ttf        мелкие служебные подписи

   Скопировать в ~/.fonts и выполнить fc-cache -f

Первая задача в новом чате: переделать пару букв в правом
верхнем углу листа. Подробности в BRIEF.md, раздел 3.
