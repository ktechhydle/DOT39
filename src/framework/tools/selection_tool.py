from src._imports import *
from src.framework.tools.base_tool import BaseTool


class SelectionTool(BaseTool):
    def __init__(self, scene):
        super().__init__(scene)

    def mousePress(self, event: QMouseEvent):
        item = self.scene().itemAt(event.x(), event.y())

        if item:
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                item.setSelected(True)
                self.scene().update()
                return

            self.scene().clearSelection()
            item.setSelected(True)

        else:
            self.scene().clearSelection()

    def mouseMove(self, event: QMouseEvent):
        # Item hover effect logic
        item = self.scene().itemAt(event.x(), event.y())

        if item:
            item.setHovered(True)
            self.scene().update()
        else:
            self.scene().clearHover()
