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
        self.ctx = GL.create_context()
        self.ctx.clear(*self.bg_color)
        self.ctx.enable(GL.DEPTH_TEST)
        self.ctx.wireframe = self.wireframe

        self.program = self.ctx.program(
            vertex_shader=vertex_shad,
            fragment_shader=fragment_shad
        )

        self.view_matrix = QMatrix4x4()
        self.view_matrix.perspective(
            0,  # Angle
            self.width() / self.height(),  # Aspect Ratio
            0.1,   # Near clipping plane
            100.0  # Far clipping plane
        )

        # Console Info
        print('---- DOT39 Compiled Successfully ----\n---- OpenGL Attributes Initialized ----')
        print('OpenGL Version: ', self.ctx.version_code)

    def resizeGL(self, w, h):
        width = max(2, w)
        height = max(2, h)
        self.ctx.viewport = (0, 0, width, height)

        self.program['aspectRatio'].value = width / max(1.0, height)

        self.view_matrix.perspective(
            0,  # Angle
            width / max(1.0, height),  # Aspect Ratio
            0.1,  # Near clipping plane
            100.0  # Far clipping plane
        )

        # Console Info
        print(f'OpenGL Viewport Resized To: {width, height}')

    def paintGL(self):
        #self.ctx.clear(*self.bg_color)
        self.ctx.enable_only(GL.DEPTH_TEST | GL.BLEND | GL.CULL_FACE)
        self.program['matrix'].value = self.view_matrix.data()

        self.drawTestObject()

        # Console Info
        print('---- Repainting OpenGL Viewport ----')
        print('Current Color: ', self.program['color'].value)
        print('Current Alpha Value: ', self.program['alphaValue'].value)
        print('Current Zoom Amount: ', self.program['cameraZoom'].value)
        print('Current Matrix: ', self.program['matrix'].value)

    def drawTestObject(self):
        self.program['color'].value = hexToRGB('#ff0000')

        vertices = np.array([
            # Horizontal line
            -0.01, 0.0, 0.0,
            0.01, 0.0, 0.0,
            # Vertical line
            0.0, -0.01, 0.0,
            0.0, 0.01, 0.0,
        ], dtype='f4').tobytes()

        vbo = self.ctx.buffer(vertices)

        vao = self.ctx.vertex_array(self.program, vbo, 'in_vert')
        vao.render(GL.POINTS)

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
            self.program['cameraZoom'].value = min(100.0, self.program['cameraZoom'].value + 0.5)  # Clamp max zoom
        else:
            self.program['cameraZoom'].value = max(0.1, self.program['cameraZoom'].value - 0.5)  # Clamp min zoom

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
