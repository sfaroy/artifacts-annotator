# src/artifacts_annotator/views/image_viewer.py
import os
from typing import List
from PyQt5.QtWidgets import (
    QGraphicsView, QMainWindow, QShortcut, QToolBar,
    QAction, QActionGroup, QComboBox, QGraphicsItem
)
from PyQt5.QtGui import QPixmap, QKeySequence, QCursor
from PyQt5.QtCore import Qt, QRectF, pyqtSignal, QSettings, QByteArray
from ..controllers.annotation_manager import AnnotationManager
from .annotation_scene import AnnotationScene
from ..config import load_artifact_types

class ImageViewer(QGraphicsView):
    """Displays an image with zoom, pan, draw & select modes."""
    zoomChanged = pyqtSignal(int)
    modeChanged = pyqtSignal(str)
    positionChanged = pyqtSignal(int, int)

    ZOOM_LEVELS = [0.25, 0.5, 0.75, 1.0, 1.5, 2.0]

    def __init__(
        self,
        parent=None,
        type_colors: dict[str, str] = None,
        default_type: str = None
    ) -> None:
        super().__init__(parent)
        self.scene_obj = AnnotationScene(
            self, type_colors=type_colors, default_type=default_type
        )
        self.setScene(self.scene_obj)
        self._zoom_index = self.ZOOM_LEVELS.index(1.0)
        self.scale_factor = 1.0
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setMouseTracking(True)

    def load_image(self, path: str) -> QPixmap:
        """Load image at 100% and clear old items."""
        self.scene_obj.clear()
        pix = QPixmap(path)
        self.scene_obj.addPixmap(pix)
        self.setSceneRect(QRectF(pix.rect()))
        self.resetTransform()
        self._zoom_index = self.ZOOM_LEVELS.index(1.0)
        self.scale_factor = 1.0
        self.zoomChanged.emit(100)
        return pix

    def replace_image(self, path: str) -> QPixmap:
        """Swap in a new image, then redraw annotations."""
        self.scene_obj.clear()
        pix = QPixmap(path)
        self.scene_obj.addPixmap(pix)
        self.setSceneRect(QRectF(pix.rect()))
        self.scene_obj._draw_all()
        self.zoomChanged.emit(int(self.scale_factor * 100))
        return pix

    def wheelEvent(self, event) -> None:
        """Ctrl+wheel adjusts zoom; plain wheel pans or scrolls."""
        if event.modifiers() & Qt.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0 and self._zoom_index < len(self.ZOOM_LEVELS) - 1:
                self._zoom_index += 1
            elif delta < 0 and self._zoom_index > 0:
                self._zoom_index -= 1
            new_f = self.ZOOM_LEVELS[self._zoom_index]
            r = new_f / self.scale_factor
            self.scale(r, r)
            self.scale_factor = new_f
            self.zoomChanged.emit(int(new_f * 100))
        else:
            super().wheelEvent(event)

    def mouseMoveEvent(self, event) -> None:
        pos = self.mapToScene(event.pos())
        self.positionChanged.emit(int(pos.x()), int(pos.y()))
        super().mouseMoveEvent(event)

    def set_mode(self, mode: str) -> None:
        """Switch between pan, rect, poly, and select modes."""
        self.scene_obj.set_mode(mode)
        self.modeChanged.emit(mode)
        if mode == 'pan':
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.setCursor(QCursor(Qt.OpenHandCursor))
        elif mode == 'select':
            self.setDragMode(QGraphicsView.RubberBandDrag)
            self.setCursor(QCursor(Qt.ArrowCursor))
        else:
            self.setDragMode(QGraphicsView.NoDrag)
            self.setCursor(QCursor(Qt.CrossCursor))


class ImageViewerWindow(QMainWindow):
    """Window that holds ImageViewer and manages per-image annotations."""
    def __init__(self, files: List[str], index: int = 0) -> None:
        super().__init__()
        self.settings = QSettings('Roee','artifact-label-tool')
        geom = self.settings.value('viewerGeometry')
        self._restored = False
        if isinstance(geom, QByteArray):
            self.restoreGeometry(geom)
            self._restored = True

        self.type_colors = load_artifact_types()
        self.current_artifact_type = next(iter(self.type_colors))

        self.files = files
        self.index = index
        folder = os.path.dirname(files[0])
        self.ann_mgr = AnnotationManager(folder)

        self.viewer = ImageViewer(
            self,
            type_colors=self.type_colors,
            default_type=self.current_artifact_type
        )
        self.setCentralWidget(self.viewer)

        tb = QToolBar('Tools', self)
        self.addToolBar(tb)

        mode_grp = QActionGroup(self)
        mode_grp.setExclusive(True)
        self.mode_actions = {}
        for key, mode in [('D','pan'), ('R','rect'), ('P','poly'), ('E','select')]:
            act = QAction(f"{mode.title()} ({key})", self)
            act.setCheckable(True)
            act.setShortcut(key)
            act.toggled.connect(lambda chk, m=mode: chk and self.viewer.set_mode(m))
            mode_grp.addAction(act)
            tb.addAction(act)
            self.mode_actions[mode] = act
        self.mode_actions['pan'].setChecked(True)

        self.type_combo = QComboBox(self)
        self.type_combo.addItem('*')
        self.type_combo.model().item(0).setEnabled(False)
        for t in self.type_colors:
            self.type_combo.addItem(t)
        if self.type_combo.count() > 1:
            self.type_combo.setCurrentIndex(1)
        self.type_combo.currentTextChanged.connect(self._on_artifact_type_changed)
        tb.addWidget(self.type_combo)

        QShortcut(QKeySequence(Qt.Key_PageDown), self, activated=self.next_image)
        QShortcut(QKeySequence(Qt.Key_PageUp), self, activated=self.prev_image)
        QShortcut(QKeySequence("Ctrl+A"), self, activated=self._select_all)

        self.viewer.zoomChanged.connect(self._update_status)
        self.viewer.modeChanged.connect(self._update_status)
        self.viewer.positionChanged.connect(self._update_status)
        self.viewer.scene_obj.selectionChanged.connect(self._on_scene_selection_changed)

        self._load_current(initial=True)

    def _select_all(self) -> None:
        """Select all annotation items in the scene."""
        scene = self.viewer.scene_obj
        for item in scene.items():
            if item.flags() & QGraphicsItem.ItemIsSelectable:
                item.setSelected(True)
        self._on_scene_selection_changed()

    def _on_scene_selection_changed(self) -> None:
        """Update combo box based on current selection."""
        items = self.viewer.scene_obj.selectedItems()
        if not items:
            self.type_combo.blockSignals(True)
            self.type_combo.setCurrentText(self.current_artifact_type)
            self.type_combo.blockSignals(False)
            return
        types = [item.data(0)['artifact_type'] for item in items]
        unique = set(types)
        self.type_combo.blockSignals(True)
        if len(unique) == 1:
            self.type_combo.setCurrentText(next(iter(unique)))
        else:
            self.type_combo.setCurrentIndex(0)
        self.type_combo.blockSignals(False)

    def _on_artifact_type_changed(self, new_type: str) -> None:
        """
        Update the current artifact type for new annotations,
        apply to selected annotations.
        """
        if new_type == '*':
            return
        self.current_artifact_type = new_type
        self.viewer.scene_obj.current_artifact_type = new_type
        scene = self.viewer.scene_obj

        for item in self.viewer.scene_obj.selectedItems():
            # 1. Grab the copy from the item
            ann_copy = item.data(0)

            # 2. Find & update the *real* dict in scene.annotations
            for ann in scene.annotations:
                # match by identity or unique fields (points+type)
                if ann is ann_copy or ann == ann_copy:
                    ann['artifact_type'] = new_type
                    real_ann = ann
                    break
            else:
                # fallback: if not found, stick with the copy
                real_ann = ann_copy
                real_ann['artifact_type'] = new_type

            # 3. Push the updated dict back into the item
            item.setData(0, real_ann)

            # 4. Redraw with the new pen
            pen = self.viewer.scene_obj._pen_for(new_type)
            item.setPen(pen)

    def _update_status(self, *args) -> None:
        z = int(self.viewer.scale_factor * 100)
        m = self.viewer.scene_obj.mode
        if len(args) == 2:
            x, y = args
            msg = f"Mode: {m} | Zoom: {z}% | Pos: ({x},{y})"
        else:
            msg = f"Mode: {m} | Zoom: {z}%"
        self.statusBar().showMessage(msg)

    def _load_current(self, initial=False) -> None:
        path = self.files[self.index]
        self.setWindowTitle(path)
        self.viewer.scene_obj.clear()
        self.viewer.scene_obj.annotations.clear()
        if initial and not self._restored:
            pix = self.viewer.load_image(path)
            self.resize(pix.width(), pix.height())
        else:
            pix = self.viewer.replace_image(path)
        anns = self.ann_mgr.load(path)
        self.viewer.scene_obj.annotations = anns
        self.viewer.scene_obj._draw_all()
        center = QRectF(pix.rect()).center()
        self.viewer.centerOn(center)

    def _save_annotations(self) -> None:
        self.ann_mgr.save(self.files[self.index], self.viewer.scene_obj.annotations)

    def next_image(self) -> None:
        if self.index < len(self.files) - 1:
            self._save_annotations()
            self.index += 1
            self._load_current()

    def prev_image(self) -> None:
        if self.index > 0:
            self._save_annotations()
            self.index -= 1
            self._load_current()

    def update_images(self, files: List[str], index: int) -> None:
        self._save_annotations()
        self.files = files
        self.index = index
        self._load_current()

    def closeEvent(self, event) -> None:
        self._save_annotations()
        self.settings.setValue('viewerGeometry', self.saveGeometry())
        super().closeEvent(event)
