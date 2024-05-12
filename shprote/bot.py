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

bot = telebot.TeleBot(
    BOT_TOKEN,
    skip_pending=config["bot"]["drop-pending"],
    parse_mode="Markdown",
    threaded=True,
    num_threads=int(config["bot"]["threads"]),
    exception_handler=TGExceptionHandler,
)
