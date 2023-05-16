#!/usr/bin/env python

from getpass import getpass
import datetime
import hashlib

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

HELP = f"""
<b>Standardized 汉语 Pronunciation TEster {__version__}</b>
(https://github.com/alex-rusakevich/shprote)

/start — start the bot and go to the main menu
/help — display this message
/check — begin your pronunciation test
/menu — get to bot's menu

<i>May the 汉语 be with you!</i>
""".strip()

logger = get_logger()
config = load_config()

if not config["main"]["token"]:
    config["main"]["token"] = getpass("Bot API key: ")
    save_config()

bot = telebot.TeleBot(config["main"]["token"], skip_pending=True)


def render_main_menu():
    markup = tt.ReplyKeyboardMarkup(resize_keyboard=True)
    check_btn = tt.KeyboardButton(MSG_CHECK)
    help_btn = tt.KeyboardButton(MSG_HELP)
    markup.add(check_btn, help_btn)
    return markup


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
            message.chat.id, "Enter teacher's text:", parse_mode="Markdown")
        bot.register_next_step_handler(
            message, get_teacher_text_and_print_stud, user_hash=user_hash)
    elif (message.text in (MSG_HELP, "/help")):
        markup = tt.ReplyKeyboardMarkup(resize_keyboard=True)
        menu_btn = tt.KeyboardButton(MSG_MENU)
        markup.add(menu_btn)

        bot.send_message(
            message.chat.id, HELP, reply_markup=markup, parse_mode="HTML")
    elif message.text in (MSG_MENU, "/menu"):
        markup = render_main_menu()
        bot.send_message(
            message.chat.id, "Welcome to the menu!", reply_markup=markup, disable_web_page_preview=True)


def get_teacher_text_and_print_stud(message, user_hash):
    teacher = message.text.strip()
    bot.reply_to(message, tf.format_text(
        tf.mcode(user_hash)), parse_mode="Markdown")

    bot.send_message(
        message.chat.id, "Enter student's text:", parse_mode="Markdown")
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
    bot.reply_to(message, tf.format_text(
        tf.mcode(data["hash"])), parse_mode="Markdown")

    data["student"]["said"] = student

    bot.send_message(
        message.chat.id, "Now wait a little...", parse_mode="Markdown")

    check_result = check_pronunciation(data["teacher"]["said"], data["teacher"]["type"],
                                       data["student"]["said"], data["student"]["type"], data["lang"])

    logger.debug("Pronunciation check result is " + str(check_result))

    if check_result["type"] == "error":
        check_result = f"""
*Something went wrong*
{check_result["type"]}: {check_result["msg"]}
""".strip()
    elif check_result["type"] == "result":
        result_total = check_result["total-ratio"] * 100

        check_result = f"""
*Your result is {result_total:.2f}%*

Phonematic mistakes: {check_result["phon-mistakes"]}
Teacher's levenseq: {check_result["teacher-said"]}
Student's levenseq: {check_result["student-said"]}
""".strip()

    bot.send_message(
        message.chat.id, tf.format_text(str(check_result),
                                        tf.mcode(data["hash"]), separator=" "), parse_mode="Markdown")


def main():
    logger.info("Starting the bot...")
    bot.infinity_polling()
    logger.info("The bot has stopped.")


if __name__ == "__main__":
    main()
