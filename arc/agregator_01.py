import sys
import os

class Work_Files():

	def __init__(self, directory):
		self.directory = directory		
		self.get_work_files()


	def execute(self):
		self.global_header = self.get_global_header()
		self.normalize_workfiles() # приводим колонки с данными в файле в соответствие с заголовками колонок
		self.result_list = self.get_result_string_set()
		self.sort_arch_list()
		self.add_keystrings_to_result_list()
		self.add_header_to_result()
		return self.write_arch_list(self.directory)


	def get_work_files(self):
		"""
		формирует список объединяемых файлов. действует просто: если в указанной 
		директории есть файлы с расширением тхт, то проверяет его формат, 
		она добавляет их в список на объединение
		"""
		self.workfiles=[] # список файлов, которые будут объединены
		a = os.listdir(self.directory)
		for entry in a:
			if entry.endswith(".txt"):
				temp = Work_File(entry, self.directory) 
				if temp.valid_format:
					self.workfiles.append(temp) # если файл с расшиернием txt в выбранном каталоге удовлетворяет формату, он добавляется в список на объединение

	def get_global_header(self):
		'''
		Формрует заголовок для объединенного списка файлов.
		Окончательный заголовок является пересечением заголовков всех объединяемых файлов
		В него попадают только те столбцы, которые присутствуют во всех файлах
		'''
		global_header = set()
		for item in self.workfiles:
			if len(global_header)==0:
				global_header = item.headset
			else:
				global_header = global_header.intersection(item.headset)
		global_header = global_header.difference(set(Work_File.ESSENTIAL_FIELDS))
		global_header_list = sorted(list(global_header))
		global_header_list[:0] = Work_File.ESSENTIAL_FIELDS
		a = {i:global_header_list.index(i) for i in global_header_list}
		# возвращает словарь с названием колонки и номером этой колонки
		return a


	def normalize_workfiles(self):
		for item in self.workfiles:
			item.normalize_file_list(self.global_header)

	def get_result_string_set(self):
		result_set = set()	
		for item in self.workfiles:
			if len(result_set)==0:
				result_set = item.normal_set.copy()
			else:
				result_set = result_set.union(item.normal_set)
		return list(result_set)

	def sort_arch_list(self):
		self.result_list.sort(key = lambda x: x.split("\t")[0])
		self.result_list.sort(key = lambda x: x.split("\t")[1])

	def get_key_string(self, string):
		keywords=[]
		for item in self.workfiles:
			if string  in item.normal_set:
				keywords.append(item.keyword)
		k = ", ".join(keywords)
		return k

	def add_keystrings_to_result_list(self):
		for i in range(len(self.result_list)):
			keystring = self.get_key_string(self.result_list[i])
			self.result_list[i] = self.result_list[i] + "\t" + keystring

	def add_header_to_result(self):
		hl = []
		for i in sorted(self.global_header.items(), key = lambda x: x[1]):
			hl.append(i[0].capitalize())
		s = "\t".join(hl)
		s += "\tКлючевые фразы"
		self.result_list.insert(0, s)

	def write_arch_list(self, path):
		filename = os.path.join(path, "archivarius_list.csv")
		f_out=open(filename,  "w",  encoding="utf16")
		for i in self.result_list:
			f_out.write(i + "\n")
		f_out.close()
		return filename

class Work_File():
	EXTENT=[".docx", ".docm", ".odt", ".xlsx", ".xlsm", ".ods", ".sxc", ".xps", ".mdb"]
	ESSENTIAL_FIELDS = ["имя файла", "папка"]
	
	def __init__(self, st, path):
		self.path = os.path.join(path, st)
		self.keyword = os.path.splitext(st)[0]#удаляет у файла расширение и обрубок использует в качестве ключевого слова
		self.keyword = self.keyword.replace(',', "\u0326") # так как запятые - это разделители между ключемыми словами, 
		#внутри ключевых слов не должно быть запятых, заменяем их на что-то похожее
		self.file_list = [] # список файлов, ассоциированный с ключевым словом
		self.normal_set = set() #множестово строк в фале. Множество, чтобы легче было исключать повторяющиеся строки из других файлов
		# она присваивается в normalize_file_list, но нигде дальше не используется
		self.get_header()
		if not self.fullpath:
			self.get_file_list()
		else:
			self.get_file_list_fullpath()
		# зачем для восстановления docx передавать параметры с заголовками столбцов?
		self.restore_docx(self.headdic["имя файла"], self.headdic["папка"])

	def get_header(self):
		"""
		Читает первую строку файла арихивариуса, в которой должен располагаться 
		заголовок с перечислением столбцов.
		Кроме того, она различает, является ли этот файл списком архивариуса или 
		просто списком файлов (полных путей).
		Возвращает черыре параметра:
		valid_format(Bool) - пригоден ли файл для дальнейшей обработки.
		fullpath(Bool) - является ли файл списком файлов (либо архивариуса)
		hheaddic(словарь) - словарь столбцов, где названию столбца поставлен в 
		"""
		headstr = open(self.path, encoding="utf-16").readline()# первая строка, ищет заголовок
		headstr = headstr.rstrip()
		headstr = headstr.lower() # понижаем региср в заголовке для того, чтобы можно было нормально сравнивать
		headlist = headstr.split("\t")
		self.headset = set(headlist)
		# если есть полный путь, путь и файл, удаляем полный путь
		if ("полный путь" in self.headset) and self.headset.issuperset(set(Work_File.ESSENTIAL_FIELDS)):
			self.headset.discard("полный путь")
		# если есть только полный путь, ставим флаг для последующего разбития полного пути на части normalize_file_list
		if ("полный путь" in self.headset) and not self.headset.issuperset(set(Work_File.ESSENTIAL_FIELDS)):
			self.fullpath = True
		else:
			self.fullpath = False
		# путь присутствует: либо полный либо в виде пары путь-файл. правильный формат
		if ("полный путь" in self.headset) or self.headset.issuperset(set(Work_File.ESSENTIAL_FIELDS)):
			self.valid_format = True
			self.headdic = {headlist[i]: i for i in range(len(headlist))} #словарь заголовка, где названию столбца сопоставляется номер столбца
			
			
			# по названию столбца можно определить его номер
		else:
			self.valid_format = False

	def get_file_list(self):
		for f_str in open(self.path, encoding="utf-16").readlines():
			f = f_str.rstrip()
			f = f.split("\t")
			ffilename = (f[self.headdic["имя файла"]])
			if ffilename == "": # заменияет пустые имена файлов на "text.txt"
				f[self.headdic["имя файла"]] = "text.txt" # этот случай возникает при обработке почтовых файлов
			self.file_list.append(f) # добавляет строку к списку файлов
		self.file_list.pop(0) # выкидывает заголовко

	def get_file_list_fullpath(self):
		for f_str in open(self.path, encoding="utf-16").readlines():
			f = f_str.rstrip()
			f = f.split("\t")
			ffilename = os.path.basename(f[self.headdic["полный путь"]])
			if ffilename == "":
				ffilename = "text.txt" # получает имя файла
			
			fpath = os.path.dirname(f[self.headdic["полный путь"]])
			if not fpath.endswith("\\"): 
				fpath += "\\" # получает путь и бобавляет слэш, если что
			f.extend([fpath, ffilename]) # добавляет два новых столбца в строку
			self.file_list.append(f)
		self.file_list.pop(0)
		self.modify_header() 


	def modify_header(self):
		'''
		Вызывается только для файлов с абсолютными путями.
		Исправляет заголовок так, чтобы на два добавленных столбца можно было 
		ссылаться.
		По сути, добавляет в словарь заголовка две записи

		'''
		self.headdic.pop("полный путь")
		l = len(self.headdic)
		self.headdic["папка"] = l+1 #можно было поставить просто l
		self.headdic["имя файла"] = l + 2 # а тут l + 1 ?
		self.headset = set(self.headdic)
		print(self.headdic)


	def normalize_file_list(self, global_header):
		for f_str in self.file_list:

			s = [None for n in range(len(global_header))]
			for i in global_header:
				s[global_header[i]] = f_str[self.headdic[i]]
			string = "\t".join(s)
			self.normal_set.add(string)

	def restore_docx(self, filepos, pathpos):
		def is_docx(path):
			for i in Work_File.EXTENT:
				a= i+"|"
				if a in path:
					return i
			return None
		
		def check_docx_name(name):
			return name.lower() == "sharedstrings.xml"

		for u in self.file_list:
			spath = u[pathpos]
			doc_pattern = is_docx(spath)
			if doc_pattern is not None:
				splitted_path = spath.split("|")
				for i in range(len(splitted_path)):
					if doc_pattern in splitted_path[i]:
						nunber_of_fragment_with_pattern = i
						break
				new_path = "|".join(splitted_path[:nunber_of_fragment_with_pattern])
				splitted_fragment = splitted_path[nunber_of_fragment_with_pattern].split("\\")
				len_split = len(splitted_fragment)
				separ = "\\" if len_split > 1 else "|"

				u[filepos] = splitted_fragment[-1]

				rest_of_path = "\\".join(splitted_fragment[:-1])
				path_frags = [new_path, rest_of_path]
				for i in path_frags:
					if i == "":
						path_frags.remove(i)
				u[pathpos] = "|".join(path_frags) + separ
			elif check_docx_name(u[filepos]):
				splitted_path = spath.split("|")
				n_path = "|".join(splitted_path[:-1])
				splitted_path = n_path.split("\\")
				u[filepos] = splitted_path[-1]
				new_path = "\\".join(splitted_path[:-1])
				if not new_path.endswith("\\"):
					new_path += "\\"
				u[pathpos] = new_path


if __name__ == '__main__':
	a = Work_Files(sys.argv[1])
	print("="*40)
	for item in a.workfiles:
		print("%020s  :  %s" % (item.keyword, item.headdic))

	a.execute()
