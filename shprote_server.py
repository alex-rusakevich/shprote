#!/usr/bin/env python
import sys
import re
import os
import tempfile
from unicodedata import category

import pinyin
import Levenshtein
from flask import Flask, request, abort, make_response, jsonify, Response

from shprote.config import load_config


config = load_config()

# Loading ignore characters. They're many enough
# Thus they'll be cached
ignored_characters = ""
ignore_cache_path = os.path.join(tempfile.gettempdir(), "shprote-ignore.cache")
if not (os.path.exists(ignore_cache_path) and os.path.isfile(ignore_cache_path)):
    print("No chached ignore characters.")
    ignored_characters = "".join([chr(i) for i in range(
        sys.maxunicode + 1) if category(chr(i)).startswith("P")])

    print(f"Writing cached ignore characters to '{ignore_cache_path}'...")
    with open(ignore_cache_path, "w", encoding="utf8") as cache_file:
        cache_file.write(ignored_characters)
else:
    print(f"Reading cached ignore characters from '{ignore_cache_path}'...")
    with open(ignore_cache_path, "r", encoding="utf8") as cache_file:
        ignored_characters = cache_file.read()

purificator_dict = dict.fromkeys(ignored_characters, " ")
purificator_tr = str.maketrans(purificator_dict)
# ==============================================

app = Flask(__name__)


def gen_error(err_name: str, err_desc: str, err_code: int) -> dict:
    resp = make_response(jsonify({
        "error-name": err_name,
        "error-desc": err_desc
    }), err_code)
    return resp


def levenshtein_massify(str_in: str) -> str:
    # Replace all punctuation marks with spaces
    str_in = str_in.lower().translate(purificator_tr)
    str_in = re.sub(
        r"(\s[āàáǎaēéěèeōóǒòo])", r"'\1", str_in)  # Add ' before words starting with a, e and o
    str_in = re.sub(r"\s", "", str_in)  # Remove spaces
    return str_in


def er_sound_mod(str_in: str) -> str:
    return re.sub(r"儿(?!子)", "ɹ", str_in)


@app.route("/")
def check_server_working():
    resp = Response(f"The server is working", 200)
    return resp


@app.route("/api/check")
def check_pronunciation():
    request_json = request.get_json(force=True)

    teacher_data = request_json["teacher"]["data"]
    teacher_data_type = request_json["teacher"]["type"]
    student_data = request_json["student"]["data"]
    student_data_type = request_json["student"]["type"]
    lang_code = request_json["lang"].lower()

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
            abort(gen_error(
                "LEVENMASS_EMPTY_ERR", "Levenshtein mass cannot be empty. Please, check your request", 422))

        max_len = max(len(teacher_text), len(student_text))
        leven_dist = Levenshtein.distance(teacher_text, student_text)
        result_ratio = (max_len - leven_dist) / max_len
        result_ratio = round(result_ratio * 100, 2)

        return {
            "total-ratio": result_ratio,
            "phon-mistakes": leven_dist,
            "teacher-said": teacher_text,
            "student-said": student_text
        }
    else:
        abort(gen_error(
            "LANGCODE_ERR", f"The language with code \"{lang_code}\" cannot be processed or does not exist", 400))


if __name__ == "__main__":
    check_updated_files = False if "DISABLE_FLASK_RELOADER" in os.environ and os.environ[
        "DISABLE_FLASK_RELOADER"] else config["server"]["debug"]

    app.run(debug=config["server"]["debug"], port=config["server"]
            ["port"], host=config["server"]["host"], use_reloader=check_updated_files)
