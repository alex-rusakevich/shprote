import os
from urllib.parse import urljoin

from flask import Flask, request, redirect
import telebot

from shprote.log import get_logger
from shprote.config import get_config
from shprote.bot_server import bot


logger = get_logger()
config = get_config()

app = Flask(__name__)
app.logger = logger


@app.route("/bot", methods=['POST'])
def get_message():
    bot.process_new_updates(
        [telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@app.route("/")
def root_hook():
    return redirect("https://t.me/shprote_bot", 302)


app.debug = config["main"]["debug"]
bot_url = os.environ.get("HEROKU_URL", "127.0.0.1")

bot.remove_webhook()
bot.set_webhook(url=urljoin(bot_url, "bot"))

logger.info("Running in production mode: " + str(not app.debug))

app.run(host="0.0.0.0", port=os.environ.get('PORT', 80))
