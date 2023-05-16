import pytest
from shprote.main import check_pronunciation

test_data = (
    ("码", "妈", 0.5000, 1),
    ("你好，我叫萨沙", "你好，我叫米沙", 0.8750, 2),
    ("我们那儿有个王小三儿，在门口儿摆着一个小杂货摊儿", "我们那儿有个王小三儿，在门口儿白着一个小杂货摊儿", 0.9831, 1),
    ("画儿", "画", 0.7500, 1),
    ("儿子", "二字", 0.5000, 2)
)


def test_empty():
    response = check_pronunciation(
        "》》？【】！；\t\r    ", "text",
        "你好", "text",
        "zh"
    )

    assert response["type"] == "error"
    assert response["name"] == "LEVENMASS_EMPTY_ERR"


@pytest.mark.parametrize("teacher, student, exp_ratio, exp_mistakes", test_data)
def test_zh(teacher, student, exp_ratio, exp_mistakes):
    response = check_pronunciation(
        teacher, "text",
        student, "text",
        "zh"
    )

    resp_ratio = float(response["total-ratio"])
    resp_mistakes = int(response["phon-mistakes"])

    assert exp_ratio == resp_ratio
    assert exp_mistakes == resp_mistakes
