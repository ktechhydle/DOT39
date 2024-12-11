from src._imports import QUndoCommand


class AddItemCommand(QUndoCommand):
    def __init__(self, item, scene):
        super().__init__()

        self.item = item
        self.scene = scene

    def redo(self):
        self.scene.addItem(self.item)

    def undo(self):
        self.scene.removeItem(self.item)