#!/usr/bin/env python
import os
from urllib.parse import urljoin

from flask import Flask, request, redirect
import telebot

from shprote.log import get_logger
from shprote.config import get_config
from shprote.bot_server import bot
from shprote.temp import clean_temp


logger = get_logger()
config = get_config()

os.environ["TZ"] = config["main"]["timezone"]


def main():
    logger.info("Starting the bot...")

    if heroku_url := os.environ.get("HEROKU_URL"):
        server = Flask(__name__)

        @server.route("/bot", methods=['POST'])
        def get_message():
            bot.process_new_updates(
                [telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
            return "!", 200

        @server.route("/")
        def root_hook():
            return redirect("https://t.me/shprote_bot", 302)

        bot.remove_webhook()
        bot.set_webhook(url=urljoin(heroku_url, "bot"))

        logger.info("Heroku detected, running in webhook mode...")
        server.run(host="0.0.0.0", port=os.environ.get('PORT', 80))
    else:  # Running on localhost
        bot.remove_webhook()

        logger.info("Running in polling mode...")
        bot.infinity_polling(
            restart_on_change=config["main"]["debug"], path_to_watch=os.path.join(".", "shprote"))

    logger.info("The bot has stopped.")
    logger.info("Cleaning temp...")
    clean_temp()


if __name__ == "__main__":
    main()
