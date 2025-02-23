from src._imports import *
from src.framework.tools.base_tool import BaseTool
from src.framework.items.alignment_item import AlignmentItem
from src.framework.scene.undo_commands import AddItemCommand


class AlignmentTool(BaseTool):
    def __init__(self, scene):
        super().__init__(scene)

        self._alignment_item = None
        self._points = []
        self._add_item_command = None

    def mousePress(self, event: QMouseEvent):
        if self._alignment_item is None:
            self._alignment_item = AlignmentItem(self.scene(), self.scene().shaderProgram())

        if self._add_item_command is None:
            self._add_item_command = AddItemCommand(self._alignment_item, self.scene())
            self.scene().addUndoCommand(self._add_item_command)

        x, y = self.scene().mapMouseToViewport(event.x(), event.y())

        self._points.append([x, y])
        self.updatePath()

    def mouseRelease(self, event: QMouseEvent):
        self.updatePath()

    def updatePath(self):
        self._alignment_item.clearHorizontalPath()
        self._alignment_item.drawStart(self._points[0][0], self._points[0][1])

        for coords in self._points:
            self._alignment_item.drawLine(coords[0], coords[1])

        self.scene().update()

    def finish(self):
        self._alignment_item = None
        self._points = []
        self._add_item_command = None


