from arc import mainlog
LOGGER = mainlog.Logger()
__version__ = '0.58'
__date__ = '29.01.2022'


def get_unicode_encoding(file: str) -> None | str:
    """
    Определяет кодировку файла. Выбор небольшой: UTF8 или UTF16
    Файлы не в юникод-кодировке читаться не будут
    """
    e = None
    for enc in ['utf-8-sig', 'utf-16']:
        t = open(file, 'r', encoding=enc)
        try:
            t.readline()
        except UnicodeDecodeError:
            pass
        else:
            e = enc
            break
        finally:
            t.close()
    return e
