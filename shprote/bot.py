import telebot
from sqlalchemy.sql import text

from shprote.config import BOT_TOKEN, get_config
from shprote.db import DB_ENGINE, DB_SESSION
from shprote.log import get_logger


class TGExceptionHandler(telebot.ExceptionHandler):
    @staticmethod
    def handle(exception):
        get_logger().warning("An exception occured, pinging the database...")

        try:
            DB_ENGINE.connect().execute(text("SELECT 1;"))
        finally:
            get_logger().warning("Rolling back the database session...")
            DB_SESSION.rollback()


config = get_config()

bot = telebot.TeleBot(BOT_TOKEN, skip_pending=config["bot"]["drop-pending"],
                      parse_mode="Markdown", threaded=True, num_threads=int(config["bot"]["threads"]),
                      exception_handler=TGExceptionHandler)
