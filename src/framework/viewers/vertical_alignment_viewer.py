from src._imports import *
from src.framework.items.alignment_item import AlignmentItem
from src.framework.items.terrain_item import TerrainItem


class VerticalAlignmentViewer(QGraphicsView):
    def __init__(self, alignment: AlignmentItem, terrain: TerrainItem, tool_btn: QPushButton, parent):
        super().__init__(parent)

        self.alignment_item = alignment
        self.terrain_item = terrain
        self.tool_btn = tool_btn

        self._graphics_scene = QGraphicsScene()
        self._graphics_scene.setSceneRect(QRectF(0, 0, self.alignment_item.horizontalPath().length(), 500))
        self.setScene(self._graphics_scene)

        # Add methods for zooming
        self.zoomInFactor = 1.25
        self.zoomClamp = True
        self.zoom = 20
        self.zoomStep = 1
        self.zoomRange = [4, 50]

        self.createScene()

    def createScene(self):
        for i in range(self.alignment_item.horizontalPath().elementCount()):
            x, y = self.alignment_item.coordAt(i)

            if self.terrain_item.getElevationAt(x, y):
                z = self.terrain_item.getElevationAt(x, y)
                print(f'Z: {z}')

                item = QGraphicsEllipseItem(QRectF(1, 1, -1, -1))
                item.setPen(QPen(QColor('#00ff00'), 1))
                item.setX(x)
                item.setY(z)
                self._graphics_scene.addItem(item)

    def wheelEvent(self, event):
        # Calculate zoom Factor
        zoomOutFactor = 1 / self.zoomInFactor

        # Calculate zoom
        if event.angleDelta().y() > 0:
            zoomFactor = self.zoomInFactor
            self.zoom += self.zoomStep
        else:
            zoomFactor = zoomOutFactor
            self.zoom -= self.zoomStep

        # Deal with clamping!
        clamped = False
        if self.zoom < self.zoomRange[0]: self.zoom, clamped = self.zoomRange[0], True
        if self.zoom > self.zoomRange[1]: self.zoom, clamped = self.zoomRange[1], True

        if not clamped or self.zoomClamp is False:
            self.scale(zoomFactor, zoomFactor)

