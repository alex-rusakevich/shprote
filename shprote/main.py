import re
import sys
import re
import os
from unicodedata import category
from pathlib import Path
import tempfile

import pinyin
import Levenshtein
import numpy as np

from shprote.log import get_logger


logger = get_logger()

# Loading ignore characters. They're many enough
# Thus they'll be cached
ignored_characters = ""
purificator_tr = {}

ignore_cache_path = os.path.join(tempfile.gettempdir(), "cache")
Path(ignore_cache_path).mkdir(parents=True, exist_ok=True)
ignore_cache_path = os.path.join(ignore_cache_path, "ignored-chars.npy")

# region Load ignored characters
if not (os.path.exists(ignore_cache_path) and os.path.isfile(ignore_cache_path)):
    logger.info("No chached ignore characters.")
    ignored_characters = "".join([chr(i) for i in range(
        sys.maxunicode + 1) if category(chr(i)).startswith("P")])

    purificator_dict = dict.fromkeys(ignored_characters, " ")
    purificator_tr = str.maketrans(purificator_dict)

    logger.info(
        f"Writing cached ignore characters to '{ignore_cache_path}'...")
    np.save(ignore_cache_path, purificator_tr)
else:
    logger.info(
        f"Reading cached ignore characters from '{ignore_cache_path}'...")
    purificator_tr = np.load(ignore_cache_path, allow_pickle=True).item()
# endregion


def levenshtein_massify(str_in: str) -> str:
    # Replace all punctuation marks with spaces
    str_in = str_in.lower().translate(purificator_tr)
    str_in = re.sub(
        r"(\s[āàáǎaēéěèeōóǒòo])", r"'\1", str_in)  # Add ' before words starting with a, e and o
    str_in = re.sub(r"\s", "", str_in)  # Remove spaces
    return str_in


def er_sound_mod(str_in: str) -> str:
    return re.sub(r"儿(?!子)", "r", str_in)


def check_pronunciation(teacher_data, teacher_data_type: str,
                        student_data, student_data_type: str, lang_code: str) -> dict:
    lang_code = lang_code.lower().strip()

    if lang_code == "zh":
        teacher_text = ""
        student_text = ""

        if teacher_data_type == "text":
            # Control R-like sounds (儿)
            teacher_data = er_sound_mod(teacher_data)
            teacher_text = pinyin.get(
                teacher_data, format='diacritical', delimiter=" ")
            teacher_text = levenshtein_massify(teacher_text)

        if student_data_type == "text":
            student_data = er_sound_mod(student_data)
            student_text = pinyin.get(
                student_data, format='diacritical', delimiter=" ")
            student_text = levenshtein_massify(student_text)

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
    else:
        return {
            "type": "error",
            "name": "LANGCODE_ERR",
            "msg": f"The language with code \"{lang_code}\" cannot be processed or does not exist"
        }
