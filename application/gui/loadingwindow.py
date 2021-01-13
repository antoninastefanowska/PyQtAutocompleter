from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QLabel

class LoadingWindow(QMainWindow):
    def __init__(self, message):
        super().__init__()
        self.message = message
        self.load_ui()

    def load_ui(self):
        uic.loadUi("resources/ui/loadingwindow.ui", self)
        status_label = self.findChild(QLabel, 'statusLabel')
        status_label.setText(self.message)