import moderngl
from src._imports import *
from src.framework.items.base_item import BaseItem
from src.framework.items.point_item import PointItem
from src.framework.scene.functions import hexToRGB, vertex_shad, fragment_shad
from src.framework.scene.unit_manager import UnitManager


class BaseScene(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.unit_manager = UnitManager()

        self.undo_stack = QUndoStack(self)
        self.undo_stack.setUndoLimit(200)

        self.ctx = None
        self.program = None

        self.is_panning = False
        self.is_orbiting = False

        self._items = []
        self._selected_items = []

    def initializeGL(self):
        r, g, b = hexToRGB('#000000')

        self.ctx = moderngl.create_context()
        self.ctx.clear(r, g, b)

        self.program = self.ctx.program(
            vertex_shader=vertex_shad,
            fragment_shader=fragment_shad
        )

    def resizeGL(self, w, h):
        width = max(2, w)
        height = max(2, h)
        self.ctx.viewport = (0, 0, width, height)

        self.program['aspectRatio'].value = self.width() / max(1.0, self.height())

        self.update()

    def paintGL(self):
        self.drawTestItem()

        for item in self.items():
            item.render()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            if event.modifiers() == Qt.Modifier.SHIFT:
                self.is_orbiting = True

            else:
                self.is_panning = True

    def mouseMoveEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):
        self.is_panning = False
        self.is_orbiting = False

    def drawTestItem(self):
        item = PointItem(self, self.program, [10.0, 10.0])

        self.addItem(item)

    def addItem(self, item: BaseItem):
        if item not in self._items:
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
