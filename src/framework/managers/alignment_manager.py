from src._imports import *
from src.framework.items.terrain_item import TerrainItem
from src.gui.dialogs import AlignmentCreatorDialog, VerticalAlignmentCreatorDialog, GetAlignmentDialog, GetTerrainDialog
from src.framework.scene.functions import isConvertibleToFloat
from src.framework.scene.undo_commands import *
from src.framework.items.alignment_item import AlignmentItem


class AlignmentManager:
    def __init__(self, parent):
        self._parent = parent

    def createAlignment(self):
        dialog = AlignmentCreatorDialog(self.parent().glScene(), self.parent())
        dialog.exec()

    def editAlignment(self):
        item = self.parent().glScene().activeSelection()
        alignment = None

        if item and isinstance(item, AlignmentItem):
            alignment = self.parent().glScene().activeSelection()

        else:
            dialog = GetAlignmentDialog(self.parent().glScene(), self.parent())
            dialog.exec()

            if dialog.activeResult():
                alignment = dialog.activeResult()

        if alignment:
            pass

    def createVerticalAlignment(self):
        item = self.parent().glScene().activeSelection()
        alignment = None

        if item and isinstance(item, AlignmentItem):
            alignment = self.parent().glScene().activeSelection()

        else:
            dialog = GetAlignmentDialog(self.parent().glScene(), self.parent())
            dialog.exec()

            if dialog.activeResult():
                alignment = dialog.activeResult()

        if alignment:
            item = self.parent().glScene().activeSelection()
            terrain = None

            if item and isinstance(item, TerrainItem):
                terrain = self.parent().glScene().activeSelection()

            else:
                dialog = GetTerrainDialog(self.parent().glScene(), self.parent())
                dialog.exec()

                if dialog.activeResult():
                    terrain = dialog.activeResult()

            if terrain:
                dialog = VerticalAlignmentCreatorDialog(self.parent().glScene(), alignment, terrain, self.parent())
                dialog.exec()


    def parent(self):
        return self._parent
