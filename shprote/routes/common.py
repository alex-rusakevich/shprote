# Shprote bot - Standardized Hanyu (Chinese) PROnunciation TEster
# Copyright (C) 2023, 2024 Alexander Rusakevich

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from typing import Callable

import telebot.formatting as tf
import telebot.types as tt

from shprote.logics.util import telebot_diff


def render_main_menu(translate_fn: Callable = lambda x: x):
    _ = translate_fn

    markup = tt.ReplyKeyboardMarkup(resize_keyboard=True)
    check_prn_btn = tt.KeyboardButton(_("🎤 Check pronunciation"))
    check_listen = tt.KeyboardButton(_("👂 Check listening"))
    help_btn = tt.KeyboardButton(_("❓ Help"))

    markup.row(check_listen, check_prn_btn)
    markup.row(help_btn)
    return markup


def generate_final_answer(
    test_type: str, data: dict, check_result: dict, translate_fn: Callable = lambda x: x
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

        check_result = _(
            """<b>Your {test_type} check result is {perc}% ({phon_mistakes} phonematic mistake(s))</b>
<i>Now you can forward all the messages with the special code to your teacher</i>{student_to_teacher}

<b>Teacher's transcription:</b> {teacher_repr}

<b>Student's transcription:</b> {student_repr}"""
        ).format(
            perc=f"{result_total:.2f}",
            phon_mistakes=check_result["phon-mistakes"],
            student_to_teacher=student_to_teacher,
            teacher_repr=check_result["teacher"]["repr"],
            student_repr=check_result["student"]["repr"],
            test_type=test_type,
        )

    return tf.format_text(str(check_result), tf.hcode(data["hash"]))
