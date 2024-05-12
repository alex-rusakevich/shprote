#!/usr/bin/env python
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

import os

from shprote.bot_server import bot
from shprote.config import get_config
from shprote.log import get_logger
from shprote.temp import clean_temp

logger = get_logger()
config = get_config()


def main():
    logger.info("Starting the bot...")
    bot.remove_webhook()

    logger.info("Running in polling mode...")
    bot.infinity_polling(
        restart_on_change=config["main"]["debug"],
        path_to_watch=os.path.join(".", "shprote"),
    )

    logger.info("The bot has stopped.")
    logger.info("Cleaning temp...")
    clean_temp()


if __name__ == "__main__":
    main()
