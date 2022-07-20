import logging
import time

class Logger(logging.Logger):
    __instance = None
    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, *args, **kwargs):
        args = ['mainlog', logging.DEBUG]
        super().__init__(*args, **kwargs)
        self.config()

    def config(self):
        cur_date = time.time()
        str_time = time.strftime("%Y.%m.%d_%H.%M.%S", time.localtime(cur_date))
        log_filename = f"archisrez_{str_time}.log"
        handler = logging.FileHandler(log_filename)
        frmt = logging.Formatter(fmt="%(asctime)s  %(module)s %(funcName)s : %(message)s")
        handler.setFormatter(frmt)
        self.addHandler(handler)
