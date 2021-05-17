import logging
from logging.handlers import TimedRotatingFileHandler

format = logging.Formatter('%(levelname)-10s:  %(module)s - %(funcName)s - %(asctime)s %(message)s')


def get_file_handler_rotation():
    app_log_hand_rotation = TimedRotatingFileHandler('../hw_lesson5_log/server_logs/logfile-server.txt', encoding='utf-8', when="s", interval=15)
    app_log_hand_rotation.setFormatter(format)
    return app_log_hand_rotation

def get_file_handler():
    app_log_hand_rotation = logging.FileHandler('../hw_lesson5_log/logfile_main.txt', encoding='utf-8')
    app_log_hand_rotation.setFormatter(format)
    return app_log_hand_rotation


def get_logger(name):
    app_log = logging.getLogger(name)
    app_log.setLevel(logging.INFO)
    app_log.addHandler(get_file_handler())
    app_log.addHandler(get_file_handler_rotation())
    return app_log

