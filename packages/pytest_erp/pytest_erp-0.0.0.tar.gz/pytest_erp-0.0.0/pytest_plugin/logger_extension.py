import os

__author__ = 'kiryl_zayets'
from logging import handlers, Filter

class ExtRotatingFileHandler(handlers.RotatingFileHandler):
    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=False):
        path = os.path.dirname(os.path.abspath(__file__))
        custom_path = os.path.join(path, 'log', filename)
        super().__init__(filename=custom_path, maxBytes=maxBytes, backupCount=backupCount)


class ExtHttpHandler(handlers.HTTPHandler):
    def emit(self, record):
        pass

class RestFilter(Filter):
    def filter(self, record):
        res = [i for i in (record.funcName, record.module, record.filename) if i.find('test')>=0]
        if res:
            return 1
        return 0
