import moderngl
from src._imports import *
from src.framework.items.base_item import BaseItem
from src.framework.items.point_item import PointItem
from src.framework.scene.functions import hexToRGB
from src.framework.scene.unit_manager import UnitManager


class BaseScene(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.unit_manager = UnitManager()

        self.undo_stack = QUndoStack(self)
        self.undo_stack.setUndoLimit(200)

        self.ctx = None
        self.axis_program = None
        self.axis_vbo = None

        self._items = []
        self._selected_items = []

    def initializeGL(self):
        r, g, b = hexToRGB('#000000')

        self.ctx = moderngl.create_context()
        self.ctx.clear(r, g, b)

    def resizeGL(self, w, h):
        width = max(2, w)
        height = max(2, h)
        self.ctx.viewport = (0, 0, width, height)

        self.update()

    def paintGL(self):
        self.drawTestItem()

    def mousePressEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):
        pass

    def drawTestItem(self):
        item = PointItem(self, [10.0, 10.0])

        self.addItem(item)

    def addItem(self, item: BaseItem):
        self._items.append(item)

        if not item.isVisible():
            item.setVisible(True)

        item.render()

    def removeItem(self, item: BaseItem):
        if item in self.items():
            item.setVisible(False)

            self.items().remove(item)

    def items(self):
        return self._items

    def selectedItems(self):
        return self._selected_items

    def itemAt(self, pos):
        pass
