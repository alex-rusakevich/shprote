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

import difflib
import string

import telebot.formatting as tf

from shprote.log import get_logger

CHINESE_IGNORED = "！？｡。＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏."
IGNORED_CHARACTERS = CHINESE_IGNORED + string.punctuation


logger = get_logger()

purificator_dict = dict.fromkeys(IGNORED_CHARACTERS, " ")
purificator_tr = str.maketrans(purificator_dict)


def telebot_diff(
    teacher: str, student: str, new_fn=tf.hunderline, delete_fn=tf.hstrikethrough
) -> str:
    str1, str2 = student, teacher

    user_chars = []
    for i, s in enumerate(difflib.ndiff(str1, str2)):
        ch = s[-1]

        if s[0] == " " or ch == " " or ch in IGNORED_CHARACTERS:
            user_chars.append(ch)
        elif s[0] == "-":
            user_chars.append(delete_fn(ch))
        elif s[0] == "+":
            user_chars.append(new_fn(ch))

    result = tf.format_text(*user_chars, separator="")
    for i in ("<s></s>", "<b></b>", "<i></i>", "<u></u>"):
        result = result.replace(i, "")

    logger.debug("Diff result: " + result)

    return result
