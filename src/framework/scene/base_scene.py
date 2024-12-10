import random

import moderngl
from src._imports import *
from src.framework.items.base_item import BaseItem
from src.framework.items.point_item import PointItem
from src.framework.items.terrain_item import TerrainItem
from src.framework.scene.functions import hexToRGB, vertex_shad, fragment_shad
from src.framework.scene.unit_manager import UnitManager


class BaseScene(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.CrossCursor)

        self.unit_manager = UnitManager()

        self.undo_stack = QUndoStack(self)
        self.undo_stack.setUndoLimit(200)

        self.ctx = None
        self.program = None
        self.wireframe = True

        self._items = []
        self._selected_items = []

    def initializeGL(self):
        r, g, b = hexToRGB('#000000')

        self.ctx = moderngl.create_context()
        self.ctx.clear(r, g, b)
        self.ctx.wireframe = self.wireframe

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
        item = TerrainItem(self, self.program, [(0.0, 0.0, 0.0),
                                                (10.0, 10.0, 0.0),
                                                (-10.0, -10.0, 0.0),
                                                (-10.0, 10.0, 0.0),
                                                (10.0, -10.0, 0.0),
                                                ])

        self.addItem(item)

        item = PointItem(self, self.program, [0, 0])

        self.addItem(item)

        for item in self.items():
            item.render()

    def addItem(self, item: BaseItem):
        if item not in self._items:
            self._items.append(item)

        if not item.isVisible():
            item.setVisible(True)

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
