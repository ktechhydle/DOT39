from src._imports import *
from src.framework.scene.undo_commands import VisibilityChangedCommand
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

            self.clearSelection()
            item.setSelected(True)

        else:
            self.clearSelection()

    def mouseMove(self, event: QMouseEvent):
        # Item hover effect logic
        item = self.scene().itemAt(event.x(), event.y())

        if item:
            item.setHovered(True)
            self.scene().update()
        else:
            self.clearHover()

    def selectAll(self):
        self.clearSelection()

        for item in self.scene().visibleItems():
            item.setSelected(True)

    def unhideAll(self):
        items = []
        new_attr = []
        old_attr = []

        for item in self.scene().items():
            if item.isVisible():
                continue

            items.append(item)
            new_attr.append(True)
            old_attr.append(item.isVisible())

        if items:
            self.scene().addUndoCommand(VisibilityChangedCommand(items, new_attr, old_attr))

    def hideSelection(self):
        items = []
        new_attr = []
        old_attr = []

        for item in self.scene().selectedItems():
            if not item.isVisible():
                continue

            items.append(item)
            new_attr.append(False)
            old_attr.append(item.isVisible())

        if items:
            self.scene().addUndoCommand(VisibilityChangedCommand(items, new_attr, old_attr))

    def clearSelection(self):
        for item in self.scene().items():
            item.setSelected(False)

        self.scene().update()

    def clearHover(self):
        for item in self.scene().items():
            item.setHovered(False)
