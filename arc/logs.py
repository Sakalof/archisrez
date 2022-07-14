import csv
csv.register_dialect('archivar', delimiter='\t', doublequote=False, quotechar='"', lineterminator='\n', escapechar='')

class LogObj:
    def __init__(self, name, fnames):
        self.file =open(name, "w", encoding = "utf16")
        self.writer = csv.DictWriter(name, fieldnames=fnames, dialect='archivar')

    def write(self, row):
        self.writer.writerow(row)

    def close(self):
        self.file.close()


class ErrLog(LogObj):
    def __init__(self):
        super().__init__()

class CopyLog(LogObj):
    pass