import pytest
from shprote_server import app

test_data = (
    ("码", "妈", 50.00, 1),
    ("你好，我叫萨沙", "你好，我叫米沙", 87.50, 2),
    ("我们那儿有个王小三儿，在门口儿摆着一个小杂货摊儿", "我们那儿有个王小三儿，在门口儿白着一个小杂货摊儿", 98.31, 1),
    ("画儿", "画", 75.00, 1),
    ("儿子", "二字", 50.00, 2)
)


def test_root():
    respone = app.test_client().get()
    assert respone.status_code == 200
    assert "Shprote-Is-Working" in respone.headers
    assert bool(respone.headers["Shprote-Is-Working"])


def test_empty():
    respone = app.test_client().get("/api/check", json={
        "teacher": {
            "data": "》》？【】！；\t\r    ",
            "type": "text"
        },
        "student": {
            "data": "你好",
            "type": "text"
        },
        "lang": "zh"
    })
    assert respone.status_code == 422
    assert "Shprote-Error-Type" in respone.headers
    assert respone.headers["Shprote-Error-Type"] == "LEVENMASS_EMPTY_ERR"


@pytest.mark.parametrize("teacher, student, exp_ratio, exp_mistakes", test_data)
def test_zh(teacher, student, exp_ratio, exp_mistakes):
    response = app.test_client().get("/api/check", json={
        "teacher": {
            "data": teacher,
            "type": "text"
        },
        "student": {
            "data": student,
            "type": "text"
        },
        "lang": "zh"
    })

    resp_json = response.get_json(force=True)

    resp_ratio = float(resp_json["total-ratio"])
    resp_mistakes = int(resp_json["phon-mistakes"])

    assert exp_ratio == resp_ratio
    assert exp_mistakes == resp_mistakes
