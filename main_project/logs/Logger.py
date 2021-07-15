import logging
from logging.handlers import TimedRotatingFileHandler


class Logger:
    def __init__(self):
        self.format = logging.Formatter('%(levelname)-10s:  %(module)s - %(funcName)s - %(asctime)s %(message)s')

    def get_file_handler_rotation(self):
        app_log_hand_rotation = TimedRotatingFileHandler('/logs/logfile-server.txt',
                                                         encoding='utf-8', when="h", interval=24)
        app_log_hand_rotation.setFormatter(self.format)
        return app_log_hand_rotation

    def log(self, name):
        app_log = logging.getLogger(name)
        app_log.setLevel(logging.INFO)
        app_log.addHandler(self.get_file_handler_rotation())
        return app_log
