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
        self._graphics_scene.setSceneRect(QRectF(0, 0, alignment.horizontalPath().length(), 200))
        self.setScene(self._graphics_scene)

        self.createScene()

    def createScene(self):
        for i in range(self.alignment_item.horizontalPath().elementCount()):
            x, y = self.alignment_item.coordAt(i)

            if self.terrain_item.getElevationAt(x, y):
                z = self.terrain_item.getElevationAt(x, y)

                item = QGraphicsEllipseItem(QRectF(5, 5, -5, -5))
                item.setX(x)
                item.setY(z)
                self._graphics_scene.addItem(item)
