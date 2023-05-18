import hashlib
import datetime

import telebot.types as tt
import telebot.formatting as tf

from ..common import *
from ..bot import bot
from ..main import check_pronunciation
from ..log import get_logger

logger = get_logger()


def render_stop_test_btn():
    markup = tt.ReplyKeyboardMarkup(resize_keyboard=True)
    stop_btn = tt.KeyboardButton(MSG_STOP)
    markup.add(stop_btn)
    return markup


def start_test(message):
    # User cache used to confirm results
    user_hash_seed = str(datetime.datetime.now()) + \
        " " + message.from_user.username
    user_hash = hashlib.sha1(
        user_hash_seed.encode('UTF-8')).hexdigest()[:12]

    bot.send_message(
        message.chat.id, tf.format_text(
            f"The check has started. Check's special code is", tf.mcode(user_hash), separator=" "))

    # Next round
    bot.send_message(
        message.chat.id, "Enter teacher's text:", reply_markup=render_stop_test_btn())
    bot.register_next_step_handler(
        message, get_teacher_text_and_print_stud, user_hash=user_hash)


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
{tf.escape_markdown(check_result["name"])}: {check_result["msg"]}
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
