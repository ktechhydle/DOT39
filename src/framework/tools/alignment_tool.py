from src._imports import *
from src.framework.tools.base_tool import BaseTool
from src.framework.items.alignment_item import AlignmentItem


class AlignmentTool(BaseTool):
    def __init__(self, scene):
        super().__init__(scene)

        self._alignment_item = AlignmentItem(self.scene(), self.scene().shaderProgram())
        self._points = []

    def mousePress(self, event: QMouseEvent):
        pass

    def updatePath(self):
        self._alignment_item.clearHorizontalPath()
