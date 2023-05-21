import re

from pypinyin import lazy_pinyin, Style
import Levenshtein

from shprote.logics.util import get_ignored_char_tr


def pinyin_exceptions_mod(str_in: str) -> str:
    pinyin_exc = {
        "马马虎虎": "mǎmǎhūhū",
    }
    for k, v in pinyin_exc.items():
        str_in = str_in.replace(k, v)
    return str_in


def levenshtein_massify(str_in: str) -> str:
    # Replace all punctuation marks with spaces
    str_in = str_in.lower().translate(get_ignored_char_tr())
    str_in = re.sub(
        r"(\s[āàáǎaēéěèeōóǒòo])", r"'\1", str_in)  # Add ' before words starting with a, e and o
    str_in = re.sub(r"\s", "", str_in)  # Remove spaces
    return str_in


def er_sound_mod(str_in: str) -> str:
    return re.sub(r"儿(?!子)", "r", str_in)


def compare_phon_repr(teacher_text, student_text) -> str:
    if len(teacher_text) == 0 or len(student_text) == 0:
        return {
            "type": "error",
            "name": "LEVENMASS_EMPTY_ERR",
            "msg": "Levenshtein mass cannot be empty. Please, check your request"
        }

    max_len = max(len(teacher_text), len(student_text))
    leven_dist = Levenshtein.distance(teacher_text, student_text)
    result_ratio = (max_len - leven_dist) / max_len
    result_ratio = round(result_ratio, 4)

    return {
        "type": "result",
        "total-ratio": result_ratio,
        "phon-mistakes": leven_dist,
        "teacher-said": teacher_text,
        "student-said": student_text
    }


def text_phonetizer(str_in: str) -> str:
    str_in = pinyin_exceptions_mod(str_in)
    str_in = er_sound_mod(str_in)
    str_in = " ".join(lazy_pinyin(
        str_in, style=Style.TONE, v_to_u=True, tone_sandhi=True))
    str_in = levenshtein_massify(str_in)
    return str_in


def compare_lang_text(teacher_data: str, student_data: str) -> dict:
    teacher_text, student_text = text_phonetizer(
        teacher_data), text_phonetizer(student_data)

    return compare_phon_repr(teacher_text, student_text)
