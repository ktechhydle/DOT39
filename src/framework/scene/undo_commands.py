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
    def __init__(self, point_group, old_attr: list[dict], new_attr: list[dict]):
        super().__init__()

        self.point_group = point_group
        self.point_items = point_group.points()
        self.old_attr = old_attr
        self.new_attr = new_attr

    def redo(self):
        for point, new_attributes in zip(self.point_items, self.new_attr):
            point.setPointNumber(new_attributes['num'])
            point.setPos([new_attributes['east'], new_attributes['north'], new_attributes['elev']])
            point.setName(new_attributes['desc'])

        self.point_group.update()

    def undo(self):
        for point, old_attributes in zip(self.point_items, self.old_attr):
            point.setPointNumber(old_attributes['num'])
            point.setPos([old_attributes['east'], old_attributes['north'], old_attributes['elev']])
            point.setName(old_attributes['desc'])

        self.point_group.update()


class EditHorizontalAlignmentCommand(QUndoCommand):
    def __init__(self, alignment, old_path, old_calls, new_path, new_calls):
        super().__init__()

        self.alignment = alignment
        self.old_path = old_path
        self.old_calls = old_calls
        self.new_path = new_path
        self.new_calls = new_calls

    def redo(self):
        self.alignment.setHorizontalPath(self.new_path)
        self.alignment.setDrawCalls(self.new_calls)

    def undo(self):
        self.alignment.setHorizontalPath(self.old_path)
        self.alignment.setDrawCalls(self.old_calls)


class VisibilityChangedCommand(QUndoCommand):
    def __init__(self, items: list, new_attr: list[bool], old_attr: list[bool]):
        super().__init__()

        self.items = items
        self.new_attr = new_attr
        self.old_attr = old_attr

    def redo(self):
        for item, new_attribute in zip(self.items, self.new_attr):
            item.setVisible(new_attribute)

    def undo(self):
        for item, old_attribute in zip(self.items, self.old_attr):
            item.setVisible(old_attribute)



