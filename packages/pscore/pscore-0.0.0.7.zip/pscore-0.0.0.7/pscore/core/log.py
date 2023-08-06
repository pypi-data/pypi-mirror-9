import logging
from datetime import datetime


class Log:
    use_stdout = True

    @staticmethod
    def error(text):
        if Log.use_stdout:
            print ("ERROR: " + Log.new_entry(text))
        else:
            logging.error(Log.new_entry(text))


    @staticmethod
    def warning(text):
        if Log.use_stdout:
            print ("WARNING: " + Log.new_entry(text))
        else:
            logging.warning(Log.new_entry(text))

    @staticmethod
    def info(text):
        if Log.use_stdout:
            print ("INFO: " + Log.new_entry(text))
        else:
            logging.info(Log.new_entry(text))

    @staticmethod
    def debug(text):
        if Log.use_stdout:
            print ("DEBUG: " + Log.new_entry(text))
        else:
            logging.debug(Log.new_entry(text))

    @staticmethod
    def new_entry(text):
        return Log.__date_text() + " " + text

    @staticmethod
    def __date_text():
        return datetime.now().strftime('%d/%m/%y %H:%M:%S')