
import os.path

main_htm='''
<HTML>                  
<HEAD>
<meta http-equiv="Content-type" content="text/html;charset=utf-8"/>
<TITLE>Список файлов.</TITLE>
<style>
.file
{
	padding: 2px;
	font: 13px Verdana;
}

.file a
{
	color: #444444;
}

.file a:hover
{
	color: red;
	text-decoration: none;
}
</style>
</HEAD>

<frameset BORDER=2 cols="16%, *">
	<frame src="index\\left.htm" name="keyword">
	<frame  src="index\\Все ключевые фразы.htm" name="files">
</frameset>
</HTML>
'''

left_head="""<HTML>                  
<HEAD>
<meta http-equiv="Content-type" content="text/html;charset=utf-8"/>
<style>
body {	font-family: Verdana;
	font-size: 13px ;
	color: black ;
	background: #D3D3F5 ;
}
a { color: black ;}
a:hover {color: red; text-decoration: none;}
h2 {font-size: 16px; font-weight: bold ;}

</style>
</HEAD>
<BODY >
<b><h2>Ключевые фразы</h2></b><BR>
"""

right_main="""
<HTML>                  
<HEAD>
<meta http-equiv="Content-type" content="text/html;charset=utf-8"/>
<style>
.file
{
	padding: 2px;
	font: 13px Verdana;
}

.file a
{
	color: #444444;
}

.file a:hover
{
	color: red;
	text-decoration: none;
}
</style>
</HEAD>

<frameset BORDER=2 rows="35, *">
"""

right_head="""<HTML>                  
<HEAD>
<meta http-equiv="Content-type" content="text/html;charset=utf-8"/>
<style>
h2 {font-family: Verdana;
	font-size: 16px ;
	font-weight: bold ;}
.file
{
	padding: 2px;
	font: 13px Verdana;
}

.file a
{
	color: #444444;
}

.file a:hover
{
	color: red;
	text-decoration: none;
}
.file a:visited {color: #aa00aa;	}
	
</style>
</HEAD>
<BODY>
"""

right_tail="""</BODY>
</HTML>"""

s_pre="<div><A href='"
s_suf="' target ='files'>"
s_post='</div><BR>'


def make_index_dir():
	'''
	Создает главный файл отчета (он всегда статичный) и директорию, куда будет 
	сваливать все списки файлов. Возвращает путь к этой папке
	'''
	open("index.htm", "w", encoding="utf-8").write(main_htm)
	if not os.path.exists("index"):
		os.mkdir("index")
	return os.path.abspath("index")


def make_left_file(all_keys, TGKW):
	left = open("left.htm", "w", encoding="utf-8")
	left.write(left_head)
	print("Формируем левый фрейм")##################################################################3
	for i in all_keys:
		print("ключевое слово:", i)###############################################################3#############
		left.write(s_pre + i + ".htm" + s_suf + i + '</A>&nbsp;')
		if len(i)>0: 
			file_count = '('+ str(len(TGKW.words[i])) + ')'
			print(file_count)##########################################################################
		else:
			print("не указываем количество файлов, так как имя пустое")#############################################33
			file_count = ""
		left.write(file_count + s_post + "\n")
	left.write(right_tail)
	left.close()


def make_right_frame(key):
	right = open(key + '.htm', "w", encoding="utf-8")
	right.write(right_main)
	right.write('<frame src="' + key + '_key.htm' + '" name="key" scrolling=no noresize>\n')
	right.write('<frame src="' + key + '_body.htm' + '" name="body">\n</frameset>\n</HTML>')
	right.close()


def make_right_key(key):
	fw=open(key + '_key.htm', "w", encoding="utf-8")
	fw.write(right_head)
	fw.write('<h2>' + key + '</h2><br><br>\n')
	fw.write(right_tail)
	fw.close()


