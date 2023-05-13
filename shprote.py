import sys
import os
import signal
from PyQt6 import QtWidgets, uic, QtGui
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtCore import QTimer
import subprocess
import os
from pathlib import Path
import requests

from shprote.config import load_config
from shprote import __version__ as __shprote_version__
from shprote.log import get_logger

logger = get_logger()


class UI(QMainWindow):
    config = {}

    def __init__(self):
        super().__init__()
        uic.loadUi("ui/shprote.ui", self)
        self.setWindowIcon(QtGui.QIcon('ui/favicon.ico'))
        self.setWindowTitle("shprote GUI v" + str(__shprote_version__))

        self.config = load_config()

        clear_button = self.clearButton
        clear_button.clicked.connect(self.clear_all)

        check_button = self.checkButton
        check_button.clicked.connect(self.start_check)

    def clear_all(self):
        self.studentTextEdit.setPlainText("")
        self.teacherTextEdit.setPlainText("")
        self.resultTextEdit.setPlainText("")

    def start_check(self):
        self.resultTextEdit.setPlainText("Checking. Please, wait...")
        adress = "http://" + self.config["server"]["host"] + ":" + \
            str(self.config["server"]["port"]) + "/api/check"
        check_result = requests.get(adress, json={
            "teacher": {
                "data": self.teacherTextEdit.toPlainText(),
                "type": "text"
            },
            "student": {
                "data": self.studentTextEdit.toPlainText(),
                "type": "text"
            },
            "lang": "zh"
        }).json()

        display_data = ""
        if check_result["type"] == "result":
            display_data = f"""
Total ratio: {check_result["total-ratio"]*100}%
Total mistakes: {check_result["phon-mistakes"]}

Teacher's levenseq: {check_result["teacher-said"]}
Student's levenseq: {check_result["student-said"]}
""".strip()
        elif check_result["type"] == "error":
            display_data = f"""
ERROR!
{check_result["error-desc"]} ({check_result["error-name"]})
""".strip()
        self.resultTextEdit.setPlainText(display_data)


def main():
    logger.info("UI started")
    os.environ["DISABLE_FLASK_RELOADER"] = "True"

    shprote_srv = subprocess.Popen([sys.executable, os.path.join(
        Path(__file__).parent, 'shprote_server.py')], shell=False)

    app = QtWidgets.QApplication(sys.argv)

    # Making the app exit on Ctrl-C
    signal.signal(signal.SIGINT, lambda *a: app.quit())
    timer = QTimer()
    timer.start(256)
    timer.timeout.connect(lambda: None)

    window = UI()
    window.show()
    ret = app.exec()

    os.environ.pop("DISABLE_FLASK_RELOADER")

    logger.info("UI has been closed. Terminating shprote server...")
    shprote_srv.kill()
    logger.info("Successfully terminated shprote server")

    sys.exit(ret)


if __name__ == "__main__":
    main()
