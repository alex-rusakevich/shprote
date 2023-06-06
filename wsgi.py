import os
import time
from urllib.parse import urljoin

from flask import Flask, request, redirect
import flask
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
    if request.headers.get("content-type") == "application/json" and (
        request.url_root.startswith(
            "https://api.telegram.org")  # Security check
    ):
        json_string = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ""
    else:
        flask.abort(403)


@app.route("/")
def root_hook():
    return redirect("https://t.me/shprote_bot", 302)


app.debug = config["main"]["debug"]
bot_url = os.environ.get("HEROKU_URL", "127.0.0.1")

bot.remove_webhook()
time.sleep(1)

bot.set_webhook(url=urljoin(bot_url, "bot"))

logger.info("Running in production mode: " + str(not app.debug))
