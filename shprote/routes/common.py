import telebot.types as tt
from shprote.logics import Language
from shprote.bot import bot
from shprote.logics import *


MSG_CHECK_PRONUN = "🎤 Check pronunciation"
MSG_CHECK_LISTEN = "👂 Check listening"
MSG_HELP = "❓ Help"
MSG_MENU = "🍱 Menu"
MSG_STOP = "❌ Stop"


def render_main_menu():
    markup = tt.ReplyKeyboardMarkup(resize_keyboard=True)
    check_prn_btn = tt.KeyboardButton(MSG_CHECK_PRONUN)
    check_listen = tt.KeyboardButton(MSG_CHECK_LISTEN)
    help_btn = tt.KeyboardButton(MSG_HELP)
    markup.add(check_listen, check_prn_btn, help_btn)
    return markup


languages_menu_captions = {
    "🇨🇳 中文": Language.Chinese
}


def language_menu_node(message, callback_fn, *callback_args, **callback_kwargs):
    markup = tt.ReplyKeyboardMarkup()
    for k, _ in languages_menu_captions.items():
        markup.add(tt.KeyboardButton(k))
    bot.send_message(
        message.chat.id, "Choose your language, please:", reply_markup=markup)
    bot.register_next_step_handler(
        message, language_handler, callback_fn, *callback_args, **callback_kwargs)


def language_handler(message, callback_fn, *callback_args, **callback_kwargs):
    language_menu_commands = {
        "/" + v.lower().strip(): k for k, v in langcode_to_name.items()}

    lang = languages_menu_captions.get(
        message.text) or language_menu_commands.get(message.text)
    if lang == None:
        bot.send_message(
            message.chat.id, f"🔴 There is no such language: {message.text}")
        bot.register_next_step_handler(
            message, language_menu_node)
        return
    callback_fn(*callback_args, lang=lang, **callback_kwargs)
