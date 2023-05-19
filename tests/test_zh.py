import pytest
from shprote.logics.zh import compare_lang_text

test_data = (
    ("码", "妈", 0.5000, 1),
    ("你好，我叫萨沙", "你好，我叫米沙", 0.8750, 2),
    ("我们那儿有个王小三儿，在门口儿摆着一个小杂货摊儿", "我们那儿有个王小三儿，在门口儿白着一个小杂货摊儿", 0.9831, 1),
    ("画儿", "画", 0.7500, 1),
    ("儿子", "二字", 0.5000, 2),
    ("妈妈", "密码", 0.5000, 2),
    ("河里的鹅", "不渴不饿", 0.1250, 7),
    ("石室诗士施氏", "嗜狮, 誓食十狮", 0.6667, 6)
)


def test_empty():
    response = compare_lang_text(
        "》》？【】！；\t\r    ",
        "你好"
    )

    assert response["type"] == "error"
    assert response["name"] == "LEVENMASS_EMPTY_ERR"


@pytest.mark.parametrize("teacher, student, exp_ratio, exp_mistakes", test_data)
def test_zh(teacher, student, exp_ratio, exp_mistakes):
    response = compare_lang_text(
        teacher,
        student
    )

    resp_ratio = float(response["total-ratio"])
    resp_mistakes = int(response["phon-mistakes"])

    assert exp_ratio == resp_ratio
    assert exp_mistakes == resp_mistakes
