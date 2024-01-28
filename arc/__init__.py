from arc import mainlog
LOGGER = mainlog.Logger()
__version__ = '0.57'
__date__ = '07.09.2022'


def get_unicode_encoding(file: str) -> None|str:
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
