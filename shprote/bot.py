from getpass import getpass
import datetime
import hashlib
import os
import sys

import telebot
import telebot.types as tt
import telebot.formatting as tf

from shprote.config import get_config, save_config
from shprote.log import get_logger
from shprote.main import check_pronunciation
from shprote import __version__


MSG_CHECK = "📝 Check"
MSG_HELP = "❓ Help"
MSG_MENU = "🍱 Menu"
MSG_STOP = "❌ Stop"

MSG_SHUTDOWN = "🔴 Shutdown"
MSG_LOG = "📜 Log"

HELP = f"""
*Standardized 汉语 Pronunciation TEster {__version__}*
(https://github.com/alex-rusakevich/shprote)

/start — start the bot and go to the main menu
/help — display this message
/check — begin your pronunciation test. The special code / hash in bot replies is intended to avoid pupil cheating by sending different results or fake tasks
/stop — stop the test and go to main menu
/menu — get to bot's menu

_May 汉语 be with you!_
""".strip()

logger = get_logger()
config = get_config()

token = os.environ.get("BOT_TOKEN")
if not token:
    token = config["main"]["token"]
if not token:
    config["main"]["token"] = getpass("Bot API key: ")
    save_config()
    token = config["main"]["token"]

admin_pass = os.environ.get("ADMIN_PASS")
if not admin_pass:
    admin_pass = config["main"]["admin-pass"]
if not admin_pass:
    config["main"]["admin-pass"] = getpass("Bot API key: ")
    save_config()
    admin_pass = admin_pass["main"]["admin-pass"]

bot = telebot.TeleBot(token, skip_pending=True,
                      parse_mode="Markdown", threaded=True)


def render_main_menu():
    markup = tt.ReplyKeyboardMarkup(resize_keyboard=True)
    check_btn = tt.KeyboardButton(MSG_CHECK)
    help_btn = tt.KeyboardButton(MSG_HELP)
    markup.add(check_btn, help_btn)
    return markup


def render_stop_test_btn():
    markup = tt.ReplyKeyboardMarkup(resize_keyboard=True)
    stop_btn = tt.KeyboardButton(MSG_STOP)
    markup.add(stop_btn)
    return markup


def render_admin():
    markup = tt.ReplyKeyboardMarkup(resize_keyboard=True)
    menu_btn = tt.KeyboardButton(MSG_MENU)
    shutdown_btn = tt.KeyboardButton(MSG_SHUTDOWN)
    log_btn = tt.KeyboardButton(MSG_LOG)
    markup.add(menu_btn, shutdown_btn, log_btn)
    return markup


def menu_handler(message):
    markup = render_main_menu()
    bot.send_message(
        message.chat.id, "Welcome to the menu!", reply_markup=markup, disable_web_page_preview=True)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = render_main_menu()
    bot.send_message(
        message.chat.id, f"Hello there, {message.from_user.first_name}! I'm ready to check your pronunciation! 🤓",
        reply_markup=markup)


@bot.message_handler(content_types=['text'])
def main_text_handler(message):
    if (message.text in (MSG_CHECK, "/check")):
        # User cache used to confirm results
        user_hash_seed = str(datetime.datetime.now()) + \
            " " + message.from_user.username
        user_hash = hashlib.sha1(
            user_hash_seed.encode('UTF-8`')).hexdigest()[:12]

        bot.send_message(
            message.chat.id, tf.format_text(
                f"The check has started. Check's special code is", tf.mcode(user_hash), separator=" "))

        # Next round
        bot.send_message(
            message.chat.id, "Enter teacher's text:", reply_markup=render_stop_test_btn())
        bot.register_next_step_handler(
            message, get_teacher_text_and_print_stud, user_hash=user_hash)
    elif (message.text in (MSG_HELP, "/help")):
        markup = tt.ReplyKeyboardMarkup(resize_keyboard=True)
        menu_btn = tt.KeyboardButton(MSG_MENU)
        markup.add(menu_btn)

        bot.send_message(
            message.chat.id, HELP, reply_markup=markup)
    # Stop test will be redirected to here
    elif message.text in (MSG_MENU, "/menu"):
        menu_handler(message)
    elif message.text.lower() in ("я тебя люблю", "i love you", "我爱你"):
        bot.send_message(message.chat.id, "❤️",
                         reply_markup=render_main_menu())
    elif message.text == "/admin":
        bot.send_message(
            message.chat.id, "Enter the password:")
        bot.register_next_step_handler(
            message, check_admin_password)


def check_admin_password(message):
    if message.text != admin_pass:
        bot.send_message(
            message.chat.id, "The password is wrong, returning to the main menu", reply_markup=render_main_menu())
        return

    bot.send_message(message.chat.id, "Hello, admin!",
                     reply_markup=render_admin())
    bot.register_next_step_handler(
        message, admin_commands)


def admin_commands(message):
    if message.text in ("/menu", MSG_MENU):
        bot.send_message(
            message.chat.id, "Switching back to the menu...", reply_markup=render_main_menu())
        return
    elif message.text in ("/shutdown", MSG_SHUTDOWN):
        logger.warning("Admin has shutdowned the bot, stopping...")
        bot.stop_bot()
        sys.exit(0)


def get_teacher_text_and_print_stud(message, user_hash):
    teacher = message.text.strip()
    if teacher in (MSG_STOP, "/stop"):
        bot.send_message(
            message.chat.id, "The check has been stopped. Getting back to the menu...",
            reply_markup=render_main_menu())
        return

    bot.send_message(message.chat.id, tf.format_text(f"Teacher said: {teacher}",
                                                     tf.mcode(user_hash)))

    bot.send_message(
        message.chat.id, "Enter student's text:", reply_markup=render_stop_test_btn())
    bot.register_next_step_handler(
        message, get_stud_and_calc_result, data={
            "hash": user_hash,
            "lang": "zh",
            "teacher": {
                "said": teacher,
                "type": "text"
            },
            "student": {
                "said": "",
                "type": "text"
            }
        })


def get_stud_and_calc_result(message, data):
    student = message.text.strip()

    if student in (MSG_STOP, "/stop"):
        bot.send_message(
            message.chat.id, "The check has been stopped. Getting back to the menu...",
            reply_markup=render_main_menu())
        return

    bot.send_message(message.chat.id, tf.format_text(f"Student said: {student}",
                                                     tf.mcode(data["hash"])))

    bot.send_message(
        message.chat.id, "Now wait a little...", reply_markup=render_stop_test_btn())

    data["student"]["said"] = student

    check_result = check_pronunciation(data["teacher"]["said"], data["teacher"]["type"],
                                       data["student"]["said"], data["student"]["type"], data["lang"])

    logger.debug("Pronunciation check result is " + str(check_result))

    if check_result["type"] == "error":
        check_result = f"""
*Something went wrong*
{check_result["name"]}: {check_result["msg"]}
""".strip()
    elif check_result["type"] == "result":
        result_total = check_result["total-ratio"] * 100

        check_result = f"""
*Your result is {result_total:.2f}%*
_Now you can forward all the messages with the special code to your teacher_

Phonematic mistakes: {check_result["phon-mistakes"]}
Teacher's levenseq: {check_result["teacher-said"]}
Student's levenseq: {check_result["student-said"]}
""".strip()

    markup = render_main_menu()
    bot.send_message(
        message.chat.id, tf.format_text(str(check_result),
                                        tf.mcode(data["hash"]), separator=" "), reply_markup=markup)
