import hashlib
import datetime
from time import time
import os

import telebot.types as tt
import telebot.formatting as tf

from .common import *
from ..bot import bot
from shprote.logics import get_module_by_lang, Language
from shprote.logics.util import get_tmp
from shprote.logics.voice import audio_file_to_text
from ..log import get_logger

logger = get_logger()
voice_temp_dir = get_tmp("voice")


def render_stop_test_btn():
    markup = tt.ReplyKeyboardMarkup(resize_keyboard=True)
    stop_btn = tt.KeyboardButton(MSG_STOP)
    markup.add(stop_btn)
    return markup


def start_listening_test(message):
    # User cache used to confirm results
    user_hash_seed = str(datetime.datetime.now()) + \
        " " + message.from_user.username
    user_hash = hashlib.sha1(
        user_hash_seed.encode('UTF-8')).hexdigest()[:12]

    bot.send_message(
        message.chat.id, tf.format_text(
            f"The *listening* check has started. _Please, remember that you cannot use replied or forwarded messages as student's answers._ Check's special code is", tf.mcode(user_hash), separator=" "))

    # Next round
    bot.send_message(
        message.chat.id, "❓ Enter or redirect teacher's text or voice message or reply to it _(redirect and reply have the highest priority of the messages you send)_:", reply_markup=render_stop_test_btn())
    bot.register_next_step_handler(
        message, get_teacher_text_and_print_stud, user_hash=user_hash)


def get_teacher_text_and_print_stud(message, user_hash):
    if message.text and message.text.strip() in (MSG_STOP, "/stop"):
        bot.send_message(
            message.chat.id, "The check has been stopped. Getting back to the menu...",
            reply_markup=render_main_menu())
        return

    teacher = ""

    forwarded_msg = ""
    if message.forward_date:
        usr_name = message.forward_sender_name if message.forward_from == None else f"@{message.forward_from.username}"
        forwarded_msg = f"*[FORWARDED FROM {usr_name}]*"
    elif message.reply_to_message:
        usr_name = None if not message.reply_to_message.from_user.username else f"@{message.reply_to_message.from_user.username}"
        forwarded_msg = f"*[REPLIED TO {usr_name}]*"
        message = message.reply_to_message
    else:
        forwarded_msg = "*[DONE BY THE STUDENT]*"

    if message.content_type == "voice":
        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        save_path = os.path.join(
            voice_temp_dir, f'{message.chat.id}_{int(time())}.ogg')

        with open(save_path, 'wb+') as new_file:
            new_file.write(downloaded_file)

        logger.debug(f"Processing the audio file with path '{save_path}'...")
        teacher = audio_file_to_text(save_path, Language.Chinese)

        bot.send_voice(message.chat.id, message.voice.file_id,
                       tf.format_text(f"Teacher's signed voice message {forwarded_msg}", tf.mcode(user_hash)))
    else:
        bot.send_message(
            message.chat.id, "🔴 Wrong data type, please, retry:", reply_markup=render_stop_test_btn())
        bot.register_next_step_handler(
            message, get_teacher_text_and_print_stud, user_hash=user_hash)
        return

    bot.send_message(
        message.chat.id, "❓ Student's answer:", reply_markup=render_stop_test_btn())
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
    """ Student recognition step """
    if message.text and message.text.strip() in (MSG_STOP, "/stop"):
        bot.send_message(
            message.chat.id, "The check has been stopped. Getting back to the menu...",
            reply_markup=render_main_menu())
        return

    student = ""

    if message.forward_date or message.reply_to_message:
        bot.send_message(
            message.chat.id, "*The answer cannot be forwarded or be a reply. The test has been failed.*",
            reply_markup=render_main_menu())
        logger.info(
            f"Someone has tried to cheat: @{message.from_user.username}, id is {message.from_user.id}")
        return

    if message.content_type == "text":
        student = message.text.strip()
        bot.send_message(message.chat.id, tf.format_text(f"Student wrote: {student}",
                                                         tf.mcode(data["hash"])))
    else:
        bot.send_message(
            message.chat.id, "🔴 Wrong data type, please, retry:", reply_markup=render_stop_test_btn())
        bot.register_next_step_handler(
            message, get_stud_and_calc_result, data=data)
        return

    bot.send_message(
        message.chat.id, "Now wait a little...", reply_markup=render_stop_test_btn())

    data["student"]["said"] = student

    lng_mod = get_module_by_lang(Language.Chinese)

    check_result = lng_mod.compare_lang_text(data["teacher"]["said"],
                                             data["student"]["said"])

    logger.debug("Listening check result is " + str(check_result))

    if check_result["type"] == "error":
        check_result = f"""
*Something went wrong*
{tf.escape_markdown(check_result["name"])}: {check_result["msg"]}
""".strip()
    elif check_result["type"] == "result":
        result_total = check_result["total-ratio"] * 100

        check_result = f"""
*Your *listening* check result is {result_total:.2f}%*
_Now you can forward all the messages with the special code to your teacher_

Phonematic mistakes: {check_result["phon-mistakes"]}
Teacher's levenseq: {check_result["teacher-said"]}
Student's levenseq: {check_result["student-said"]}
""".strip()

    markup = render_main_menu()
    bot.send_message(
        message.chat.id, tf.format_text(str(check_result),
                                        tf.mcode(data["hash"]), separator=" "), reply_markup=markup)
