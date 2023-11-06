import re
import string

import Levenshtein
from pypinyin import Style, lazy_pinyin

from shprote.logics.util import CHINESE_IGNORED, purificator_tr


def pinyin_exceptions_mod(str_in: str) -> str:
    pinyin_exc = {"马马虎虎": "mǎmǎhūhū", "朋友": "péngyou"}
    for k, v in pinyin_exc.items():
        str_in = str_in.replace(k, v)
    return str_in


def levenshtein_massify(str_in: str) -> str:
    # Replace all punctuation marks with spaces
    str_in = str_in.lower().translate(purificator_tr)
    str_in = re.sub(
        r"(\s[āàáǎaēéěèeōóǒòo])", r"'\1", str_in
    )  # Add ' before words starting with a, e and o
    str_in = re.sub(r"\s", "", str_in)  # Remove spaces
    return str_in


def compare_phon_repr(teacher_levenseq, student_levenseq) -> str:
    if len(teacher_levenseq) == 0 or len(student_levenseq) == 0:
        return {
            "type": "error",
            "name": "LEVENMASS_EMPTY_ERR",
            "msg": "Levenshtein mass cannot be empty. Please, check your request",
        }

    max_len = max(len(teacher_levenseq), len(student_levenseq))
    leven_dist = Levenshtein.distance(teacher_levenseq, student_levenseq)
    result_ratio = (max_len - leven_dist) / max_len
    result_ratio = round(result_ratio, 4)

    return {
        "type": "result",
        "total-ratio": result_ratio,
        "phon-mistakes": leven_dist,
    }


def make_repr_from_text(str_in: str) -> str:
    str_in = pinyin_exceptions_mod(str_in)
    str_in = re.sub(r"儿(?!子)", "r", str_in)  # Erhua
    str_in = " ".join(
        lazy_pinyin(str_in, style=Style.TONE, v_to_u=True, tone_sandhi=True)
    )

    str_in = re.sub(rf"\s?([{re.escape(CHINESE_IGNORED)}])\s?", r"\1", str_in)
    str_in = re.sub(rf"\s?([{string.punctuation}])", r"\1", str_in)
    return str_in


def text_to_levenseq(str_in: str) -> str:
    str_in = make_repr_from_text(str_in)
    str_in = levenshtein_massify(str_in)
    return str_in


def compare_lang_text(teacher_data: str, student_data: str) -> dict:
    teacher_repr = make_repr_from_text(teacher_data)
    student_repr = make_repr_from_text(student_data)

    teacher_levenseq = levenshtein_massify(teacher_repr)
    student_levenseq = levenshtein_massify(student_repr)

    result = compare_phon_repr(teacher_levenseq, student_levenseq)

    result["teacher"], result["student"] = ({}, {})
    result["teacher"]["levenseq"] = teacher_levenseq
    result["teacher"]["repr"] = teacher_repr
    result["teacher"]["text"] = teacher_data

    result["student"]["levenseq"] = student_levenseq
    result["student"]["repr"] = student_repr
    result["student"]["text"] = student_data

    return result
