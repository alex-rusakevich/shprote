#!/usr/bin/env python
import sys
import re
import os
import tempfile
from unicodedata import category

import pinyin
import Levenshtein
from flask import Flask, request, abort, Response

from shprote.config import load_config


config = load_config()

# Loading ignore characters. They're many enough
# Thus they'll be cached
ignored_characters = ""
ignore_cache_path = os.path.join(tempfile.gettempdir(), "shprote-ignore.cache")
if not (os.path.exists(ignore_cache_path) and os.path.isfile(ignore_cache_path)):
    ignored_characters = "".join([chr(i) for i in range(
        sys.maxunicode + 1) if category(chr(i)).startswith("P")])
    with open(ignore_cache_path, "w", encoding="utf8") as cache_file:
        cache_file.write(ignored_characters)
else:
    with open(ignore_cache_path, "r", encoding="utf8") as cache_file:
        ignored_characters = cache_file.read()

purificator_dict = dict.fromkeys(ignored_characters, " ")
purificator_tr = str.maketrans(purificator_dict)
# ==============================================

app = Flask(__name__)


def gen_error(err_name: str, err_text: str, err_code: int) -> Response:
    resp = Response(f"{err_name}: {err_text}", err_code)
    resp.headers["Shprote-Error-Type"] = err_name
    return resp


def levenshtein_massify(str_in: str) -> str:
    # Replace all punctuation marks with spaces
    str_in = str_in.lower().translate(purificator_tr)
    str_in = re.sub(
        r"(\s[āàáǎaēéěèeōóǒòo])", r"'\1", str_in)  # Add ' before words starting with a, e and o
    str_in = re.sub(r"\s", "", str_in)  # Remove spaces
    return str_in


@app.route("/")
def check_server_working():
    resp = Response(f"The server is working", 200)
    resp.headers["Shprote-Is-Working"] = True
    return resp


@app.route("/api/check")
def check_pronunciation():
    teacher_data = request.args.get("teacher")
    teacher_data_type = request.args.get("teacher-type")
    student_data = request.args.get("student")
    student_data_type = request.args.get("student-type")
    lang_code = request.args.get("lang").lower()

    if lang_code == "zh":
        teacher_text = ""
        student_text = ""

        if teacher_data_type == "text":
            teacher_text = pinyin.get(
                teacher_data, format='diacritical', delimiter=" ")
            teacher_text = levenshtein_massify(teacher_text)

        if student_data_type == "text":
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

        resp = Response(
            f"Total: {result_ratio}%, {leven_dist} mistake(s)", 200)
        resp.headers["Shprote-Result-Total-Ratio"] = result_ratio
        resp.headers["Shprote-Result-Total-Mistakes"] = leven_dist
        return resp
    else:
        abort(gen_error(
            "LANGCODE_ERR", f"The language with code \"{lang_code}\" cannot be processed or does not exist", 400))


if __name__ == "__main__":
    app.run(debug=config["server"]["debug"], port=config["server"]
            ["port"], host=config["server"]["host"])
