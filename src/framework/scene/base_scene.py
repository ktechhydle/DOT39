import moderngl
from src._imports import *
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
        self.ctx.viewport = (0, 0, w, h)

    def paintGL(self):
        self.drawGrid()

    def mousePressEvent(self, event):
        pass

    def mouseMoveEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):
        pass

    def drawGrid(self):
        pass

    def addItem(self):
        pass

    def items(self):
        pass

    def selectedItems(self):
        pass

    def itemAt(self, pos):
        pass
