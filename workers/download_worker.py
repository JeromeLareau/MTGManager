import requests
from PySide6.QtCore import QObject, Signal, Slot

class DownloadWorker(QObject):
    finished = Signal(str, bytes)   # url, raw bytes
    failed = Signal(str, str)  # url, error message

    @Slot(str)
    def download(self, url: str):
        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            self.finished.emit(url, resp.content)
        except Exception as e:
            self.failed.emit(url, str(e))