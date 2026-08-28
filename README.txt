BUILD A SENTENCE. Английская книга готова.

Общая карта репозитория лежит в CHITAT-PERVYM.md. Начните с неё.

BRIEF.md
   Бриф этого проекта. Прочитать целиком перед началом работы.

Build-a-Sentence-Animals-A-Z.pdf
   Готовая книга: 57 страниц, из них 55 рабочих листов.
   Формат Letter, весь алфавит A-Z по два листа на букву,
   плюс три бонусных листа.

letter-corner/
   Буквы для обводки: 52 буквы с пунктиром, стрелками и номерами
   движений, программы их сборки, готовый лист для проверки
   и три шрифта. Читать letter-corner/CHITAT-PERVYM.md.

scripts/
   build_book.py        сборка всей книги в один PDF
   letters.py           старые скелеты букв, книгой больше не используются
   thicken.py           подгонка толщины линии новых рисунков
   build_sentence2.py   одиночный лист, ранний черновик

fonts/
   SchoolPrint-Regular.ttf       обычный текст
   SchoolPrintBold-Regular.ttf   вопрос
   SchoolPrintHeavy-Regular.ttf  старый шрифт для буквы в уголке,
                                 книгой больше не используется
   JosefinSans-Variable.ttf      исходник трёх предыдущих
   Baloo2-Variable.ttf           название листа
   Quicksand-Variable.ttf        мелкие служебные подписи

   Скопировать в ~/.fonts, затем fc-cache -f

newart/
   Новые рисунки от Рикардо. Файлы *_fix.png готовы к работе,
   у них уже подогнана толщина линии. Рядом лежат исходники.
