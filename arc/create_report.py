import sys
import os
import arc.report_template as rt
from collections import Counter

RESET_BUTTON_NAME = "Все файлы"
class Record:
    RECORDS_COUNTER = 0
    KEYWORDS_COUNTER = Counter()

    def __init__(self, string):
        '''
        Из-за того что программа читает файл copy.log полностью, включая заголовок
        Во-первых, заголовок нужно выкидывать,
        а во-вторых нужно помнить о выкинутом заголовке, если буду переходить на csv
        '''
        a = string.split("\t")
        self.rel_path = a[2]  # относительный путь, чтобы файл по клику открывался в браузере
        Record.RECORDS_COUNTER += 1
        self.record_number = Record.RECORDS_COUNTER
        keywords = a[3].strip()
        ke = keywords.split(", ")
        self.tooltip_keys = ke[:]
        ke.append(RESET_BUTTON_NAME)
        for i in range(len(ke)):
            # на этапе archivarius_list в списке ключевых слов запятые заменяются на похожий символ
            # потому что запятая может являться частью ключевого слова
            # а здесь запятые возвращаются назад
            ke[i] = ke[i].replace("\u0326", ',')
        self.keys = set(ke)
        self.KEYWORDS_COUNTER.update(self.keys)


def get_records_list(copy_log: str) -> list[Record]:
    """
	workfiles содержит относительные пути к скопированнымфайлам и списки
	ключевых слов для каждого файла
	"""
    workfiles = list()
    count = 0
    with open(copy_log, "r", encoding="utf16") as cl:
        for item in cl:
            if count > 0 :  # пропускаем заголовок файла
                r = Record(item)
                if "\\" in r.rel_path:
                    workfiles.append(r)
            count += 1
        return workfiles


def get_keywords_list(workfiles: list[Record]) -> dict[str, str]:
    key_set = set()
    keyword_dict = {}
    for item in workfiles:
        key_set.update(item.keys)
    all_keys = list(key_set)
    all_keys.sort(key=lambda x: x.lower())
    all_keys.insert(0, RESET_BUTTON_NAME)
    for n, kw in enumerate(all_keys):
        keyword_dict[kw] = f'keyword{n}'

    return keyword_dict



button_template = '<button class="button {0}" id="{1}" data-keyword="{2}">{3}</button>\n'

def make_buttons(keyword_dict: dict[str, str]) -> str:
    string = ''
    for key in keyword_dict:
        active = 'active' if key == RESET_BUTTON_NAME else ''
        data_kw = key
        button_name = f'{data_kw} ({Record.KEYWORDS_COUNTER[key]})'
        option = button_template.format(active, keyword_dict[key], data_kw, button_name)
        string += option
    return string


rec_temp = ''' <div class="{0}">
                <span class="number">({1})
                  <span class="tooltip">{2}</span>
                </span><a href="..\\{3}" target="_blank">{3}</a>
              </div>\n'''


def make_records(workfiles: list[Record], keyword_dict: dict[str, str]) -> str:
    string = ''
    for rec in workfiles:
        classes = [keyword_dict[k] for k in rec.keys]
        classes = 'record ' + ' '.join(classes)
        keywords = '<br>'.join(rec.tooltip_keys)

        record = rec_temp.format(classes, rec.record_number, keywords, rec.rel_path)
        string += record
    return string


def make_html(keyword_dict, workfiles):
    report_file = open("report.html", "w", encoding="utf-8")
    report_file.write(rt.begining)
    # формируем левое меню
    buttons_part = make_buttons(keyword_dict)
    report_file.write(buttons_part)
    report_file.write(rt.inter)
    records = make_records(workfiles, keyword_dict)
    report_file.write(records)
    report_file.write(rt.ending)


def create_all(copy_log, report_directory):
    """
	Создает HTML-отчет о копировании. Принимает путь к файлу copy.log и папку, куда записывать отчет
	"""
    os.chdir(report_directory)
    workfiles = get_records_list(copy_log)
    keyword_dict = get_keywords_list(workfiles)
    make_html(keyword_dict, workfiles)


if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("Необходим аргумент (файл copy.log).")
        sys.exit(1)
    else:
        arg = sys.argv[1]
        create_all(arg, ".")
