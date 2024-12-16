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


class PointsToSurfaceCommand(QUndoCommand):
    def __init__(self, point_group_item, surface_item, scene):
        super().__init__()

        self.point_group_item = point_group_item
        self.surface_item = surface_item
        self.scene = scene

    def redo(self):
        self.scene.removeItem(self.point_group_item)
        self.scene.addItem(self.surface_item)

    def undo(self):
        self.scene.addItem(self.point_group_item)
        self.scene.removeItem(self.surface_item)


class EditPointsCommand(QUndoCommand):
    def __init__(self, point_items: list, old_attr, new_attr):
        super().__init__()

        self.point_items = point_items
        self.old_attr = old_attr
        self.new_attr = new_attr

    def redo(self):
        pass

    def undo(self):
        pass


