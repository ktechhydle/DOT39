from src._imports import *
from src.framework.items.base_item import BaseItem
from src.framework.items.point_item import PointItem
from src.framework.items.terrain_item import TerrainItem
from src.framework.scene.functions import hexToRGB, vertex_shad, fragment_shad
from src.framework.scene.unit_manager import UnitManager
from src.framework.scene.undo_commands import *

from pyrr import Matrix44


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
        self.aspect_ratio = 1.0
        self.camera_zoom = 2.0

        self._items = []
        self._selected_items = []

    def initializeGL(self):
        self.ctx = GL.create_context()
        self.ctx.clear(*self.bg_color)
        self.ctx.enable(GL.DEPTH_TEST)
        self.ctx.wireframe = self.wireframe

        self.program = self.ctx.program(
            vertex_shader=vertex_shad,
            fragment_shader=fragment_shad
        )

        self.view_matrix = self.program['matrix']

        # Console Info
        print('---- DOT39 Compiled Successfully ----\n---- OpenGL Attributes Initialized ----')
        print('OpenGL Version: ', self.ctx.version_code)

    def resizeGL(self, w, h):
        width = max(2, w)
        height = max(2, h)
        self.ctx.viewport = (0, 0, width, height)

        self.aspect_ratio = width / max(1.0, height)

        perspective = Matrix44.perspective_projection(1, self.aspect_ratio, 0.1, 1000.0)
        lookat = Matrix44.look_at(
            (0.0, 0.0, self.camera_zoom),
            (0.0, 0.0, 0.0),
            (0.0, 1.0, 0.0)
        )
        self.view_matrix.write((perspective * lookat).astype('f4'))

        # Console Info
        print(f'OpenGL Viewport Resized To: {width, height}')

    def paintGL(self):
        #self.ctx.clear(*self.bg_color)
        self.ctx.enable_only(GL.DEPTH_TEST | GL.BLEND | GL.CULL_FACE)

        self.aspect_ratio = self.width() / max(1.0, self.height())

        perspective = Matrix44.perspective_projection(60.0, self.aspect_ratio, 0.1, 1000.0)
        lookat = Matrix44.look_at(
            (0.0, 0.0, self.camera_zoom),
            (0.0, 0.0, 0.0),
            (0.0, 1.0, 0.0)
        )
        self.view_matrix.write((perspective * lookat).astype('f4'))

        for item in self.items():
            item.render()

        # Console Info
        print('---- Repainting OpenGL Viewport ----')
        print(f'Rendering {len(self.items())} Items')
        print('Current Color: ', self.program['color'].value)
        print('Current Alpha Value: ', self.program['alphaValue'].value)
        print('Current Zoom Amount: ', self.camera_zoom)
        print('Current Matrix: ', self.program['matrix'].value)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                # Orbiting logic
                self.setCursor(Qt.CursorShape.SizeAllCursor)

            else:
                # Panning logic
                self.setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):
        self.unsetCursor()

    def wheelEvent(self, event):
        self.camera_zoom += -event.angleDelta().y() * 0.001

        if self.camera_zoom < -0.1:
            self.camera_zoom = -0.1

        self.update()

    def unsetCursor(self):
        self.setCursor(Qt.CursorShape.CrossCursor)

    def addItem(self, item: BaseItem):
        if item not in self._items:
            self._items.append(item)

        print('Item Added')

        self.update()

    def removeItem(self, item: BaseItem):
        self._items.remove(item)

        print('Item Removed')

        self.update()

    def items(self) -> list[BaseItem]:
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

    def context(self) -> GL.Context:
        return self.ctx

    def shaderProgram(self) -> GL.Program:
        return self.program
