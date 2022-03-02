﻿help_text = '''02.03.2022
v 0.54
Автор: Соколов Дмитрий
mail: sakalof@mail.ru
Telegram: @sakalof


	Программа предназначена для облегчения работы компьютерных экспертов. Она осуществляет копирование файлов на основе файл-списков Архивариуса  и формирует HTML-отчет о копировании.

	Небольшое вступление: программа работает с текстовыми файлами только в кодировке "UTF-16". "Архивариус 3000" архивариус создает списки именно в такой кодировке, а вот со списками из других программ нужно быть внимательнее. 
Чтобы архисрез корректно отработал одт начала до конца необходимы следующие устовия:
	1) Кодировка Unicode, как уже говорилось. 
	2) Касширение файлов: TXT.
	3) Столбцы в файл-списках должны разделяться знаками табуляции "\\t".
	4) Наличие заголовка в первой строке (то есть столбцы должны быть подписаны, чтобы программа их различала)
	5) Столбцы могут идти в произвольном порядке, главное, чтобы в каждой строке был путь - одним столбцом или парой "имя файла" - "папка".

	Во время поиска ключевых слов в Архивариусе обнаруженные файлы нужно сохранять следующим образом: «экспорт списка» > “экспортировать в текстовый файл”. В качестве имени файл-списка вводить ключевое слово или фразу. Списки нужно сохранять в один каталог.

	Программа разделена на три секции, каждая из которых осуществляет свой этап обработки обнаруженных файлов:
	1) Формирование сводного списка файлов.
	2) Копирование файлов в выбранный каталог.
	3) Создание HTML-отчета для удобного просмотра скопированных файлов.

	Этапы можно выполнять последовательно, либо произвести одну из операций выборочно.

	Первая секция программы собирает все списки архивариуса, сформированные по разным ключевым словам и выводит в один файл. Файлы должны лежать  в одном каталоге и иметь расширение «тхт». Другие файлы с таким расширением в данный каталог лучше не писать, так как они тоже будут приняты в обработку и исказят результат. На выходе получается файл «archivarius_list.csv» который пишется всё в ту же папку. В этом файле: 1) убраны повторяющиеся строки; 2) сами сроки отсортированы по  путям в алфавитном порядке; 3) к конце каждой строки приведен список ключевых фраз, встречающихся в данном файле, что для следователя может оказаться полезным. Итоговый список имеет формат «csv» и без проблем открывается в редакторах таблиц. 

	Кроме того программа исправляет ошибочное представление некоторых файлов в списках Архивариуса. Например, файл с расширением "xlsx" воспринимается Архивариусом как архив, содержащий xml-файл. Соответственно, копируется не документ целиком, а xml-вложение. Архисрез данную ситуацию исправляет.

	Так же с помощью этой секции можно переводить список абсолютных путей в формат вида "имя файла" - "папка". Файл может быть один или несколько — так как на данном этапе программа требует имя имя папки с файлами, а файлы ищет сама. Если файлов в папке несколько, программа их объединит, выбросив повторяющиеся строки, если файл один — отстртирует список файлов по путям. Получившийся список можно использовать для копирования файлов во второй секции.

	Вторая секция осуществляет копирование файлов.  Копирование может осуществляться на основе списка «archivarius_list.csv», созданного на первом этапе работы программы. Так же можно копировать, подсунув программе файл-список архивариуса либо простто список файлов (файл, содержащий список абсолютных путей без заголовка впервой строке ). Копирование происходит с сохранением структуры каталогов. Если файлы находятся в архивах  ”zip” “rar”, “iso” и т. д., они так же распаковываются. Причем архивы могут быть произвольной вложенности. Вложения из почтовых архивов программа, к сожалению, не достает. На данном этапе программа генерирует два отчета. “copy.log” содержит список всех скопированных файлов. Кроме того этот файл на третьем этапе работы программы испльзуется необходим для формирования HTML-отчета.  “error.log” содержит список файлов, при копировании которых произошли ошибки. Для ручного разбора проблемы, так сказать. Если файл, содержащийся в архиве не удается распаковать, то весь архив не копируется, просто в лог записывается ошибка. Для работы данной секции необходимо указать, куда скопировать файлы и при необходимости выбрать файл-список (если осуществлялся первый этап, то  файл «archivarius_list.csv» подставляется автоматически).

	Третья секция формирует  HTML-отчет, для удобного просмотра скопированных файлов. В отчете файлы разделены по ключевым словам, и при нажатии на имя файла он, как правило, открывается в браузере или в сторонней программе. Обычно поля данной секции заполняются автоматически, и нужно просто нажать на «выполнить». Но если необходимо только сгенерировать отчет, нужно указать файл  “copy.log”.

	Буду признателен за сообщения об ошибках и конструктивную критику.'''
