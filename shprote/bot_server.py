from shprote.config import get_config
from shprote.log import get_logger
from shprote import __version__
from shprote.routes.admin import check_tg_id
from shprote.routes.check import start_test
from shprote.common import *
from shprote.bot import bot

from shprote.db import DATABASE, DB_ENGINE

HELP = f"""
*Standardized 汉语 Pronunciation TEster {__version__}*
(https://github.com/alex-rusakevich/shprote)

/start — start the bot and go to the main menu
/help — display this message
/check — begin your pronunciation test. The special code / hash in bot replies is intended to avoid pupil cheating by sending different results or fake tasks
/stop — stop the test and go to main menu

_May 汉语 be with you!_
""".strip()

logger = get_logger()
config = get_config()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = render_main_menu()
    bot.send_message(
        message.chat.id, f"Hello there, {message.from_user.first_name}! I'm ready to check your pronunciation! 🤓",
        reply_markup=markup)


@bot.message_handler(content_types=['text'])
def main_text_handler(message):
    if (message.text in (MSG_CHECK, "/check")):
        start_test(message)
    elif (message.text in (MSG_MENU, "/menu")):
        bot.send_message(
            message.chat.id, "Welcome to the main menu!", reply_markup=render_main_menu())
    elif message.text.strip() in (MSG_STOP, "/stop"):
        bot.send_message(
            message.chat.id, "The check has been stopped. Getting back to the menu...",
            reply_markup=render_main_menu())
    elif (message.text in (MSG_HELP, "/help")):
        bot.send_message(
            message.chat.id, HELP, reply_markup=render_main_menu())
    elif message.text.lower() in ("я тебя люблю", "i love you",
                                  "我爱你", "я тебя люблю!", "i love you!", "我爱你！", "521", "520"):
        try:
            bot.send_sticker(
                message.chat.id, "CAACAgIAAxkBAAEJAkdkZJ2OU5DV1melgSjQGkkg7O9jkQACoBwAAipooUjogwEq_q_PRy8E",
                reply_markup=render_main_menu())
        except:
            bot.send_message(message.chat.id, "❤️",
                             reply_markup=render_main_menu())
    elif message.text == "/admin":
        bot.send_message(
            message.chat.id, "Checking your telegram id...")
        check_tg_id(message)
