from arc import get_unicode_encoding

from tkinter import *
from tkinter.filedialog import askopenfilename, askdirectory
from arc import LOGGER

import os
import os.path
import sys
from pathlib import Path
cw = os.getcwd()
sys.path.append(os.path.join(cw, "z"))

from arc import agregator
from arc import report
from arc import srez
from arc import gui
from arc import __version__


class Aggregator():
	def __init__(self, app):
		self.app = app
		self.gu = gui.Aggr_Gui(self.app)
		#привязка функций к виджетам: для кнопки; для строки ввода; для кнопки исполнения
		self.gu.bind_functions(self.button_dir, self.entry_dir, self.agregate_files)

	def entry_dir(self, event):
		self.inspect_dir()
		
	def button_dir(self):
		self.get_dirname_from_button()
		self.inspect_dir()

	def get_dirname_from_button(self):
		self.gu.ebun.set_var(os.path.normpath(askdirectory()))

	def inspect_dir(self):	
		""" 
		Проверяет выбранный каталог на наличие файлов, которые булут объединяться в один.
		Делается это до запуска объединения. В смотрит заголовки файлов, опрелеляет, подойдут они или нет 
		"""
		self.app.output_directory = self.gu.ebun.get_var()
		self.wof = agregator.ArchReportFiles(os.path.normpath(self.gu.ebun.get_var()))
		if len(self.wof.archivar_files) > 0:
			self.display_working_files() #показывает список файлов, которые будут объединяться в один
			self.gu.unlock_exec_button() #разблокирует кнопку запуска объединения
		else:
			self.app.display("Каталог не содержит нужных файлов.")
			self.gu.lock_exec_button()

	def display_working_files(self):
		string = "Список файлов:\n"
		for entry in self.wof.archivar_files:
			string += "   " + os.path.basename(entry.path) + "\n"
		self.app.display(string)

	def agregate_files(self, event = None):	
		"""
		Запускает объединение файлов. Запускает метод Work_Files.execute по уже 
		сформированному списку файлов и выводит результаты на экран
		"""			
		arc_out_list = self.wof.execute()
		self.app.display("Создан файл %s." % arc_out_list)
		self.app.interf_srez.gu.gui_file.set_var(arc_out_list)# и передает имя суммарного файла в секцию для копирования
		self.app.interf_srez.arch_list = arc_out_list
	


class Srez():
	def __init__(self, app):
		self.app = app
		self.gu = gui.Srez_Gui(self.app )
		self.gu.bind_functions(self.open_file_list, self.open_srez_dir, self.copy_files)


	def open_file_list(self):
		self.gu.gui_file.set_var(os.path.normpath(askopenfilename()))
		self.arch_list = self.gu.gui_file.get_var()

	def open_srez_dir(self):
		self.gu.gui_dir.set_var(os.path.normpath(askdirectory()))

	def copy_files(self, event=None):

		self.app.logger.debug("File copying Started")
		self.app.display("Подготовка каталогов для копирования...", star=False)
		copylog, errlog = srez.init_logs(self.gu.gui_file.get_var(), self.gu.gui_dir.get_var())
		srez.prepare_logs(copylog, errlog)
		prep_err = srez.prepare_catalogs()
		if not prep_err:
			self.app.display("Файлы не копировались из-за ошибки инициализации каталогов.")
			srez.close_logs(copylog, errlog)
			# не просто ретурн возвращать, а код ошибки
			# а ошибку в дисплее выводить отдельно
			return

		self.app.display("Подготовлены.")
		# определяем кодировку файла среза
		srez_file_encoding = get_unicode_encoding(self.gu.gui_file.get_var())
		if srez_file_encoding is None:
			self.app.display("Файл имеет неверную кодировку (не Юникод).")
			# не просто ретурн возвращать, а код ошибки
			# а ошибку в дисплее выводить отдельно
			return
		# определяем, что файл среза имеет верный формат
		if not srez.is_valid_format(self.gu.gui_file.get_var(), srez_file_encoding):
			self.app.display("Файл имеет неверный формат.")
			return
		# создаем список объектов (файлов) для копирования
		arch = srez.init_from_utf16_file_list(self.gu.gui_file.get_var(), srez_file_encoding)
		self.app.display("Копирование файлов...", star=False)

		entry_count = 0
		all_lines = len(arch)
		self.prog_bar = gui.SrezProgBar(all_lines)
		for entry in arch:
			entry_count+=1
			entry.copy()
			self.prog_bar.show_progress(entry_count)
			entry.write_log()
		self.prog_bar.destroy()

		srez.close_logs(copylog, errlog)

		success_lines = error_lines = processed_lines = 0
		for i in arch:
			if i.copied:
				success_lines += 1
			else:
				error_lines += 1
			processed_lines +=1 
		del arch
		self.display_copying_result(processed_lines, success_lines, error_lines)

	def display_copying_result(self, processed_lines, success_lines, error_lines):
		s = "Обработано файлов: %d.\nУдачно скопировано: %d.\nОшибок копирования: %d.\n" \
		% (processed_lines, success_lines, error_lines)
		self.app.display(s)
		cl = os.path.abspath(srez.Str_entry.COPYLOG.__getattribute__("name"))
		el = os.path.abspath(srez.Str_entry.ERRORLOG.__getattribute__("name"))
		self.app.display("Журнал скопиорванных файлов: " + cl, star = False)
		self.app.display("Журнал ошибок: " + el)
		# self.mother.f_rp.copylog = cl
		# self.mother.f_rp.otchet = self.gu.gui_dir.get_var()
		# self.mother.f_rp.gui_dir.show_text(self.mother.f_rp.otchet)
		# self.mother.f_rp.gui_file.show_text(self.mother.f_rp.copylog)
		self.app.interf_report.gu.gui_file.set_var(cl)
		self.app.interf_report.gu.gui_dir.set_var(self.gu.gui_dir.get_var())
	

class Report():
	def __init__(self, app):
		self.app = app
		self.gu = gui.Report_Gui(self.app)
		self.gu.bind_functions2(file_button = self.get_copylog_from_button, 
			dir_button = self.get_srez_dir_from_button, 
			file_entry = self.get_copylog_from_entry,
			exec_button =  self.make_otchet)		
		self.otchet = None

	def get_copylog_from_button(self):
		self.gu.gui_file.set_var(os.path.normpath(askopenfilename()))
		self.open_copylog()

	def get_copylog_from_entry(self, event = None):
		self.open_copylog()

	def get_srez_dir_from_button(self):
		self.gu.gui_dir.set_var(os.path.normpath(askdirectory()))
		
	def open_copylog(self):
		'''
		получает файл copy.log по кнопке, получает из него папку для создания отчета 
		по умолчанию (заполняет второе поле). В случае проблем выдает сообщение об ошибке.
		'''
		copy_log = self.gu.gui_file.get_var()
		if self.check_copylog(copy_log):
			otchet_dir = self.get_srez_dir_from_copylog(copy_log)
			self.gu.gui_dir.set_var(otchet_dir)
			self.app.display("Файл для создания отчета о скопированных файлах выбран.")
		else:
			self.app.display("Неверный формат файла.")


	def check_copylog(self, copy_log):
		'''
		в случае канонической формы файла copy.log возвращает истину, иначе - ложь
		'''
		canon = "оригинальный путь	результирующий путь	относительный путь	ключевые фразы"
		f = open(copy_log, "r", encoding="utf16")
		try:	
			header = f.readline()
		except UnicodeError:
			f.close()
			return False
		string = f.readline()
		f.close()
		if header.rstrip() == canon:
			return True
		else:
			return False
			
	def get_srez_dir_from_copylog(self, copy_log):
		'''
		получает из copy.log папку, куда осуществлялось копирование файла
		для того, чтобы подставить ее в качестве папки по умолчанию, куда будут 
		копироваться файлы отчета 
		'''
		f = open(copy_log, "r", encoding="utf16")
		string = f.readline()#читаем вторую строку
		f.close()
		paths = string.split("\t")
		dest = paths[1]
		relative = paths[2]
		otchet_path = dest[:dest.index(relative)]
		return os.path.normpath(otchet_path)

	def make_otchet(self, event = None):
		report.create_all(self.gu.gui_file.get_var(), self.gu.gui_dir.get_var())
		self.app.display("Создан отчет по скопированным файлам.")


class Application(Tk):
	def __init__(self):
		super().__init__()
		self.title(f"Архисрез {__version__}")
		self.minsize(580, 720)
		self.maxsize(600, 770)
		self.logger = LOGGER
		self.logger.debug("=" * 60)
		self.logger.debug("Program Started")


		self.interf_help = gui.HelpButton(self)
		self.interf_aggregator = Aggregator(self)
		self.interf_srez = Srez(self)
		self.interf_report = Report(self)
		self.interf_display = gui.Display_Gui(self)
		self.output_directory = os.getcwd


	def display(self, string, star=True):
		self.interf_display.add_info(string)
		if star:
			self.interf_display.add_info("-" * 50)


app = Application()
app.mainloop()
