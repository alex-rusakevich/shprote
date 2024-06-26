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

import os

import pytest

from shprote.logics import Language
from shprote.logics.voice import audio_file_to_text
from shprote.logics.zh import compare_lang_text, text_to_levenseq

test_data = (
    ("码", "妈", 0.5000, 1),
    ("你好，我叫萨沙", "你好，我叫米沙", 0.8750, 2),
    (
        "我们那儿有个王小三儿，在门口儿摆着一个小杂货摊儿",
        "我们那儿有个王小三儿，在门口儿白着一个小杂货摊儿",
        0.9828,
        1,
    ),
    ("画儿", "画", 0.7500, 1),
    ("儿子", "二字", 0.5000, 2),
    ("妈妈", "密码", 0.5000, 2),
    ("河里的鹅", "不渴不饿", 0.1250, 7),
    ("石室诗士施氏", "嗜狮, 誓食十狮", 0.6667, 6),
)

test_levenmass = (
    # Test latin will remain the same
    ("Hello from Belarus!", "hellofrombelarus"),
    ("érzizàinǎrhuàhuàr", "érzizàinǎrhuàhuàr"),
    ("马马虎虎", "mǎmǎhūhū"),
    ("花儿", "huār"),
    ("南岸", "nán'àn"),
    ("儿子在哪儿画画儿？", "érzizàinǎrhuàhuàr"),
    ("句子", "jùzi"),
    (
        """521521521521，，，，【【【】】】{{{{{{{}}}}}}}
        520520520520""",
        "521521521521520520520520",
    ),
)

test_audio_levenmass = (
    ("zh_1.ogg", "wǒzhùzàimíngsīkè"),
    ("zh_2.ogg", "běijīngshìzhōngguódeshǒudū"),
    ("zh_3.ogg", "wǒnǚpéngyoushìzuìměilìde"),
)


@pytest.mark.parametrize("teacher, student, exp_ratio, exp_mistakes", test_data)
def test_zh(teacher, student, exp_ratio, exp_mistakes):
    response = compare_lang_text(teacher, student)

    resp_ratio = float(response["total-ratio"])
    resp_mistakes = int(response["phon-mistakes"])

    assert exp_ratio == resp_ratio
    assert exp_mistakes == resp_mistakes


@pytest.mark.parametrize("word_given, pinyin_expected", test_levenmass)
def test_levenmass(word_given, pinyin_expected):
    pinyin_given = text_to_levenseq(word_given)
    assert pinyin_given == pinyin_expected


@pytest.mark.parametrize("audio_file_path, pinyin_expected", test_audio_levenmass)
def test_audio(audio_file_path, pinyin_expected):
    txt = audio_file_to_text(
        os.path.join(".", "tests", "audio", audio_file_path), lang=Language.Chinese
    )
    pinyin = text_to_levenseq(txt)
    assert pinyin == pinyin_expected


def test_empty():
    response = compare_lang_text("》》？【】！；\t\r    ", "你好")

    assert response["type"] == "error"
    assert response["name"] == "LEVENMASS_EMPTY_ERR"
