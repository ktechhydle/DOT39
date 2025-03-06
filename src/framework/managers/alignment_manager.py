from src._imports import *
from src.gui.dialogs import AlignmentCreatorDialog, GetAlignmentDialog
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

    def parent(self):
        return self._parent
