import logging
from logging.handlers import RotatingFileHandler
import os
import sys
from pathlib import Path

import telebot
import sqlalchemy

from shprote.config import get_config

DATA_DIR = os.path.abspath(".")

log_formatter = logging.Formatter(
    '[%(asctime)s] %(levelname)s %(funcName)s(%(lineno)d) %(message)s')

logfile_dir = os.path.join(DATA_DIR, "log")
Path(logfile_dir).mkdir(parents=True, exist_ok=True)
log_file = os.path.join(logfile_dir, "shprote.log")

shprote_handler = RotatingFileHandler(log_file, mode='a', maxBytes=get_config()["log"]["maxsize"],
                                      backupCount=get_config()["log"]["maxfiles"], encoding="utf8", delay=0)
LOG_LVL = logging.DEBUG if get_config()["main"]["debug"] else logging.INFO

shprote_handler.setFormatter(log_formatter)
shprote_handler.setLevel(LOG_LVL)

app_log = logging.getLogger('root')
app_log.setLevel(LOG_LVL)
app_log.addHandler(shprote_handler)

stdout_handler = None
if get_config()["log"]["stdout"]:
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(LOG_LVL)
    stdout_handler.setFormatter(log_formatter)
    app_log.addHandler(stdout_handler)


telebot.logger = app_log

# region SQLAlchemy logger
sqlalchemy_logger = logging.getLogger('sqlalchemy.engine')
sqlalchemy_logger.setLevel(LOG_LVL)
sqlalchemy_logger.addHandler(shprote_handler)
if get_config()["log"]["stdout"]:
    sqlalchemy_logger.addHandler(stdout_handler)
# endregion


def exception_hook(exc_type, exc_value, exc_traceback):
    logging.getLogger('root').exception(
        "Uncaught exception",
        exc_info=(exc_type, exc_value, exc_traceback)
    )


sys.excepthook = exception_hook


def get_logger():
    return logging.getLogger('root')
