from src._imports import *
from src.framework.items.terrain_item import TerrainItem
from src.gui.dialogs import (AlignmentCreatorDialog, VerticalAlignmentCreatorDialog, GetAlignmentDialog,
                             GetTerrainDialog, EditAlignmentDialog)
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
            dialog = EditAlignmentDialog(self.parent().glScene(), alignment, self.parent())
            dialog.exec()

    def autoGenerateAlignment(self):
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
            dialog = GetTerrainDialog(self.parent().glScene(), self.parent())
            dialog.exec()

            if dialog.activeResult():
                dialog = VerticalAlignmentCreatorDialog(self.parent().glScene(),
                                                        alignment,
                                                        dialog.activeResult(),
                                                        self.parent())
                dialog.exec()

    def parent(self):
        return self._parent
