import sys
import os
import signal
from PyQt6 import QtWidgets, uic, QtGui
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QFileDialog
from PyQt6.QtCore import QTimer, QCoreApplication
import subprocess
import os
import requests
import webbrowser
import datetime
from pathlib import Path

from shprote.config import load_config, get_script_dir, DATA_DIR
from shprote import __version__ as __shprote_version__
from shprote import __adress__
from shprote.log import get_logger

logger = get_logger()
scriptdir = get_script_dir()


class UI(QMainWindow):
    config = {}

    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join(scriptdir, "ui", "shprote.ui"), self)
        self.setWindowIcon(QtGui.QIcon(
            os.path.join(scriptdir, 'ui', 'favicon.ico')))
        self.setWindowTitle("shprote GUI " + str(__shprote_version__))

        self.config = load_config()

        clear_button = self.clearButton
        clear_button.clicked.connect(self.clear_all)

        check_button = self.checkButton
        check_button.clicked.connect(self.start_check)

        help_menu_b = self.actionShprote_repo
        help_menu_b.triggered.connect(self.open_github)

        quit_menu_b = self.actionExit
        quit_menu_b.triggered.connect(QCoreApplication.quit)

        save_text_b = self.actionSave_the_result_as
        save_text_b.triggered.connect(self.save_result)

    def save_result(self):
        result_txt = self.resultTextEdit.toPlainText().strip()

        if result_txt == "":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setText("There is no result to save")
            msg.setWindowTitle("Error")
            msg.exec()
            return

        # Creating standart dir for results
        RESULTS_DIR = os.path.join(DATA_DIR, "results")
        Path(RESULTS_DIR).mkdir(parents=True, exist_ok=True)

        result_save_path, _ = QFileDialog.getSaveFileName(self, "Save As...", RESULTS_DIR, filter="""
            Text files (*.txt);;
            All files (*.*)
        """)

        with open(result_save_path, 'w', encoding='utf8') as result_file:
            result_file.write(
                "[" + str(datetime.datetime.utcnow()) + "]" + "\n\n")
            result_file.write(
                "Teacher said: " + self.teacherTextEdit.toPlainText().strip() + "\n\n")
            result_file.write(
                "Student said: " + self.studentTextEdit.toPlainText().strip() + "\n\n")
            result_file.write(result_txt + "\n")

    def clear_all(self):
        self.studentTextEdit.setPlainText("")
        self.teacherTextEdit.setPlainText("")
        self.resultTextEdit.setPlainText("")

    def start_check(self):
        logger.info("Started processing the input data")

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
        logger.info(f"Displaying the result:\n{display_data}")
        self.resultTextEdit.setPlainText(display_data)

    def open_github(self):
        webbrowser.open_new_tab(__adress__)


def main():
    logger.info("UI program started")
    os.environ["DISABLE_FLASK_RELOADER"] = "True"

    shprote_srv = subprocess.Popen([sys.executable, os.path.join(
        get_script_dir(), 'shprote_server.py')], stdout=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)

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

    sys.exit(ret)


if __name__ == "__main__":
    main()
