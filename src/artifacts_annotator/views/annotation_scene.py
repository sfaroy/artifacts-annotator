# src/my_package_name/views/annotation_scene.py
from PyQt5.QtWidgets import (
    QGraphicsScene, QGraphicsRectItem, QGraphicsPolygonItem, QGraphicsItem
)
from PyQt5.QtGui import QPen, QBrush, QPolygonF
from PyQt5.QtCore import Qt, QPointF, QRectF

class AnnotationScene(QGraphicsScene):
    """
    Scene supporting rectangle, polygon annotation, selection, and deletion.
    """
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.mode = 'pan'         # 'pan', 'rect', 'poly', 'select'
        self.temp_item = None
        self.start_point = QPointF()
        self.poly_points = []     # List[QPointF]
        self.annotations = []     # List[dict]
        self.pen = QPen(Qt.red, 2)
        self.brush = QBrush(Qt.transparent)

    def set_mode(self, mode: str) -> None:
        self.mode = mode
        if self.temp_item:
            self.removeItem(self.temp_item)
            self.temp_item = None
        self.poly_points.clear()
        if mode != 'select':
            for item in self.selectedItems():
                item.setSelected(False)

    def mousePressEvent(self, event) -> None:
        pos = event.scenePos()
        if self.mode == 'rect':
            self.start_point = pos
            rect_item = QGraphicsRectItem(QRectF(pos, pos))
            rect_item.setPen(self.pen)
            rect_item.setBrush(self.brush)
            rect_item.setFlag(QGraphicsItem.ItemIsSelectable, True)
            self.addItem(rect_item)
            self.temp_item = rect_item

        elif self.mode == 'poly':
            if (event.button() == Qt.RightButton
                    and self.temp_item
                    and len(self.poly_points) >= 3):
                # finish polygon
                ann = {'type': 'poly',
                       'points': [[p.x(), p.y()] for p in self.poly_points]}
                self.annotations.append(ann)
                self.temp_item.setData(0, ann)
                self.temp_item = None
                self.poly_points.clear()

            elif event.button() == Qt.LeftButton:
                self.poly_points.append(pos)
                if self.temp_item is None:
                    poly_item = QGraphicsPolygonItem(QPolygonF(self.poly_points))
                    poly_item.setPen(self.pen)
                    poly_item.setBrush(self.brush)
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
                'points': [
                    [rect.x(), rect.y()],
                    [rect.x()+rect.width(), rect.y()+rect.height()]
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
        """Redraw all loaded annotations."""
        for ann in self.annotations:
            if ann['type'] == 'rect':
                p0, p1 = ann['points']
                rect = QRectF(QPointF(*p0), QPointF(*p1))
                item = QGraphicsRectItem(rect)
            else:
                poly = QPolygonF([QPointF(x,y) for x,y in ann['points']])
                item = QGraphicsPolygonItem(poly)
            item.setPen(self.pen)
            item.setBrush(self.brush)
            item.setFlag(QGraphicsItem.ItemIsSelectable, True)
            self.addItem(item)
