import sys

from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import QApplication

from application.modelconnector import ModelConnector

from application.gui.loadingwindow import LoadingWindow
from application.gui.mainwindow import MainWindow
from application.utils.backgroundworker import BackgroundWorker

def on_done_loading():
    loading_window.close()
    main_window.show()

if __name__ == "__main__":
    app = QApplication([])
    model_connector = ModelConnector()

    loading_window = LoadingWindow('Loading models...')
    main_window = MainWindow(model_connector)
    background_worker = BackgroundWorker(model_connector.load_models)
    background_worker.signals.done.connect(on_done_loading)

    loading_window.show()
    QThreadPool.globalInstance().start(background_worker)
    sys.exit(app.exec_())