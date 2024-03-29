﻿from arc import get_unicode_encoding

import os
import sys
import shutil
import subprocess
import time
import re
import binascii
from typing import Dict, Optional, TextIO
from pathlib import Path

Global_cur_time = time.time()
Temp_Catalog = os.environ['TEMP'] + '\\archisrez'
if __name__ == '__main__':
	zip_path = '../z/'
	from . import LOGGER
else: 
	zip_path = './z/'
	from arc import LOGGER

Prefix = str() # зачем она так объявлена, зачем она вообще на глобальном уровне существует?

class Str_entry():
	COPYLOG = None
	ERRORLOG = None
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
			self.filename = os.path.basename(a[Str_entry.H_ABSPATH])
			self.abspath = a[Str_entry.H_ABSPATH].strip()
		if Str_entry.H_KEY is not None:
			self.keystring = a[Str_entry.H_KEY].strip()
		else:
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
		LOGGER.debug(source_path)
		# Удолит эту отладочную информацию
		if not os.path.exists(source_path):
			LOGGER.debug("file not found")
		#-------------------------------------------
		if os.path.exists(source_path):
			LOGGER.debug("path exists")
			self.dest_path, self.relative_path = self.get_dest_dir(dest)
			self.make_dest_dir()
			if self.copy_file(source_path, self.dest_path):
				self.set_copied()

	def remove_disk_letter_from_path(self, dest_path):
		common_path_template = r"(?P<diskletter>^(?P<letter>\w):)(?P<tail>\\.*)"
		server_path_template = r"(?P<full>^\\\\(?P<short>\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}))(?P<tail>\\.+)"
		if re.findall(common_path_template, dest_path):
			dest_srez = re.sub(common_path_template, r"\g<letter>\g<tail>", dest_path)
		elif re.findall(server_path_template, dest_path):
			dest_srez = re.sub(server_path_template, r"\g<short>\g<tail>", dest_path)
		else:
			dest_srez = dest_path
		return dest_srez

	def get_dest_dir(self, string):
		'''
		Создает путь, куда будет копироваться файл. Берет изначальный путь, убирает от буквы 
		диска двоеточие и пристегивает получившуюся строку к префиксу, то есть пути, куда 
		будут скопированы все файлы.
		'''
		dest_path = os.path.dirname(string)
		relative_path = self.remove_disk_letter_from_path(dest_path)
		dest_path = Path(Prefix, relative_path)
		return dest_path, relative_path
	
	def make_dest_dir(self):
		if not os.path.exists(self.dest_path):
			LOGGER.debug(self.dest_path)
			try:
				os.makedirs(self.dest_path)
			except Exception as erka:
				print("Ошибка создания каталога %" % self.dest_path)
				LOGGER.debug("ERROR CREATED DEST PATH" + str(erka))
			else:
				LOGGER.debug("dest_path created")

	def is_archived(self):
		#print("proc is_archived")
		archived = "|"  in self.abspath
		archived2 = "/" in self.abspath
		archived = archived or archived2
		LOGGER.debug(self.abspath)
		if archived:
			LOGGER.debug("file is archived")
		return archived

	def extract_one_string(self):
		'''
		Осуществляет разархивирование файла, обрабатывая один или больше вложенных архивов
		Возвращает путь к разархивированному файлу
		'''
		"""
		Учитывая, что зачастую приходится копировать файлы из списка абсолютных путей ,который был создан в ТОТАЛЕ,
		возникает проблема с архивами. Архив там обозначается не пайпом, а обратным слешем. Поэтому в качестве 
		костыльного решения попробую пока переделать все бэкслеши в пайпы. Вдруг будет нормально работать
		"""
		self.abspath = self.abspath.replace("/","|")
		archive_parts =self.abspath.split("|")# вначале представляет собой раздробленную по пайпам стрку,
		#в конце процедуры представляет набор ссылок на архивы по ходу вложенности
		cur_path=archive_parts[0]
		# от предыдущих разархивирований может остаться распакованный файл
		# тут словарь нужен для вложенных архивов. Если часть пути до второго или третьего по вложенности архива есть,
		# она достается из словаря
		dict_flag = True
		for i in range(1, len(archive_parts)):
			# по сути в cur_path формируется ключ для словаря по которому можно будет достать распакованный файл
			cur_path ="|".join([cur_path,  archive_parts[i]])
			if dict_flag:
				# ключ: часть оригинального пути ло следующего архива
				# значение: путь к распакованному архиву
				# в начале поиска по архивам всегда проверяется, есть ли путь к разархивированному архиву в словре
				# если на первом уровне вложенности нет разархивированного архиива, то искать уже нет смысла
				# поэтому ставим переменную dict_flag в False
				if Str_entry.ARC_DICT.get(cur_path):
					archive_parts[i] = Str_entry.ARC_DICT[cur_path]
				else:
					dict_flag = False
			# если переменная dict_flag ==False, распаковаываем следующий файл, находящийся в архиве
			# и возвращаем путь к нему. При распаковке берутся две части archive_parts[i-1] -путь к распакованному архиву
			# и archive_parts[i] путь к файлу внутри архива, который еще нужно распаковать.
			# Почему используется archive_parts[i-1]? Потому что оо модифицируется при успешно разхивировании следующего вложенного архива

			if not dict_flag:	                                    # путь к архиву        путь к файлу в архиве
				unpacked_arcive_path, path_in_archive = self.new_path(archive_parts[i-1],       archive_parts[i])
				if unpacked_arcive_path  is None:
					print("Ошибка распаковки")
					return None
				else:
					archive_parts[i] = os.path.join(unpacked_arcive_path, path_in_archive)
					#archive_parts[i]=os.path.join(unpacked_arcive_path, archive_parts[i])
					if not archive_parts[i] is archive_parts[-1]:
						#кроме последней сторки, так как там лежит не архив, а
						#распакованный файл и записвывть его в список архивов бессмысленно
						Str_entry.ARC_DICT[cur_path]=archive_parts[i]
			#print("AP\n",  archive_parts)
		LOGGER.debug("UNZIPPED PATH: %s" % archive_parts[-1])
		return archive_parts[-1]  # разархивированный конечный файл, кот. надо скопировать

	def new_path(self, arch, fil):
		'''
		распаковывает архив в новую папку и возвращает местоположение распакованного файла.
		arch - путь к архиву, из которого нужно распаковывать содержимое.
		fil - файл со всеми каталогами внутри архива, из котрого нужно распаковать сам архив не указывается
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

		inner_crc = get_hash_of_file_in_archive(arch, fil)
		print('ОШИБКА ФАЙЛА')
		if inner_crc is None:
			try:
				fil = (fil.encode('cp1251')).decode('cp866')
			except:
				try:
					fil = (fil.encode('cp1251')).decode('cp866')
				except:
					pass
			inner_crc = get_hash_of_file_in_archive(arch, fil)
		print('ОШИБКА ФАЙЛА В АРХИВЕ - НЕИЗВЕСТНАЯ КОНТРОЛЬНАЯ СУММА (КОДИРОВКА)')
		Str_entry.GLOBAL_COUNTER += 1
		# промежутчный каталог куда разархивируется файл
		transit_path = os.path.join(Temp_Catalog,  str(Str_entry.GLOBAL_COUNTER))
		os.mkdir(transit_path)
		# строка, чтобы  распаковывать файл из архива в temp
		command = f'{zip_path}7z.exe x "{arch}" -y -o"{transit_path}" "{fil}"'
		#LOGGER.debug(command)
		# запускаем команду на распаковку файла из архива
		po = subprocess.Popen(command,  stdout = subprocess.PIPE, stdin = subprocess.PIPE)
		# этот энтер нужен на случай если архив запросит пароль. Если его не ставить, выполнение 7z не завершится,
		# он так и будет ожидать ввода пароля. Костыльный шаг, но довольно простой.
		po.stdin.write(b'\n')
		# смотрим, что выводит архиватор в процессе работы
		listing = po.communicate()[0]
		z7out=listing.decode("cp866")
		Str_entry.UNZIP_OUTPUT.write(z7out + '\n=====================================cheked\n')

		LOGGER.debug(z7out)
		# должна выводить, если скопировалась корректно
		if "Everything is Ok" in z7out:
			return transit_path, fil
		else:

			pathn = os.path.join(transit_path, fil)
			
			if not os.path.exists(pathn):
				return None, None
			else:
				file_crc = check_file_crc(pathn)
				if	inner_crc == file_crc:
					return transit_path, fil
				else:
					return None, None
						
		
		
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
		dest_path = str(self.dest_path).replace("\\\\?\\", "")
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


def init_from_utf16_file_list(path: str, utf_encoding: str) -> list[Str_entry]:
	file_records=[]
	for file in open(path, "r", encoding = utf_encoding).readlines():
		file_records.append(Str_entry(file.rstrip()))
	return file_records


# def get_unicode_encoding(file: str) -> Optional[str]:
# 	e = None
# 	for enc in ['utf-8-sig', 'utf-16']:
# 		t = open(file, 'r', encoding=enc)
# 		try:
# 			t.readline()
# 		except UnicodeDecodeError:
# 			pass
# 		else:
# 			e = enc
# 			break
# 		finally:
# 			t.close()
# 	return e

def is_valid_format(file: str, encoding: str):
	header_str=open(file, "r", encoding = encoding).readline()
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

	encoding = get_unicode_encoding(srez_file)
	if encoding is None:
		print("Файл имеет неверную кодировку (не Юникод).")
		return None

	if not is_valid_format(srez_file, encoding):
		print("Файл имеет неверный формат.")
		return None

	arch_str = init_from_utf16_file_list(srez_file, encoding)
	print('Осуществляется копирование файлов...')
	copy_all_files(arch_str)
	close_logs(copylog, errlog)
	return arch_str




if __name__ == "__main__":
	if len(sys.argv) < 3:
		print("Отсутствуют необходимые аргументы.")
		sys.exit(1)		

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
	
