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


class UI(QMainWindow):
    config = {}

    def __init__(self):
        super().__init__()
        uic.loadUi("ui/shprote.ui", self)
        self.setWindowIcon(QtGui.QIcon('ui/favicon.png'))

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
        display_data = "\n".join(
            f"{str(k)}: {str(v)}" for k, v in check_result.items())
        self.resultTextEdit.setPlainText(display_data)


if __name__ == "__main__":
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

    print("UI has been closed. Terminating shprote server...", end=" ")
    shprote_srv.kill()
    print("Success!")

    sys.exit(ret)
