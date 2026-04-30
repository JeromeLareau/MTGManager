# network/download_manager.py
from PySide6.QtCore import QObject, QThread, Signal
from workers.download_worker import DownloadWorker

class DownloadManager(QObject):
    request_download = Signal(str)

    image_downloaded = Signal(str, bytes)
    download_failed = Signal(str, str)

    def __init__(self):
        super().__init__()

        self.thread = QThread()
        self.worker = DownloadWorker()

        self.worker.moveToThread(self.thread)

        self.request_download.connect(self.worker.download)
        self.worker.finished.connect(self.image_downloaded)
        self.worker.failed.connect(self.download_failed)

        self.thread.start()

    def download(self, url: str):
        self.request_download.emit(url)

    def shutdown(self):
        self.thread.quit()
        self.thread.wait()