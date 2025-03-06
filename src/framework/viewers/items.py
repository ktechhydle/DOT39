from src._imports import *


class EllipsePointItem(QGraphicsEllipseItem):
    def __init__(self, color: str, bottom: bool = False, rect: QRectF = QRectF()):
        super().__init__(rect)
        self.setPen(QPen(QColor(color), 1))

        if bottom:
            self.setZValue(-10000)


class BoundingBoxItem(QGraphicsRectItem):
    def __init__(self, bottom: bool = False, rect: QRectF = QRectF()):
        super().__init__(rect)
        pen = QPen(QColor('#000000'), 1)
        pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        self.setPen(pen)

        if bottom:
            self.setZValue(-10000)
