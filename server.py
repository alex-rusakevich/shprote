import os
import time

from flask import Flask, request, redirect
import flask
import telebot
from waitress import serve

from shprote.log import get_logger
from shprote.config import get_config, BOT_TOKEN
from shprote.bot_server import bot


logger = get_logger()
config = get_config()


WEBHOOK_URL_BASE = os.environ.get("OUTER_URL", "127.0.0.1")
WEBHOOK_URL_PATH = "/{}/".format(BOT_TOKEN)


app = Flask(__name__)
app.logger = logger


@app.route(WEBHOOK_URL_PATH, methods=['POST'])
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

bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)

logger.info("Running in production mode: " + str(not app.debug))

# Starting waitress
waitress_args = {}

if os.environ.get("DYNO"):  # Expose the socket to ngnix if running on Heroku
    waitress_args["unix_socket"] = "/tmp/nginx.socket"
    open('/tmp/app-initialized', 'w').close()
else:
    waitress_args = {
        "port": os.environ.get("PORT", 8080)
    }

serve(app.wsgi_app, **waitress_args)
