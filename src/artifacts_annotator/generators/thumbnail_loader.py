# src/my_package_name/generators/thumbnail_loader.py
import io
from PIL import Image
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QRunnable, QThreadPool, pyqtSignal, QObject

class ThumbnailSignal(QObject):
    loaded = pyqtSignal(str, QPixmap)

class ThumbnailLoader:
    """Asynchronously generate 128×128 thumbnails."""
    def __init__(self) -> None:
        self.pool = QThreadPool()
        self.signals = ThumbnailSignal()

    def load(self, path: str, size: int = 128) -> None:
        task = _ThumbnailTask(path, size, self.signals.loaded)
        self.pool.start(task)

class _ThumbnailTask(QRunnable):
    def __init__(self, path: str, size: int, signal: pyqtSignal) -> None:
        super().__init__()
        self.path = path
        self.size = size
        self.signal = signal

    def run(self) -> None:
        img = Image.open(self.path)
        img.thumbnail((self.size, self.size), resample=Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        pixmap = QPixmap()
        pixmap.loadFromData(buf.getvalue())
        self.signal.emit(self.path, pixmap)
