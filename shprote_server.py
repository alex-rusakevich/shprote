#!/usr/bin/env python

import os

from shprote.log import get_logger
from shprote.config import get_config
from shprote.bot_server import bot


logger = get_logger()
config = get_config()

os.environ["TZ"] = config["main"]["timezone"]


def main():
    logger.info("Starting the bot...")
    bot.infinity_polling(
        restart_on_change=config["main"]["debug"], path_to_watch=os.path.join(".", "shprote"))
    logger.info("The bot has stopped.")


if __name__ == "__main__":
    main()
