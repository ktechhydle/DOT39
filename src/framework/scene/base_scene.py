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
        self.ctx.clear(*self.bg_color)
        self.ctx.enable(DEPTH_TEST)
        self.ctx.wireframe = self.wireframe

        self.program = self.ctx.program(
            vertex_shader=vertex_shad,
            fragment_shader=fragment_shad
        )

        # Console Info
        print('DOT39 Is Now Compiled')
        print('OpenGL Attributes Initialized')

    def resizeGL(self, w, h):
        width = max(2, w)
        height = max(2, h)
        self.ctx.viewport = (0, 0, width, height)

        self.program['aspectRatio'].value = width / max(1.0, height)

        # Console Info
        print(f'OpenGL Viewport Resized To: {width, height}')

    def paintGL(self):
        self.ctx.clear(*self.bg_color)
        self.ctx.enable(BLEND)
        self.ctx.enable(DEPTH_TEST | CULL_FACE)
        self.ctx.wireframe = self.wireframe

        if not hasattr(self, 'item'):
            self.item = PointItem(self, self.program, [5.0, 5.0, 5.0])
            self.addItem(self.item)

        for item in self.items():
            item.render()

        # Console Info
        print('\n')
        print('Repainting OpenGL Viewport')
        print('Current Color: ', self.program['color'].value)
        print('Current Alpha Value: ', self.program['alphaValue'].value)
        print('Current Zoom Amount: ', self.program['cameraZoom'].value)
        print('\n')

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
        if event.angleDelta().y() > 0:
            self.program['cameraZoom'].value = min(100.0, self.program['cameraZoom'].value + 0.1)  # Clamp max zoom
        else:
            self.program['cameraZoom'].value = max(0.1, self.program['cameraZoom'].value - 0.1)  # Clamp min zoom

        self.update()

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

        self.update()

    def setBackgroundColor(self, color: str):
        self.bg_color = hexToRGB(color)

        self.update()

    def isWireframe(self):
        return self.wireframe

    def setWireframe(self, enabled: bool):
        self.wireframe = enabled

        self.update()
