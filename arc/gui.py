import os
from tkinter import *
from tkinter.filedialog import askopenfilename, askopenfilenames, askdirectory
from arc import help

class HelpButton():
	def __init__(self, app):
		self.help_but = Button(app, text = "О программе", 
			command = self.call_help_window)
		self.help_but.pack(side = TOP)

	def call_help_window(self):
		help_win = Toplevel()
		help_win.title("О программе")
		he = Text(help_win, width = 80, height = 24, background = "white", 
			relief = SUNKEN, bd = 3, 
			font = "Arial 9",
			wrap = WORD)
		scroller = Scrollbar(help_win, orient = VERTICAL, 
			command = he.yview)
		he.config(yscrollcommand = scroller.set)
		he.pack(side = LEFT, expand = YES, fill = BOTH)
		scroller.pack(side = RIGHT, expand = YES, fill = Y)
		he.insert("1.0", help.help_text)
		he.config(state = DISABLED)		
		help_win.focus_set()
		he.focus()

# сборка: строка ввода с кнопкой
class EnButt():
	def __init__(self, parent = None, string = "", proc = None):
		self.entry = Entry(parent)
		self.entry_var = StringVar()
		self.entry.config(textvariable = self.entry_var)
		self.entry_never_enter = True

		self.button = Button(parent, text = "Выбрать", command = proc)
		self.entry_var.set(string)
		self.entry.pack(side = LEFT, expand = YES, fill = X)
		self.button.pack(side = RIGHT)
		self.entry.bind("<Button-1>", self.remove_default_text_from_entry)

		
	def set_function(self, function, ent_bind):
		self.button.config(command = function)
		self.entry.bind('<Return>', ent_bind)
		self.entry.bind('<FocusIn>', self.remove_default_text_from_entry)

	def remove_default_text_from_entry(self, event = None):
		if self.entry_never_enter:
			self.set_var("")
	
	def set_var(self, string):
		self.entry_var.set(string)
		self.entry_never_enter = False

	def get_var(self):
		return self.entry_var.get()
		

class Aggr_Gui():# панелька, ответственная за объединение срезов
	def __init__(self, app):
		self.app = app
		self.agrfame = Frame(self.app, relief=GROOVE,
							 borderwidth = 4, width = 800, padx = 10, pady = 10, height = 400) # область интерфейса агрегатора
		self.agrfame.pack(side = TOP)
		label_text = "1. Слияние списков Архивариус 3000."
		Label(self.agrfame, width=80, height = 2, text =label_text, anchor = NW).pack()
		self.fr = Frame(self.agrfame, padx = 5, pady = 5) # область для помещения текстового поля с кнопкой
		self.fr.pack(side = TOP, expand = YES, fill = X)	
		
		self.ebun = EnButt(self.fr, "Каталог со списками архивариуса.", None) # комбо: текстовое поле с кнопкой
		self.exec_but = Button(self.agrfame, text ="Выполнить", state = DISABLED) # кнопка запуска
		self.exec_but.pack()

	# привязка функций к виджетам
	# butt_func - функция кнопки выбора папки
	# butt_func - 
	def bind_functions(self, butt_func, ent_func, exec_butt_func):
		def exec_func_mod(event = None):
			exec_butt_func()
			self.app.interf_srez.gu.gui_dir.entry.focus()

		self.ebun.set_function(butt_func, ent_func)
		self.exec_but.config(command = exec_func_mod)
		self.exec_but.bind('<Return>', exec_func_mod)

	def unlock_exec_button(self):
		self.exec_but.config(state = NORMAL)
		self.exec_but.focus()

	def lock_exec_button(self):
		self.exec_but.config(state = DISABLED)



class Srez_Gui():
	def __init__(self, app):
		self.app = app
		self.srezframe = Frame(self.app, relief=GROOVE,
							   borderwidth = 4, width = 700, padx = 10, pady = 10,
							   height = 400)
		self.srezframe.pack(side = TOP)
		lt =  "2. Копирование файлов."
		Label(self.srezframe, width=80, height = 2, text = lt, anchor = NW).pack(side = TOP, expand = YES, fill = X)

		self.fr1 = Frame(self.srezframe, padx = 5, pady = 5)
		self.fr1.pack(side = TOP, expand = YES, fill = X)
		self.fr2 = Frame(self.srezframe, padx = 5, pady = 5)
		self.fr2.pack(side = TOP, expand = YES, fill = X)
		self.gui_file = EnButt(self.fr1, "Список файлов для копирования.", None)
		self.gui_dir = EnButt(self.fr2, "Каталог для копирования.", None)
		self.srez_exec = Button(self.srezframe, text ="Выполнить", state = DISABLED)
		self.srez_exec.pack(side = TOP)
		self.ready_to_execute()

	def bind_functions(self, file_butt_func,  dir_butt_func, exec_butt_func):
		
		def ent_func_file(event):
			if self.ready_to_srez():
				self.srez_exec.focus()
			else:
				self.gui_dir.entry.focus()

		def ent_func_dir(event):
			if self.ready_to_srez():
				self.srez_exec.focus()
			else:
				self.gui_file.entry.focus()
		def exec_func_mod(event = None):
			exec_butt_func()
			self.app.interf_report.gu.otchet_go.focus()

		self.gui_file.set_function(file_butt_func, ent_func_file)
		self.gui_dir.set_function(dir_butt_func, ent_func_dir)

		self.srez_exec.config(command = exec_func_mod)
		self.srez_exec.bind('<Return>', exec_func_mod)

	def unlock_exec_button(self):
		self.srez_exec.config(state = NORMAL)

	def lock_exec_button(self):
		self.srez_exec.config(state = DISABLED)
		#self.gui_file.show_text("Список файлов для копирования.")

	def ready_to_srez(self):
		filee = self.gui_file.get_var()
		dirr = self.gui_dir.get_var()
		return os.path.exists(filee) and os.path.exists(dirr)

	def ready_to_execute(self):
		if self.ready_to_srez():
			self.unlock_exec_button()
		else:
			self.lock_exec_button()
		self.srezframe.after(200, self.ready_to_execute)


class Report_Gui():
	def __init__(self, app): #parent - Tk();  root - Raport()
		self.app = app
		self.repframe = Frame(self.app, relief=GROOVE,
							  borderwidth = 4, width = 700, padx = 10, pady = 10,
							  height = 400)
		self.repframe.pack(side = TOP)

		self.lb = Label(self.repframe, width=80, height = 2, text ="3. Формирование HTML-отчета о копировании.", anchor = NW)
		self.lb.pack(side = TOP, expand = YES, fill = X)
		self.fr1 = Frame(self.repframe, padx = 5, pady = 5)
		self.fr1.pack(side = TOP, expand = YES, fill = X)
		self.fr2 = Frame(self.repframe, padx = 5, pady = 5)
		self.fr2.pack(side = TOP, expand = YES, fill = X)
		self.gui_file = EnButt(self.fr1, "Файл с отчетом о копировании файлов.")
		self.gui_dir = EnButt(self.fr2, "Каталог со скопированными файлами.")
		
		self.otchet_go = Button(self.repframe, text ="Выполнить", state = DISABLED,
								command = None)
		self.otchet_go.pack(side = TOP)
		self.ready_to_execute()

	def bind_functions2(self, file_button = None, dir_button = None, 
		file_entry = None, dir_entry = None, exec_button = None):
		
		def file_entry_mod(event):
			if self.ready_to_otchet():
				self.otchet_go.focus()
			else:
				file_entry()
				if self.ready_to_otchet():
					self.otchet_go.focus()
				else:
					self.gui_dir.entry.focus()

		def ent_func_dir(event):
			if self.ready_to_otchet():
				self.otchet_go.focus()
			else:
				self.gui_file.entry.focus()

		self.gui_file.set_function(file_button, file_entry_mod)
		self.gui_dir.set_function(dir_button, ent_func_dir)

		self.otchet_go.config(command = exec_button)
		self.otchet_go.bind('<Return>', exec_button)

	def unlock_exec_button(self):
		self.otchet_go.config(state = NORMAL)
		#self.otchet_go.focus()

	def lock_exec_button(self):
		self.otchet_go.config(state = DISABLED)
		#self.gui_file.show_text("Список файлов для копирования.")

	def ready_to_otchet(self):
		filee = self.gui_file.get_var()
		dirr = self.gui_dir.get_var()
		return os.path.exists(filee) and os.path.exists(dirr)

	def ready_to_execute(self):
		if self.ready_to_otchet():
			self.unlock_exec_button()
		else:
			self.lock_exec_button()
		self.repframe.after(200, self.ready_to_execute)

class Display_Gui():
	def __init__(self, parent): #parent - Tk(); 
		self.dispgui = Frame(parent, relief=GROOVE, 
				borderwidth = 4, width = 700, padx = 10, pady = 10, 
				height = 500)
		self.dispgui.pack(side = TOP)
		self.lb = Label(self.dispgui, width=80,  text = "Информация")
		self.lb.pack(side = TOP)
		self.tex = Text(self.dispgui, width = 75, height = 14, background = "white", 
			relief = SUNKEN, bd = 3, 
			font = "Arial 9",
			state = DISABLED, 
			wrap = WORD)
		self.scroller = Scrollbar(self.dispgui, orient = VERTICAL, command = self.tex.yview)
		self.tex.config(yscrollcommand = self.scroller.set)
		self.tex.pack(side = LEFT, expand = YES, fill = BOTH)
		self.scroller.pack(side = RIGHT, expand = YES, fill = Y)

	def add_info(self, strings):
		self.tex.config(state = NORMAL)
		self.tex.insert(END, strings)
		self.tex.insert(END, "\n")
		self.tex.see(END)
		self.tex.config(state = DISABLED)
		self.tex.update()
