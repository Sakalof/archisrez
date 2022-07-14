import sys
import os
from arc import html_parts

class TetraGrammaKeyword():
	def __init__(self, all_words, workfiles):
		self.words = dict()
		self.words = {i:list() for i in all_words}

		for i in all_words:
			for entry in workfiles:
				if i in entry.keys:
					self.words[i].append(entry.rel_path)
		#отдельно формируется список всех файлов			
		self.words["Все ключевые фразы"] = list()
		for entry in workfiles: 
			self.words["Все ключевые фразы"].append(entry.rel_path)
		print("файлы распиханы по ключевым словам")


class Record_Keyword_List():
	# для чего добавляется строка "Все ключевые фразы"?
	def __init__(self,  string):
		a=string.split("\t")
		self.rel_path = a[2]# относительный путь, чтобы файл по клику открывался в браузере
		keywords = a[3].strip()
		ke = keywords.split(", ")
		for i in range(len(ke)):
			ke[i] = ke[i].replace("\u0326", ',')
		self.keys = set(ke)

def get_records_list(copy_log):
	'''
	workfiles содержит относительные пути к скопированнымфайлам и списки 
	ключевых слов для каждого файла
	'''
	workfiles = list()
	for item in open(copy_log, "r", encoding="utf16").readlines():
		workfiles.append(Record_Keyword_List(item))
		if "\\" not in workfiles[0].rel_path:
			workfiles.pop(0)
	return workfiles

def get_keywords_list(workfiles):
	# key_list в классе Record_Keyword_List тоже надо сделать сетом
	#"Все ключевые фразы" сначала удаляются, а потом добавляются, странно это
	#реализация с помощью set()
	#список всех ключевых слов без деления по файлам
	key_set=set()
	for item in workfiles:
		key_set.update(item.keys)
	all_keys = list(key_set)
	all_keys.sort()
	all_keys.insert(0, "Все ключевые фразы")
	return all_keys


def make_html(index_directory, all_keys, workfiles, TGKW):
	os.chdir(index_directory)
	html_parts.make_left_file(all_keys, TGKW)
	
	for key in all_keys:
		num_counter = 1
		html_parts.make_right_frame(key)
		html_parts.make_right_key(key)
		body_file= key + "_body.htm"
		file_rigth_body = open(body_file,  "w",  encoding = "utf-8")
		file_rigth_body.write(html_parts.right_head)
		for rel_path in TGKW.words[key]:
			file_rigth_body.write("<div class=file> (" +str(num_counter) + ") &nbsp;<a href='..\\" + rel_path + "'>" + rel_path + "</A></div>\n")
			num_counter += 1
		file_rigth_body.write(html_parts.right_tail)
		file_rigth_body.close()
	

def create_all(copy_log, otchet_directory):
	'''
	Создает HTML-отчет о копировании. Пинимает путь к файлу copy.log и папку, куда записываь отчет
	'''
	os.chdir(otchet_directory)
	index_directory = html_parts.make_index_dir()
	workfiles = get_records_list(copy_log)
	# all_keys - отсортированный список ключеывх слов
	all_keys = get_keywords_list(workfiles)
	TGKW = TetraGrammaKeyword(all_keys, workfiles)
	make_html(index_directory, all_keys, workfiles, TGKW)


if __name__ == '__main__':

	if len(sys.argv) < 2:
		print("Необходим аргумент (файл copy.log).")
		sys.exit(1)
	else:
		arg = sys.argv[1]
		create_all(arg, ".")
