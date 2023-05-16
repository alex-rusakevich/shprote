#!/usr/bin/env python

from getpass import getpass
import datetime
import hashlib
import os

import telebot
import telebot.types as tt
import telebot.formatting as tf

from shprote.config import load_config, save_config
from shprote.log import get_logger
from shprote.main import check_pronunciation
from shprote import __version__

MSG_CHECK = "📝 Check"
MSG_HELP = "❓ Help"
MSG_MENU = "🍱 Menu"
MSG_STOP = "❌ Stop"

HELP = f"""
<b>Standardized 汉语 Pronunciation TEster {__version__}</b>
(https://github.com/alex-rusakevich/shprote)

/start — start the bot and go to the main menu
/help — display this message
/check — begin your pronunciation test. The special code / hash in bot replies is intended to avoid pupil cheating by sending different results or fake tasks
/stop — stop the test and go to main menu
/menu — get to bot's menu

<i>May the 汉语 be with you!</i>
""".strip()

logger = get_logger()
config = load_config()

token = os.environ.get("BOT_TOKEN")
if not token:
    token = config["main"]["token"]
if not token:
    config["main"]["token"] = getpass("Bot API key: ")
    save_config()
    token = config["main"]["token"]

bot = telebot.TeleBot(token, skip_pending=True)


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
                f"The check has started. Check's special code is", tf.mcode(user_hash), separator=" "), parse_mode="Markdown")

        # Next round
        bot.send_message(
            message.chat.id, "Enter teacher's text:", reply_markup=render_stop_test_btn(), parse_mode="Markdown")
        bot.register_next_step_handler(
            message, get_teacher_text_and_print_stud, user_hash=user_hash)
    elif (message.text in (MSG_HELP, "/help")):
        markup = tt.ReplyKeyboardMarkup(resize_keyboard=True)
        menu_btn = tt.KeyboardButton(MSG_MENU)
        markup.add(menu_btn)

        bot.send_message(
            message.chat.id, HELP, reply_markup=markup, parse_mode="HTML")
    # Stop test will be redirected to here
    elif message.text in (MSG_MENU, "/menu"):
        menu_handler(message)


def get_teacher_text_and_print_stud(message, user_hash):
    teacher = message.text.strip()
    if teacher in (MSG_STOP, "/stop"):
        bot.send_message(
            message.chat.id, "The check has been stopped. Getting back to the menu...",
            reply_markup=render_main_menu(), parse_mode="Markdown")
        return

    bot.send_message(message.chat.id, tf.format_text(f"Teacher said: {teacher}",
                                                     tf.mcode(user_hash)), parse_mode="Markdown")

    bot.send_message(
        message.chat.id, "Enter student's text:", reply_markup=render_stop_test_btn(), parse_mode="Markdown")
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
            reply_markup=render_main_menu(), parse_mode="Markdown")
        return

    bot.send_message(message.chat.id, tf.format_text(f"Student said: {student}",
                                                     tf.mcode(data["hash"])), parse_mode="Markdown")

    bot.send_message(
        message.chat.id, "Now wait a little...", reply_markup=render_stop_test_btn(), parse_mode="Markdown")

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
                                        tf.mcode(data["hash"]), separator=" "), reply_markup=markup, parse_mode="Markdown")


def main():
    logger.info("Starting the bot...")
    bot.infinity_polling(
        restart_on_change=config["main"]["debug"], path_to_watch=os.path.join(".", "shprote"))
    logger.info("The bot has stopped.")


if __name__ == "__main__":
    main()
