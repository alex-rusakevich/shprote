import difflib
import string

import telebot.formatting as tf

from shprote.log import get_logger

CHINESE_IGNORED = (
    "！？｡。＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰〾〿–—‘’‛“”„‟…‧﹏."
)
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
