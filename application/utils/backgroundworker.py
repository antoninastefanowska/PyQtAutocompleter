from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject, QRunnable

class BackgroundWorker(QRunnable):
    def __init__(self, handler):
        super().__init__()
        self.signals = BackgroundWorker.BackgroundSignals()
        self.handler = handler

    @pyqtSlot()
    def run(self):
        self.handler()
        self.signals.done.emit()

    class BackgroundSignals(QObject):
        done = pyqtSignal()