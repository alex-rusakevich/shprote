import telebot.formatting as tf
import telebot.types as tt

from shprote.bot import bot
from shprote.logics import *
from shprote.logics import Language
from shprote.logics.util import telebot_diff

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


def generate_final_answer(test_type: str, data: dict, check_result: dict) -> str:
    if check_result["type"] == "error":
        check_result = f"""
*Something went wrong*
{tf.escape_markdown(check_result["name"])}: {check_result["msg"]}
""".strip()
    elif check_result["type"] == "result":
        result_total = check_result["total-ratio"] * 100

        student_to_teacher = ""
        if result_total != 100:
            student_to_teacher = f"""\n\n<b>Student → teacher:</b>
{telebot_diff(check_result["teacher"]["repr"], check_result["student"]["repr"])}"""

        check_result = f"""
<b>Your {test_type} check result is {result_total:.2f}% ({check_result["phon-mistakes"]} phonematic mistake(s))</b>
<i>Now you can forward all the messages with the special code to your teacher</i>{student_to_teacher}

<b>Teacher's transcription:</b> {check_result["teacher"]["repr"]}

<b>Student's transcription:</b> {check_result["student"]["repr"]}
""".strip()

    return tf.format_text(str(check_result),
                          tf.hcode(data["hash"]))
