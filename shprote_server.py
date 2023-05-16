#!/usr/bin/env python

from getpass import getpass

import telebot
import telebot.types as tt

from shprote.config import load_config, save_config
from shprote.log import get_logger

MSG_CHECK = "📝 Check"
MSG_HELP = "❓ Help"
MSG_MENU = "🍱 Menu"

HELP = """
<b>Standardized 汉语 Pronunciation TEster</b>
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
        markup = render_main_menu()
        bot.send_message(
            message.chat.id, "Sorry, this function is not available yet. Switching back to the main menu",
            reply_markup=markup)
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


def main():
    logger.info("Starting the bot...")
    bot.infinity_polling()
    logger.info("The bot has stopped.")


if __name__ == "__main__":
    main()
