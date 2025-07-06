# src/my_package_name/views/thumbnail_grid.py
from PyQt5.QtWidgets import QListWidget, QListWidgetItem
from PyQt5.QtCore import pyqtSignal, Qt, QSize
from PyQt5.QtGui import QIcon, QPixmap
from typing import List
from ..generators.thumbnail_loader import ThumbnailLoader

class ThumbnailGrid(QListWidget):
    """Grid of thumbnails; emits `thumbnail_clicked(path)`."""
    thumbnail_clicked = pyqtSignal(str)

    def __init__(self, paths: List[str]) -> None:
        super().__init__()
        self.setViewMode(QListWidget.IconMode)
        self.setIconSize(QSize(128, 128))
        self.setGridSize(QSize(150, 150))
        self.setResizeMode(QListWidget.Adjust)
        self.setFlow(QListWidget.LeftToRight)
        self.setWrapping(True)

        self.loader = ThumbnailLoader()
        self.loader.signals.loaded.connect(self._on_loaded)
        self.populate(paths)

    def populate(self, paths: List[str]) -> None:
        self.clear()
        for p in paths:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, p)
            placeholder = QPixmap(128, 128)
            placeholder.fill(Qt.blue)
            item.setIcon(QIcon(placeholder))
            self.addItem(item)
            self.loader.load(p)

    def _on_loaded(self, path: str, pixmap: QPixmap) -> None:
        if pixmap.isNull():
            return
        for i in range(self.count()):
            item = self.item(i)
            if item.data(Qt.UserRole) == path:
                item.setIcon(QIcon(pixmap))
                break

    def mousePressEvent(self, event) -> None:
        item = self.itemAt(event.pos())
        if item:
            self.thumbnail_clicked.emit(item.data(Qt.UserRole))
        super().mousePressEvent(event)
