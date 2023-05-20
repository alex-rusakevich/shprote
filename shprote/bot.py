import os
from getpass import getpass

import telebot

from shprote.config import get_config, save_config
from shprote.log import get_logger
from shprote.db import DB_SESSION


class TGExceptionHandler(telebot.ExceptionHandler):
    @staticmethod
    def handle(exception):
        get_logger().warning("An exception occured, rolling back the database session...")
        DB_SESSION.rollback()


config = get_config()

# region Loading token
token = os.environ.get("BOT_TOKEN")
if not token:
    token = config["main"]["token"]
if not token:
    config["main"]["token"] = getpass("Bot API key: ")
    save_config()
    token = config["main"]["token"]
# endregion

bot = telebot.TeleBot(token, skip_pending=True,
                      parse_mode="Markdown", threaded=True, num_threads=int(config["main"]["threads"]),
                      exception_handler=TGExceptionHandler)
