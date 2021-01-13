from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QPushButton, QFileDialog
from PyQt5.QtGui import QTextCursor
from PyQt5.QtCore import pyqtSlot, Qt, QThreadPool

from application.gui.loadingwindow import LoadingWindow
from application.utils.backgroundworker import BackgroundWorker

class MainWindow(QMainWindow):
    def __init__(self, model_connector):
        super().__init__()
        self.model_connector = model_connector
        self.predicted = None

        self.text_area = None
        self.buttons = []
        self.buttons_visible = False
        self.loading_window = None
        self.background_worker = None

        self.load_ui()

    def load_ui(self):
        uic.loadUi("resources/ui/mainwindow.ui", self)

        self.text_area = self.findChild(QTextEdit, "textArea")
        self.buttons.append(self.findChild(QPushButton, "button1"))
        self.buttons.append(self.findChild(QPushButton, "button2"))
        self.buttons.append(self.findChild(QPushButton, "button3"))
        self.buttons.append(self.findChild(QPushButton, "button4"))
        self.buttons.append(self.findChild(QPushButton, "button5"))

        for button in self.buttons:
            policy = button.sizePolicy()
            policy.setRetainSizeWhenHidden(True)
            button.setSizePolicy(policy)

        self.hide_buttons()

    @pyqtSlot()
    def text_area_changed(self):
        text = self.text_area.toPlainText()
        word_count = len(text.rsplit(' ', 2)) - 1
        if word_count == 0:
            if self.buttons_visible:
                self.hide_buttons()
        else:
            if not self.buttons_visible:
                self.show_buttons()
            if text[-1] == ' ':
                tokens = self.model_connector.tokenize(text)
                if word_count >= 2:
                    self.background_worker = BackgroundWorker(lambda: self.model_connector.learn(tokens[-1]))
                    QThreadPool.globalInstance().start(self.background_worker)

                self.predicted = self.model_connector.predict_words(tokens)
                for i, predicted_word in enumerate(self.predicted):
                    self.buttons[i].setText("F" + str(i + 1) + ": " + predicted_word)

    def hide_buttons(self):
        for button in self.buttons:
            button.hide()
        self.buttons_visible = False

    def show_buttons(self):
        for button in self.buttons:
            button.show()
        self.buttons_visible = True

    def choose_word(self, index):
        chosen_word = self.predicted[index]
        text = self.text_area.toPlainText()
        if text[-1] != ' ':
            text = text.rsplit(' ', 1)[0]
            text += ' '
        text += chosen_word
        self.text_area.setText(text)
        self.text_area.moveCursor(QTextCursor.End)
        self.text_area.setFocus()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F1:
            self.choose_word(0)
        elif event.key() == Qt.Key_F2:
            self.choose_word(1)
        elif event.key() == Qt.Key_F3:
            self.choose_word(2)
        elif event.key() == Qt.Key_F4:
            self.choose_word(3)
        elif event.key() == Qt.Key_F5:
            self.choose_word(4)

    @pyqtSlot()
    def new_file(self):
        self.text_area.clear()

    @pyqtSlot()
    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, 'Otwórz...', '', 'Wszystkie pliki (*);;Pliki tekstowe (*.txt)', options=QFileDialog.Options())
        if filename:
            file = open(filename, 'r')
            self.text_area.setText(file.read())
            file.close()

    @pyqtSlot()
    def save_file(self):
        filename, _ = QFileDialog.getSaveFileName(self, 'Zapisz jako...', '', 'Wszystkie pliki (*);;Pliki tekstowe (*.txt)', options=QFileDialog.Options())
        if filename:
            file = open(filename, 'w')
            file.write(self.text_area.toPlainText())
            file.close()

    @pyqtSlot()
    def button1_clicked(self):
        self.choose_word(0)

    @pyqtSlot()
    def button2_clicked(self):
        self.choose_word(1)

    @pyqtSlot()
    def button3_clicked(self):
        self.choose_word(2)

    @pyqtSlot()
    def button4_clicked(self):
        self.choose_word(3)

    @pyqtSlot()
    def button5_clicked(self):
        self.choose_word(4)

    def on_model_saved(self, close):
        self.loading_window.close()
        close()

    def closeEvent(self, event):
        self.hide()
        self.loading_window = LoadingWindow('Saving model...')
        self.background_worker = BackgroundWorker(self.model_connector.save_model)
        self.background_worker.signals.done.connect(lambda: self.on_model_saved(event.accept))
        self.loading_window.show()
        QThreadPool.globalInstance().start(self.background_worker)