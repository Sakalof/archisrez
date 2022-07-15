from tkinter import *
from tkinter.ttk import Progressbar
from tkinter.filedialog import askopenfilename, askdirectory
import logging
import os
import os.path
import sys
import time
cw = os.getcwd()
sys.path.append(cw + "\\z")

from arc import agregator
from arc import report
from arc import srez
from arc import gui


class Argegat():
	def __init__(self, parent = None, app = None): #parent высший уровень, app - управляющий класс без графики
		self.mother = app
		self.gu = gui.Agr_Gui(parent, self)
		#привязка функций к виджетам: для кнопки; для строки ввода; для кнопки исполнения
		self.gu.bind_functions(self.button_dir, self.entry_dir, self.agregate_files)
		# при выборе пути происходит проверка файлов в директории: те,
		# с которых читать данные. Это делает inspect_dir
		#print("agregat_parent", self.mother)
		#print("top level", parent)

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
		self.mother.output_directory = self.gu.ebun.get_var()
		self.wof = agregator.Work_Files(os.path.normpath(self.gu.ebun.get_var()))
		if len(self.wof.workfiles) > 0:
			self.display_working_files() #показывает список файлов, которые будут объединяться в один
			self.gu.unlock_exec_button() #разблокирует кнопку запуска объединения
		else:
			self.mother.display("Каталог не содержит нужных файлов.")
			self.gu.lock_exec_button()

	def display_working_files(self):
		string = "Список файлов:\n"
		for entry in self.wof.workfiles:
			string += "   " + os.path.basename(entry.path) + "\n"
		self.mother.display(string)

	def agregate_files(self, event = None):	
		"""
		Запускает объединение файлов. Запускает метод Work_Files.execute по уже 
		сформированному списку файлов и выводит результаты на экран
		"""			
		arc_out_list = self.wof.execute()
		self.mother.display("Создан файл %s." % arc_out_list)
		self.mother.f_sr.gu.gui_file.set_var(arc_out_list)# и передает имя суммарного файла в секцию для копирования
		self.mother.f_sr.arch_list = arc_out_list
	


class Srez():
	def __init__(self, parent = None, app = None):
		self.mother = app
		self.gu = gui.Srez_Gui(parent, self)
		self.gu.bind_functions(self.open_file_list, self.open_srez_dir, self.copy_files)


	def open_file_list(self):
		self.gu.gui_file.set_var(os.path.normpath(askopenfilename()))
		self.arch_list = self.gu.gui_file.get_var()

	def open_srez_dir(self):
		self.gu.gui_dir.set_var(os.path.normpath(askdirectory()))

	def copy_files(self, event=None):

		prog_bar_window = Toplevel() # создание прогресс бара
		prog_bar_window.overrideredirect(True) # убирание у прогресс бара возможности закрыться (крестик убираем)
		#prog_bar_window.wm_attributes('-fullscreen', 'true')
		prog_bar_window.geometry("410x100")
		pbl = Label(prog_bar_window, text = 'Прогресс копирования файлов.')
		pbl.pack(side = TOP)
		pb = Progressbar(prog_bar_window , orient=HORIZONTAL, length=300, mode='determinate')
		pb.pack(side = TOP, expand = YES, fill = BOTH)

		logging.debug("File copying Started")
		self.mother.display("Подготовка каталогов для копирования...", star=False)
		copylog, errlog = srez.init_logs(self.gu.gui_file.get_var(), self.gu.gui_dir.get_var())
		srez.prepare_logs(copylog, errlog)
		prep_err = srez.prepare_catalogs()
		if not prep_err:
			self.mother.display("Файлы не копировались из-за ошибки инициализации каталогов.")
			srez.close_logs(copylog, errlog)
			# не просто ретурн возвращать, а код ошибки
			# а ошибку в дисплее выводить отдельно
			return

		self.mother.display("Подготовлены.")
		# определяем кодировку файла среза
		srez_file_encoding = srez.get_unicode_encoding(self.gu.gui_file.get_var())
		if srez_file_encoding is None:
			self.mother.display("Файл имеет неверную кодировку (не Юникод).")
			# не просто ретурн возвращать, а код ошибки
			# а ошибку в дисплее выводить отдельно
			return
		# определяем, что файл среза имеет верный формат
		if not srez.is_valid_format(self.gu.gui_file.get_var(), srez_file_encoding):
			self.mother.display("Файл имеет неверный формат.")
			return
		# создаем список объектов (файлов) для копирования
		arch = srez.init_from_utf16_file_list(self.gu.gui_file.get_var(), srez_file_encoding)
		self.mother.display("Копирование файлов...", star=False)
		all_lines = len(arch)
		entry_count = 0
		pb['value'] = 0
		prog_bar_window.update()
		for entry in arch:
			entry_count+=1
			entry.copy()
			prog_float = int(entry_count/all_lines*100)
			pb['value'] = prog_float
			pbl.config(text=f'{entry_count}/{all_lines}')
			prog_bar_window.update()
			entry.write_log()
		prog_bar_window.destroy()


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
		self.mother.display(s)
		cl = os.path.abspath(srez.Str_entry.COPYLOG.__getattribute__("name"))
		el = os.path.abspath(srez.Str_entry.ERRORLOG.__getattribute__("name"))
		self.mother.display("Журнал скопиорванных файлов: " + cl, star = False)
		self.mother.display("Журнал ошибок: " + el)
		# self.mother.f_rp.copylog = cl
		# self.mother.f_rp.otchet = self.gu.gui_dir.get_var()
		# self.mother.f_rp.gui_dir.show_text(self.mother.f_rp.otchet)
		# self.mother.f_rp.gui_file.show_text(self.mother.f_rp.copylog)
		self.mother.f_rp.gu.gui_file.set_var(cl)
		self.mother.f_rp.gu.gui_dir.set_var(self.gu.gui_dir.get_var())
	

class Report():
	def __init__(self, parent = None, app = None):
		self.mother = app
		self.gu = gui.Report_Gui(parent, self)
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
			self.mother.display("Файл для создания отчета о скопированных файлах выбран.")
		else:
			self.mother.display("Неверный формат файла.")


	def check_copylog(self, copy_log):
		'''
		в случае канонической формы файла copy.log возвращает истину, иначе - ложь
		'''
		canon= "оригинальный путь	результирующий путь	относительный путь	ключевые фразы"
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
		string = f.readline()
		string = f.readline()#читаем вторую строку
		f.close()
		paths = string.split("\t")
		dest = paths[1]
		relative = paths[2]
		otchet_path = dest[:dest.index(relative)]
		return os.path.normpath(otchet_path)


	def make_otchet(self, event = None):
		report.create_all(self.gu.gui_file.get_var(), self.gu.gui_dir.get_var())
		self.mother.display("Создан отчет по скопированным файлам.")

class Application():
	def __init__(self, parent):
		#print("application toplevel", parent)
		
		self.f_help = gui.HelpButton(parent)
		self.f_ag = Argegat(parent, self)
		self.f_sr = Srez(parent, self)	
		self.f_rp = Report(parent, self)
		self.f_di = gui.Display_Gui(parent)
		self.output_directory = os.getcwd

	def display(self, string, star=True):
		self.f_di.add_info(string)
		if star:
			self.f_di.add_info("-"*50)


root = Tk()
cur_date = time.time()
str_time = time.strftime("%Y.%m.%d_%H.%M.%S", time.localtime(cur_date))
log_filename = f"archisrez_{str_time}.log"

logging.basicConfig(level = logging.DEBUG, filename = log_filename, filemode ="w",
	 format = "%(asctime)s  %(module)s %(funcName)s : %(message)s")
cur_date = time.time()
logging.debug("="*60)
#logging.debug(time.strftime("%d.%m.%Y %H:%M:%S", time.localtime(cur_date)))
logging.debug("Program Started")
#print("Самый верх: ", root)
root.title("Архисрез 0.55")
root.minsize(580, 720)
root.maxsize(600, 770)
app = Application(root)
root.mainloop()
