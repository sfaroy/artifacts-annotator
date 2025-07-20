# src/artifacts_annotator/views/annotation_scene.py
from PyQt5.QtWidgets import (
    QGraphicsScene, QGraphicsRectItem, QGraphicsPolygonItem, QGraphicsItem
)
from PyQt5.QtGui import QPen, QBrush, QPolygonF, QColor
from PyQt5.QtCore import Qt, QPointF, QRectF

class AnnotationScene(QGraphicsScene):
    """Scene supporting rectangle and polygon annotations with classified types."""
    def __init__(
        self,
        parent=None,
        type_colors: dict[str, str] = None,
        default_type: str = None
    ) -> None:
        super().__init__(parent)
        self.mode = 'pan'  # 'pan', 'rect', 'poly', 'select'
        self.temp_item = None
        self.start_point = QPointF()
        self.poly_points: list[QPointF] = []
        # List of annotation dicts: {'type':..., 'artifact_type':..., 'points':...}
        self.annotations: list[dict] = []
        # Mapping artifact_type → hex color
        self.type_colors = type_colors or {}
        # Current artifact type for new annotations
        self.current_artifact_type = default_type or next(iter(self.type_colors), None)

    def set_mode(self, mode: str) -> None:
        self.mode = mode
        if self.temp_item:
            self.removeItem(self.temp_item)
        self.temp_item = None
        self.poly_points.clear()
        if mode != 'select':
            for item in self.selectedItems():
                item.setSelected(False)

    def _pen_for(self, art_type: str) -> QPen:
        color = self.type_colors.get(art_type, '#ff0000')
        return QPen(QColor(color), 2)

    def _brush(self) -> QBrush:
        return QBrush(Qt.transparent)

    def mousePressEvent(self, event) -> None:
        pos = event.scenePos()
        if self.mode == 'rect':
            self.start_point = pos
            rect_item = QGraphicsRectItem(QRectF(pos, pos))
            rect_item.setPen(self._pen_for(self.current_artifact_type))
            rect_item.setBrush(self._brush())
            rect_item.setFlag(QGraphicsItem.ItemIsSelectable, True)
            self.addItem(rect_item)
            self.temp_item = rect_item

        elif self.mode == 'poly':
            if (event.button() == Qt.RightButton and
                    self.temp_item and len(self.poly_points) >= 3):
                # finish polygon
                ann = {
                    'type': 'poly',
                    'artifact_type': self.current_artifact_type,
                    'points': [[p.x(), p.y()] for p in self.poly_points]
                }
                self.annotations.append(ann)
                self.temp_item.setData(0, ann)
                self.temp_item = None
                self.poly_points.clear()

            elif event.button() == Qt.LeftButton:
                self.poly_points.append(pos)
                if self.temp_item is None:
                    poly_item = QGraphicsPolygonItem(QPolygonF(self.poly_points))
                    poly_item.setPen(self._pen_for(self.current_artifact_type))
                    poly_item.setBrush(self._brush())
                    poly_item.setFlag(QGraphicsItem.ItemIsSelectable, True)
                    self.addItem(poly_item)
                    self.temp_item = poly_item
                else:
                    self.temp_item.setPolygon(QPolygonF(self.poly_points))

        elif self.mode == 'select':
            super().mousePressEvent(event)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self.mode == 'rect' and self.temp_item:
            current = event.scenePos()
            rect = QRectF(self.start_point, current).normalized()
            self.temp_item.setRect(rect)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if self.mode == 'rect' and self.temp_item:
            rect = self.temp_item.rect()
            ann = {
                'type': 'rect',
                'artifact_type': self.current_artifact_type,
                'points': [
                    [rect.x(), rect.y()],
                    [rect.x() + rect.width(), rect.y() + rect.height()]
                ]
            }
            self.annotations.append(ann)
            self.temp_item.setData(0, ann)
            self.temp_item = None

        elif self.mode == 'select':
            super().mouseReleaseEvent(event)
        else:
            super().mouseReleaseEvent(event)

    def keyPressEvent(self, event) -> None:
        if event.key() == Qt.Key_Delete and self.mode == 'select':
            for item in list(self.selectedItems()):
                ann = item.data(0)
                if ann in self.annotations:
                    self.annotations.remove(ann)
                self.removeItem(item)
        elif event.key() == Qt.Key_Escape and self.mode == 'poly':
            if self.temp_item:
                self.removeItem(self.temp_item)
                self.temp_item = None
                self.poly_points.clear()
        else:
            super().keyPressEvent(event)

    def _draw_all(self) -> None:
        """Redraw all loaded annotations with their type-specific colors."""
        for ann in self.annotations:
            art_type = ann.get('artifact_type')
            if ann['type'] == 'rect':
                p0, p1 = ann['points']
                item = QGraphicsRectItem(QRectF(QPointF(*p0), QPointF(*p1)))
            else:
                poly = QPolygonF([QPointF(x, y) for x, y in ann['points']])
                item = QGraphicsPolygonItem(poly)

            # style based on the saved artifact_type
            item.setPen(self._pen_for(art_type))
            item.setBrush(self._brush())
            item.setFlag(QGraphicsItem.ItemIsSelectable, True)
            item.setData(0, ann)
            self.addItem(item)
