# Shprote bot - Standardized Hanyu (Chinese) PROnunciation TEster
# Copyright (C) 2023, 2024 Alexander Rusakevich

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

import telebot

from shprote.config import get_config

DATA_DIR = os.path.abspath(".")

log_formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)s %(funcName)s(%(lineno)d) %(message)s"
)

logfile_dir = os.path.join(DATA_DIR, "log")
Path(logfile_dir).mkdir(parents=True, exist_ok=True)
log_file = os.path.join(logfile_dir, "shprote.log")

shprote_handler = RotatingFileHandler(
    log_file,
    mode="a",
    maxBytes=get_config()["log"]["maxsize"],
    backupCount=get_config()["log"]["maxfiles"],
    encoding="utf8",
    delay=0,
)
LOG_LVL = logging.DEBUG if get_config()["main"]["debug"] else logging.INFO

shprote_handler.setFormatter(log_formatter)
shprote_handler.setLevel(LOG_LVL)

app_log = logging.getLogger("root")
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
sqlalchemy_logger = logging.getLogger("sqlalchemy.engine.base.Engine")
for hdlr in sqlalchemy_logger.handlers:
    sqlalchemy_logger.removeHandler(hdlr)
sqlalchemy_logger.setLevel(LOG_LVL)
sqlalchemy_logger.addHandler(shprote_handler)
if get_config()["log"]["stdout"]:
    sqlalchemy_logger.addHandler(stdout_handler)
# endregion


# region Waitress logger
waitress_logger = logging.getLogger("waitress")
if waitress_logger:
    for hdlr in waitress_logger.handlers:
        waitress_logger.removeHandler(hdlr)
    waitress_logger.setLevel(LOG_LVL)
    waitress_logger.addHandler(shprote_handler)
    if get_config()["log"]["stdout"]:
        waitress_logger.addHandler(stdout_handler)
# endregion


def exception_hook(exc_type, exc_value, exc_traceback):
    logging.getLogger("root").exception(
        "Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback)
    )


sys.excepthook = exception_hook


def get_logger():
    return logging.getLogger("root")
