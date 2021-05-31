import logging
from logging.handlers import TimedRotatingFileHandler
import inspect
import time

format = logging.Formatter('%(levelname)-10s:  %(module)s - %(funcName)s - %(asctime)s %(message)s')


def log(func):
    def call_func(*args,**kwargs):
        with open('../hw_lesson5_log/server_logs/logfile-server.txt', 'a', encoding='utf-8') as f:
            f.write("%s Вызов функции %s из функции %s, %s: %s\n" % (time.ctime(), func.__name__, inspect.stack()[1][3], args, kwargs))
        r = func(*args,**kwargs)
        return r
    return call_func


def get_file_handler_rotation():
    app_log_hand_rotation = TimedRotatingFileHandler('../hw_lesson5_log/server_logs/logfile-server.txt',
                                                     encoding='utf-8', when="h", interval=24)
    app_log_hand_rotation.setFormatter(format)
    return app_log_hand_rotation


def get_logger(name):
    app_log = logging.getLogger(name)
    app_log.setLevel(logging.INFO)
    app_log.addHandler(get_file_handler_rotation())
    return app_log

