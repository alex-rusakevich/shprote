import sys
import signal
from PyQt6 import QtWidgets, uic, QtGui
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtCore import QTimer
import subprocess
import os
from pathlib import Path


class UI(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/shprote.ui", self)
        self.setWindowIcon(QtGui.QIcon('ui/favicon.png'))

        clear_button = self.clearButton
        clear_button.clicked.connect(self.clear_all)

    def clear_all(self):
        self.studentTextEdit.setPlainText("")
        self.teacherTextEdit.setPlainText("")
        self.resultTextEdit.setPlainText("")


if __name__ == "__main__":
    shprote_srv = subprocess.Popen([sys.executable, os.path.join(
        Path(__file__).parent, 'shprote_server.py')], shell=False)

    app = QtWidgets.QApplication(sys.argv)

    # Making the app exit on Ctrl-C
    signal.signal(signal.SIGINT, lambda *a: app.quit())
    timer = QTimer()
    timer.start(512)
    timer.timeout.connect(lambda: None)

    window = UI()
    window.show()
    ret = app.exec()

    print("UI has been closed. Terminating shprote server...", end=" ")
    shprote_srv.kill()
    print("Success!")

    sys.exit(ret)
