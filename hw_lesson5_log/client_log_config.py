import logging

format = logging.Formatter('%(levelname)-10s:  %(name)s - %(module)s - %(funcName)s - %(asctime)s %(message)s')


def get_file_handler():
    app_log_hand = logging.FileHandler('../hw_lesson5_log/logfile_main.txt', encoding='utf-8')
    app_log_hand.setFormatter(format)
    return app_log_hand


def get_logger(name):
    app_log = logging.getLogger(name)
    app_log.setLevel(logging.INFO)
    app_log.addHandler(get_file_handler())
    return app_log