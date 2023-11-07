import datetime
import hashlib
import os
from time import time
from typing import Callable

import telebot.formatting as tf
import telebot.types as tt

from shprote.config import get_translator
from shprote.logics import Language, get_module_by_lang
from shprote.logics.util import telebot_diff
from shprote.logics.voice import audio_file_to_text
from shprote.temp import get_tmp

from ..bot import bot
from ..log import get_logger
from .common import generate_final_answer, render_main_menu

logger = get_logger()
voice_temp_dir = get_tmp("voice")


def render_stop_test_btn(translate_fn: Callable = lambda x: x):
    _ = translate_fn

    markup = tt.ReplyKeyboardMarkup(resize_keyboard=True)
    stop_btn = tt.KeyboardButton(_("❌ Stop"))
    markup.add(stop_btn)
    return markup


def start_pronun_test(message):
    _ = get_translator(message.from_user.language_code)

    # User cache used to confirm results
    user_hash_seed = str(datetime.datetime.now()) + " " + message.from_user.username
    user_hash = hashlib.sha1(user_hash_seed.encode("UTF-8")).hexdigest()[:12]

    bot.send_message(
        message.chat.id,
        tf.format_text(
            _(
                "The *pronunciation* check has started. _Please, remember that you cannot use replied or forwarded messages as student's answers._ Check's special code is"
            ),
            tf.mcode(user_hash),
            separator=" ",
        ),
    )

    # Next round
    bot.send_message(
        message.chat.id,
        _(
            "❓ Enter or redirect teacher's text or voice message or reply to it _(redirect and reply have the highest priority of the messages you send)_:"
        ),
        reply_markup=render_stop_test_btn(_),
    )
    bot.register_next_step_handler(
        message, get_teacher_text_and_print_stud, user_hash=user_hash
    )


def get_teacher_text_and_print_stud(message, user_hash):
    _ = get_translator(message.from_user.language_code)

    if message.text and message.text.strip() in (_("❌ Stop"), "/stop"):
        bot.send_message(
            message.chat.id,
            _("The check has been stopped. Getting back to the menu..."),
            reply_markup=render_main_menu(_),
        )
        return

    teacher = ""

    forwarded_msg = ""
    if message.forward_date:
        usr_name = (
            message.forward_sender_name
            if message.forward_from == None
            else f"@{message.forward_from.username}"
        )
        forwarded_msg = _("*[FORWARDED FROM {usr_name}]*").format(usr_name=usr_name)
    elif message.reply_to_message:
        usr_name = (
            None
            if not message.reply_to_message.from_user.username
            else f"@{message.reply_to_message.from_user.username}"
        )
        forwarded_msg = _("*[REPLIED TO {usr_name}]*").format(usr_name=usr_name)
        message = message.reply_to_message
    else:
        forwarded_msg = _("*[DONE BY THE STUDENT]*")

    if message.content_type == "text":
        teacher = message.text
        bot.send_message(
            message.chat.id,
            tf.format_text(
                _("Teacher wrote {forwarded_msg}: {teacher}").format(
                    forwarded_msg=forwarded_msg, teacher=teacher
                ),
                tf.mcode(user_hash),
            ),
        )
    # Teacher can send both audio and voice
    elif message.content_type in ("voice", "audio"):
        bot.send_message(
            message.chat.id, _("⏳ Processing the audio file, please, wait...")
        )

        file_info = ""
        file_id = 0x00000000

        if message.content_type == "voice":
            file_id = message.voice.file_id
        else:
            file_id = message.audio.file_id

        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Getting the extension
        ext = os.path.splitext(file_info.file_path)[1]
        if ext == ".oga":
            ext = ".ogg"

        save_path = os.path.join(
            voice_temp_dir, f"{message.chat.id}_{int(time())}{ext}"
        )

        with open(save_path, "wb+") as new_file:
            new_file.write(downloaded_file)

        logger.debug(f"Processing the audio file with path '{save_path}'...")

        try:
            teacher = audio_file_to_text(save_path, Language.Chinese)
        except:
            logger.error(
                "Something happened while processing user's audio:", exc_info=True
            )
            bot.send_message(
                message.chat.id,
                _("🔴 Cannot process this file, please, try another one:"),
                reply_markup=render_stop_test_btn(_),
            )
            bot.register_next_step_handler(
                message, get_teacher_text_and_print_stud, user_hash=user_hash
            )
            return

        bot.send_message(
            message.chat.id,
            tf.format_text(
                _(
                    "Teacher said {forwarded_msg}: {teacher}\n*The signed voice message itself will appear below*"
                ).format(forwarded_msg=forwarded_msg, teacher=teacher),
                tf.mcode(user_hash),
            ),
        )
        bot.send_audio(
            message.chat.id,
            file_id,
            tf.format_text(_("Teacher's signed voice message, "), tf.mcode(user_hash)),
        )
    else:
        bot.send_message(
            message.chat.id,
            _(
                '🔴 Wrong data type ("{data_type}"), please, send a voice message or an audio (.mp3, .ogg) file:'
            ).format(data_type=message.content_type),
            reply_markup=render_stop_test_btn(_),
        )
        bot.register_next_step_handler(
            message, get_teacher_text_and_print_stud, user_hash=user_hash
        )
        return

    bot.send_message(
        message.chat.id,
        _("❓ Student's voice record:"),
        reply_markup=render_stop_test_btn(_),
    )
    bot.register_next_step_handler(
        message,
        get_stud_and_calc_result,
        data={
            "hash": user_hash,
            "lang": "zh",
            "teacher": {"said": teacher, "type": "text"},
            "student": {"said": "", "type": "text"},
        },
    )


def get_stud_and_calc_result(message, data):
    """Student recognition step"""

    _ = get_translator(message.from_user.language_code)

    if message.text and message.text.strip() in (_("❌ Stop"), "/stop"):
        bot.send_message(
            message.chat.id,
            _("The check has been stopped. Getting back to the menu..."),
            reply_markup=render_main_menu(_),
        )
        return

    student = ""

    if message.forward_date or message.reply_to_message:
        bot.send_message(
            message.chat.id,
            _(
                "*The answer cannot be forwarded or be a reply. The test has been failed.*"
            ),
            reply_markup=render_main_menu(_),
        )
        logger.info(
            f"Someone has tried to cheat: @{message.from_user.username}, id is {message.from_user.id}"
        )
        return

    # Student cannot send audio
    if message.content_type == "voice":
        bot.send_message(
            message.chat.id, _("⏳ Processing the audio file, please, wait...")
        )

        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Getting the extension
        ext = os.path.splitext(file_info.file_path)[1]
        if ext == ".oga":
            ext = ".ogg"

        save_path = os.path.join(
            voice_temp_dir, f"{message.chat.id}_{int(time())}{ext}"
        )

        with open(save_path, "wb+") as new_file:
            new_file.write(downloaded_file)

        logger.debug(f"Processing the audio file with path '{save_path}'...")
        try:
            student = audio_file_to_text(save_path, Language.Chinese)
        except:
            logger.error(
                "Something happened while processing user's audio:", exc_info=True
            )
            bot.send_message(
                message.chat.id,
                _("🔴 Cannot process this file, please, try another one:"),
                reply_markup=render_stop_test_btn(_),
            )
            bot.register_next_step_handler(message, get_stud_and_calc_result, data=data)
            return

        bot.send_message(
            message.chat.id,
            tf.format_text(
                _(
                    "Student said: {student}\n*The signed voice message will appear below*"
                ).format(student=student),
                tf.mcode(data["hash"]),
            ),
        )
        bot.send_voice(
            message.chat.id,
            message.voice.file_id,
            tf.format_text(
                _("Student's signed voice message, "), tf.mcode(data["hash"])
            ),
        )
    else:
        bot.send_message(
            message.chat.id,
            _(
                '🔴 Wrong data type ("{data_type}"), please, send a _voice_ message:'
            ).format(data_type=message.content_type),
            reply_markup=render_stop_test_btn(_),
        )
        bot.register_next_step_handler(message, get_stud_and_calc_result, data=data)
        return

    bot.send_message(
        message.chat.id, _("Now wait a little..."), reply_markup=render_stop_test_btn(_)
    )

    data["student"]["said"] = student

    lng_mod = get_module_by_lang(Language.Chinese)

    check_result = lng_mod.compare_lang_text(
        data["teacher"]["said"], data["student"]["said"]
    )

    logger.debug("Pronunciation check result is " + str(check_result))

    markup = render_main_menu(_)
    bot.send_message(
        message.chat.id,
        generate_final_answer(_("pronunciation"), data, check_result, translate_fn=_),
        reply_markup=markup,
        parse_mode="HTML",
    )
