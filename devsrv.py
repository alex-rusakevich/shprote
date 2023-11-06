#!/usr/bin/env python
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
