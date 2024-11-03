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
import time

import flask
import telebot
from flask import Flask, redirect, request

from shprote.bot_server import bot
from shprote.config import BOT_TOKEN, get_config
from shprote.log import get_logger

logger = get_logger()
config = get_config()


WEBHOOK_URL_BASE = os.environ.get("OUTER_URL", "127.0.0.1")
WEBHOOK_URL_PATH = "/{}/".format(BOT_TOKEN)


app = Flask(__name__)
app.logger = logger


""" @app.before_request
def before_request():
    if "DYNO" in os.environ:  # Force heroku https
        if request.url.startswith("http://"):
            url = request.url.replace("http://", "https://", 1)
            code = 301
            return redirect(url, code=code) """


@app.route(WEBHOOK_URL_PATH, methods=["POST"])
def get_message():
    if request.headers.get("content-type") == "application/json":
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

bot.remove_webhook()
time.sleep(1)

bot.set_webhook(
    url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH,
    drop_pending_updates=config["bot"]["drop-pending"],
)

logger.info("Running in production mode: " + str(not app.debug))

# Starting waitress
wsgi_app = app.wsgi_app
