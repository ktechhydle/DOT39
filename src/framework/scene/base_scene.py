import moderngl
from src._imports import *
from src.framework.items.base_item import BaseItem
from src.framework.items.point_item import PointItem
from src.framework.items.terrain_item import TerrainItem
from src.framework.scene.functions import hexToRGB, vertex_shad, fragment_shad
from src.framework.scene.unit_manager import UnitManager
from src.framework.scene.undo_commands import *


class BaseScene(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.CrossCursor)

        self.undo_stack = QUndoStack(self)
        self.undo_stack.setUndoLimit(200)

        self.ctx = None
        self.program = None
        self.wireframe = True
        self.bg_color = hexToRGB('#000000')

        self._items = []
        self._selected_items = []

    def initializeGL(self):
        self.ctx = moderngl.create_context()
        self.ctx.clear(self.bg_color[0], self.bg_color[1], self.bg_color[2])
        self.ctx.wireframe = self.wireframe

        self.program = self.ctx.program(
            vertex_shader=vertex_shad,
            fragment_shader=fragment_shad
        )

        self.ctx.finish()

    def resizeGL(self, w, h):
        width = max(2, w)
        height = max(2, h)
        self.ctx.viewport = (0, 0, width, height)

        self.program['aspectRatio'].value = self.width() / max(1.0, self.height())

        self.update()

    def paintGL(self):
        self.ctx.clear(self.bg_color[0], self.bg_color[1], self.bg_color[2])
        self.ctx.enable(DEPTH_TEST)

        item = TerrainItem(self, self.program, [(0.0, 0.0, 0.0),
                                                    (10.0, 10.0, 0.0),
                                                    (-10.0, -10.0, 0.0),
                                                    (-10.0, 10.0, 0.0),
                                                    (10.0, -10.0, 0.0),
                                                    ])

        if not hasattr(self, 'undo_cmd'):
            self.undo_cmd = AddItemCommand(item, self)
            self.addUndoCommand(self.undo_cmd)

        for item in self.items():
            item.render()

        # Console Info
        print('Current Color: ', self.program['color'].value)
        print('Current Alpha Value: ', self.program['alphaValue'].value)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            if event.modifiers() & Qt.Modifier.SHIFT:
                # Orbiting logic
                pass

            else:
                # Panning logic
                pass

    def mouseMoveEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):
        pass

    def wheelEvent(self, event):
        # Zooming logic
        pass

    def addItem(self, item: BaseItem):
        if item not in self._items:
            self._items.append(item)

        print('Item Added')

        self.update()

    def removeItem(self, item: BaseItem):
        self._items.remove(item)

        print('Item Removed')

        self.update()

    def items(self):
        return self._items

    def selectedItems(self):
        return self._selected_items

    def itemAt(self, pos):
        pass

    def undoStack(self) -> QUndoStack:
        return self.undo_stack

    def addUndoCommand(self, command: QUndoCommand):
        self.undo_stack.push(command)

        print(f'Undo Command: {command}')
