from src._imports import *
from src.gui.dialogs import AlignmentCreatorDialog
from src.framework.scene.functions import isConvertibleToFloat
from src.framework.scene.undo_commands import *


class AlignmentManager:
    def __init__(self, parent):
        self._parent = parent

    def createAlignment(self):
        dialog = AlignmentCreatorDialog(self.parent().glScene(), self.parent())
        dialog.exec()

    def parent(self):
        return self._parent
