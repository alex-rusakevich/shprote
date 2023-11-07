from typing import Callable

import telebot.formatting as tf
import telebot.types as tt

from shprote.bot import bot
from shprote.config import get_translator
from shprote.logics import *
from shprote.logics import Language
from shprote.logics.util import telebot_diff

MSG_MENU = "🍱 Menu"
MSG_STOP = "❌ Stop"


def render_main_menu(translate_fn: Callable = lambda x: x):
    _ = translate_fn

    markup = tt.ReplyKeyboardMarkup(resize_keyboard=True)
    check_prn_btn = tt.KeyboardButton(_("🎤 Check pronunciation"))
    check_listen = tt.KeyboardButton(_("👂 Check listening"))
    help_btn = tt.KeyboardButton(_("❓ Help"))

    markup.row(check_listen, check_prn_btn)
    markup.row(help_btn)
    return markup


languages_menu_captions = {"🇨🇳 中文": Language.Chinese}


def language_menu_node(message, callback_fn, *callback_args, **callback_kwargs):
    _ = get_translator(message.from_user.language_code)

    markup = tt.ReplyKeyboardMarkup()
    for k, undef in languages_menu_captions.items():
        markup.add(tt.KeyboardButton(k))
    bot.send_message(
        message.chat.id, _("Choose your language, please:"), reply_markup=markup
    )
    bot.register_next_step_handler(
        message, language_handler, callback_fn, *callback_args, **callback_kwargs
    )


def language_handler(message, callback_fn, *callback_args, **callback_kwargs):
    _ = get_translator(message.from_user.language_code)

    language_menu_commands = {
        "/" + v.lower().strip(): k for k, v in langcode_to_name.items()
    }

    lang = languages_menu_captions.get(message.text) or language_menu_commands.get(
        message.text
    )
    if lang == None:
        bot.send_message(
            message.chat.id,
            _("🔴 There is no such language: {langname}").format(langname=message.text),
        )
        bot.register_next_step_handler(message, language_menu_node)
        return
    callback_fn(*callback_args, lang=lang, **callback_kwargs)


def generate_final_answer(
    test_type: str, data: dict, check_result: dict, translate_fn: Callable
) -> str:
    _ = translate_fn

    if check_result["type"] == "error":
        check_result = (
            _(
                """
*Something went wrong*
{err_name}: {err_msg}
"""
            )
            .format(
                err_name=tf.escape_markdown(check_result["name"]),
                err_msg=check_result["msg"],
            )
            .strip()
        )
    elif check_result["type"] == "result":
        result_total = check_result["total-ratio"] * 100

        student_to_teacher = ""
        if result_total != 100:
            student_to_teacher = _(
                """\n\n<b>Student → teacher:</b>
{telebot_diff}"""
            ).format(
                telebot_diff=telebot_diff(
                    check_result["teacher"]["repr"], check_result["student"]["repr"]
                )
            )

        check_result = (
            _(
                """
<b>Your {test_type} check result is {perc}% ({phon_mistakes} phonematic mistake(s))</b>
<i>Now you can forward all the messages with the special code to your teacher</i>{student_to_teacher}

<b>Teacher's transcription:</b> {teacher_repr}

<b>Student's transcription:</b> {student_repr}
"""
            )
            .format(
                perc=f"{result_total:.2f}",
                phon_mistakes=check_result["phon-mistakes"],
                student_to_teacher=student_to_teacher,
                teacher_repr=check_result["teacher"]["repr"],
                student_repr=check_result["student"]["repr"],
            )
            .strip()
        )

    return tf.format_text(str(check_result), tf.hcode(data["hash"]))
