import os
import sys
import shutil
import subprocess
import time
import re
import binascii
import logging
from typing import Dict, Optional

Global_cur_time = time.time()
Temp_Catalog = os.environ['TEMP'] + '\\archisrez'
if __name__ == '__main__':
	zip_path = '../z/'
else: 
	zip_path = './z/'

Prefix = str() 

class Str_entry():
	COPYLOG = None
	ERRORLOG = None
	#ARC_DICT: Dict[Optional[str]] = dict()
	ARC_DICT = dict()
	GLOBAL_COUNTER = 0
	UNZIP_OUTPUT = open('zip_output.txt', 'w', encoding = 'utf16')
	
	def __init__(self,  string):
		self.raw_str = string
		a = string.split("\t")
		if Str_entry.H_ABSPATH is None:
			self.filename = a[Str_entry.H_NAME]
			self.abspath = a[Str_entry.H_PATH].rstrip() + a[Str_entry.H_NAME].rstrip()
		else:
			#print("-*-*-*-*-*-*-*-*-*-*-*-*-*-*-")
			#print(a)
			#print(len(a))
			#print(Str_entry.H_ABSPATH)
			#print(a[Str_entry.H_ABSPATH])
			self.filename = os.path.basename(a[Str_entry.H_ABSPATH])
			self.abspath = a[Str_entry.H_ABSPATH].strip()
		if Str_entry.H_KEY is not None:
			self.keystring = a[Str_entry.H_KEY].strip()
		else:
			#self.keystring = None
			self.keystring = ""
		self.copied = False
		self.processed = False

	def copy(self):
		"""
		осуществляет копирование файла в указанную папку. При необходимости 
		разархивирует файл. Процедура верхнего уровня.
		"""
		#print("proc copy")
		self.processed = True
		if self.is_archived():
			source_path = self.extract_one_string()
			if source_path is None:
				return
			dest = self.get_dest_path_from_arch()
		else:
			source_path = self.abspath
			dest = self.abspath
		logging.debug(source_path)
		# Удолит эту отладочную информацию
		if not os.path.exists(source_path):
			logging.debug("file not found")
		#-------------------------------------------
		if os.path.exists(source_path):
			logging.debug("path exists")
			self.dest_path, self.relative_path = self.get_dest_dir(dest)
			self.make_dest_dir()
			if self.copy_file(source_path, self.dest_path):
				self.set_copied()

	def get_dest_dir(self, string):
		'''
		Создает путь, куда будет копироваться файл. Берет изначальный путь, убирает от буквы 
		диска двоеточие и пристегивает получившуюся строку к префиксу, то есть пути, куда 
		будут скопированы все файлы.
		'''
		dest_path = os.path.dirname(string)
		dest_srez = dest_path.replace(":", "") # заменяем двоеточие в названии диска на слэш
		relative_path = dest_srez
		dest_path = os.path.join(Prefix, dest_srez) # добавляем префикс
		return dest_path, relative_path
	
	def make_dest_dir(self):
		if not os.path.exists(self.dest_path):
			logging.debug(self.dest_path)
			try:
				os.makedirs(self.dest_path)
			except Exception as erka:
				print("Ошибка создания каталога %" % self.dest_path)
				logging.debug("ERROR CREATED DEST PATH" + str(erka))
			else:
				logging.debug("dest_path created")

	def is_archived(self):
		#print("proc is_archived")
		archived = "|"  in self.abspath
		archived2 = "/" in self.abspath
		archived = archived or archived2
		logging.debug(self.abspath)
		if archived:
			logging.debug("file is archived")
		return archived

	def extract_one_string(self):
		'''
		Осуществляет разархивирование файла, обрабатывая один или больше вложенных архивов
		'''
		"""
		Учитывая, что зачастую приходится копировать файлы из списка абсолютных путей ,который был создан в ТОТАЛЕ,
		возникает проблема с архивами. Архив там обозначается не пайпом, а обратным слешем. Поэтому в качестве 
		костыльного решения попробую пока переделать все бэкслеши в пайпы. Вдруг будет нормально работать
		"""
		#print("proc extract_one_string")
		self.abspath = self.abspath.replace("/","|")
		ap =self.abspath.split("|")# вначале представляет собой раздробленную по пайпам стрку, 
		#в конце процедуры представляет набор ссылок на архивы по ходу вложенности
		cur_path=ap[0]
		dict_flag = True
		for i in range(1, len(ap)):
			cur_path ="|".join([cur_path,  ap[i]])
			if dict_flag:
				if Str_entry.ARC_DICT.get(cur_path):
					ap[i] = Str_entry.ARC_DICT[cur_path]
				else:
					dict_flag = False
			if not dict_flag:	
				path = self.new_path(ap[i-1], ap[i])
				if path  is None:
					print("Ошибка распаковки")
					return None
				else:
					ap[i]=os.path.join(path, ap[i])
					if not ap[i] is ap[-1]:
						#кроме последней сторки, так как там лежит не архив а 
						#распакованный файл и записвывть его в список архивов бессмысленно
						Str_entry.ARC_DICT[cur_path]=ap[i]
			#print("AP\n",  ap)
		logging.debug("UNZIPPED PATH: %s" % ap[-1])
		return ap[-1]  # разархивированный конечный файл, кот. надо скопировать

	def new_path(self, arch, fil):
		'''
		распаковывает архив в новую папку и ворзвращает местоположение распакованного файла.
		arch - откуда распаковывать.
		fil - файл (с промежуточными каталогами) который надо распаковать
		pathn - каталог со случайным именем в который распаковывался файл из архива (возможно с подкаталогами)
		'''

		def arch_info(archive, un_file):
			command = '%s7z.exe l "%s" "%s" -slt' %(zip_path, archive,  un_file)
			po = subprocess.Popen(command,  stdout = subprocess.PIPE)
			listing = po.communicate()[0]
			listing	= listing.decode("cp866")
			return listing

		def get_hash_of_file_in_archive(archive, un_file):
			file_info = arch_info(archive, un_file)
			crc_dec = None
			shab = "CRC = (.+)" #ищет во всем выводе поэтому возвращает хэш с возвратом каретки
			g = re.findall(shab, file_info)
			if len(g)>0:
				a = g[0].rstrip() #избаавялемся от возврата каретки
				crc_dec = int(a, 16)# переводим из шестнадцатеричной в десятичную форму
			return crc_dec

		def check_file_crc(path):
			inp = open(path, "rb").read() 
			return binascii.crc32(inp)
		#print("proc new_path")
		Str_entry.GLOBAL_COUNTER += 1
		transit_path = os.path.join(Temp_Catalog,  str(Str_entry.GLOBAL_COUNTER)) # промежутчный каталог куда разархивируется файл
		command = '%s7z.exe x "%s" -y -o"%s" "%s"' %(zip_path,arch, transit_path, fil)
		#logging.debug(command)
		os.mkdir(transit_path)
		po = subprocess.Popen(command,  stdout = subprocess.PIPE, stdin = subprocess.PIPE)
		# этот энтер нужен на случай если архив хапросит пароль. Если его не ставить, выполнение 7z не завершится, 
		# он так и будет ожидать ввода пароля. Костыльный шаг, но довольно простой.
		po.stdin.write(b'\n')
		listing = po.communicate()[0]
		z7out=listing.decode("cp866")
		Str_entry.UNZIP_OUTPUT.write(z7out + '\n=====================================cheked\n')

		logging.debug(z7out)
		if "Everything is Ok" in z7out:
			return transit_path  
		else:
			pathn = os.path.join(transit_path, fil)
			
			if not os.path.exists(pathn):
				return None
			else:
				inner_crc = get_hash_of_file_in_archive(arch, fil)
				file_crc = check_file_crc(pathn)
				if	inner_crc == file_crc:
					return transit_path
				else:
					return None
						
		
		
	def get_dest_path_from_arch(self):
		'''
		возвращает путь в который надо скопировать  распакованный файл
		и само имя файла.
		'''
		arc_split = self.abspath.split("|")
		allem=[]
		for item in arc_split[:-1]:
			a=item.split("\\")
			a[-1]=a[-1] + "-ARCHIVE"
			allem.extend(a)
		dir_path = "\\".join(allem)
		addon_dirs = arc_split[-1].split("\\")[:-1] # папки внутри последнего архива, но не сам файл
		if len(addon_dirs) > 0:
			addon="\\".join(addon_dirs)
			dir_path = dir_path + "\\" + addon
		file_path = arc_split[-1].split("\\")[-1]
		return os.path.join(dir_path, file_path)

	def copy_file(self, source_path, dest_path):
		try:
			shutil.copy2(source_path, dest_path)
		except (EnvironmentError, TypeError, WindowsError, UnicodeEncodeError):
			result = False
		else:
			result = True
		return result

	def set_copied(self):
		global Global_cur_time
		self.copied = True
		dest_path = self.dest_path.replace("\\\\?\\", "")
		cur_file_time  = time.time()
		timedelta = cur_file_time - Global_cur_time
		timedelta = "%8.3f" % timedelta
		Global_cur_time = cur_file_time
		self.copy_str = self.abspath + "\t" + os.path.join(dest_path, self.filename)\
		 + "\t" + os.path.join(self.relative_path, self.filename) + "\t"\
		 + self.keystring + "\t" + timedelta +"\n"

	def write_log(self):
		if self.copied:
			Str_entry.COPYLOG.write(self.copy_str)
		else:
			Str_entry.ERRORLOG.write(self.abspath + "\n")


def init_from_utf16_file_list(path):
	# проверяем что файл содержит списик ключевых фраз
	# грубо говоря просто считает количество столбцов
	assert os.path.exists(path), "Файл  со списком путей не обнаружен"
	strings=[]
	for file in open(path, "r", encoding = "utf16").readlines():
		strings.append(Str_entry(file.rstrip()))
	return strings


def is_utf16_encoding(file):
	try:
		open(file, "r", encoding = "utf_16").readline()
	except UnicodeError:
		return False
	else:
		return True

def is_valid_format(file):
	header_str=open(file, "r", encoding = "utf_16").readline()
	header_str = header_str.rstrip()

	tit_list=["полный путь","папка", "имя файла", "ключевые фразы"]
	titles={i:1000 for i in tit_list}
	count=0
	header_columns = {}
	header_list = header_str.split("\t") 
	header_list = [i.lower() for i in header_list]
	for item in header_list:
		header_columns[item] = count
		count += 1

	for item in tit_list:
		titles[item] = header_columns.get(item, 1000)

	if titles["ключевые фразы"]<1000:
		Str_entry.H_KEY = titles["ключевые фразы"]
	else:
		Str_entry.H_KEY = None

	if (titles["папка"] + titles["имя файла"] < 1000):
		Str_entry.H_PATH = titles["папка"]
		Str_entry.H_NAME = titles["имя файла"]
		Str_entry.H_ABSPATH = None
		return True
	elif (titles["полный путь"] < 1000): 
		Str_entry.H_ABSPATH = titles["полный путь"]
		Str_entry.H_PATH = None
		Str_entry.H_NAME = None
		Str_entry.H_KEY = titles["ключевые фразы"]
		return True
	elif len(header_list)<2 and (os.path.splitdrive(header_list[0])) != "": 
		Str_entry.H_ABSPATH = 0
		Str_entry.H_PATH = None
		Str_entry.H_NAME = None
		return True

	else:
		return False


def reborn_catalog(path):
	errorcode = True
	if os.path.exists(path):	
			errorcode = remove_content_of_catalog(path)
	else:
		os.makedirs(path)
	return errorcode

def remove_content_of_catalog(path):
	errorcode = True
	for root, dirs, files in os.walk(path):
		for d in dirs:
			os.chmod(os.path.join(root, d), 33279)
		for f in files:
			fabs = os.path.join(root, f)
			os.chmod(fabs, 33279)
			try:
				os.remove(fabs)
			except (WindowsError):
				errorcode = False
		if not errorcode:
			break
	if errorcode:
		for entry in os.listdir(path):
			try:
				shutil.rmtree(os.path.join(path, entry))
			except (EnvironmentError, WindowsError):
				errorcode = False
				break
	return errorcode

def close_logs(copylog, errlog):
	copylog.close()
	errlog.close()

def prepare_catalogs():
	prep_err = reborn_catalog(Prefix)
	if not prep_err:
		return prep_err
	prep_err = reborn_catalog(Temp_Catalog)
	return prep_err

def prepare_logs(copylog, errlog):
	Str_entry.COPYLOG = copylog
	Str_entry.ERRORLOG = errlog


def custom_log_name(log, file_name):
	fn = os.path.splitext((os.path.split(file_name)[1]))[0]
	custom_log = log +'_' + fn 
	return custom_log


def init_logs(srez_file, srez_dir, custom_log=False):
	global Prefix
	print("srez_dir: ", srez_dir)
	print("srez_file: ", srez_file)
	Prefix = "\\\\?\\" + srez_dir
	pth = os.path.dirname(srez_file)
	sf = os.path.dirname(srez_file)
	elog = "error"
	clog = "copy"
	if custom_log is True:
		elog = custom_log_name(elog, srez_file)
		clog = custom_log_name(clog, srez_file)
	elog += ".log"
	clog += ".log"
	err_str = os.path.join(pth, elog)
	copy_log_str = os.path.join(pth, clog)
	errlog = open(err_str, "w", encoding = "utf16")
	copylog = open(copy_log_str, "w", encoding = "utf16")
	copylog.write("оригинальный путь\tрезультирующий путь\tотносительный путь\tключевые фразы\n")
	return copylog, errlog

def copy_all_files(arch_str):
	for entry in arch_str:
		entry.copy()
		entry.write_log()


def main_copy(srez_file, srez_dir):
	copylog, errlog = init_logs(srez_file, srez_dir, True)
	prepare_logs(copylog, errlog)
	prep_err = prepare_catalogs()
	if not prep_err:
		print("Файлы не копировались из-за ошибки инициализации каталогов.")
		close_logs(copylog, errlog)
		return None
	print("Рабочие каталоги подготовлены.")

	if not is_utf16_encoding(srez_file):
		print("Файл имеет неверную кодировку (не UTF-16).")
		return None

	if not is_valid_format(srez_file):
		print("Файл имеет неверный формат.")
		return None

	arch_str = init_from_utf16_file_list(srez_file)
	print('Осуществляется копирование файлов...')
	copy_all_files(arch_str)
	close_logs(copylog, errlog)
	return arch_str

if __name__ == "__main__":
	if len(sys.argv) < 3:
		print("Отсутствуют необходимые аргументы.")
		sys.exit(1)		

	cur_date = time.time()
	str_time = time.strftime("%Y.%m.%d_%H.%M.%S", time.localtime(cur_date))
	log_filename = f"archisrez_{str_time}.log"

	logging.basicConfig(level = logging.DEBUG, filename = log_filename, filemode ="w",
		 format = "%(asctime)s  %(module)s %(funcName)s : %(message)s")


	arch = main_copy(sys.argv[1], sys.argv[2])
	if arch is None:
		print("Файлы не копировались из-за ошибки.")
		input("Press Enter")
		sys.exit(1)
	success_lines = error_lines = processed_lines = 0
	for i in arch:
		if i.copied:
			success_lines += 1
		else:
			error_lines += 1
		processed_lines +=1 
	del arch
	print("Всего обработано %d файлов." %  processed_lines)
	print("Успешно скопировано: %d" %  success_lines)
	print("Ошибок копирования: %d" %  error_lines)
	
