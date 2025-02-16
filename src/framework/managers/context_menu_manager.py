from src._imports import *
from src.gui.widgets import ContextMenu
from src.framework.items.point_group import PointGroupItem


class ContextMenuManager(object):
    def __init__(self, scene, parent):
        self.scene = scene
        self.parent = parent

    def showSceneMenu(self, event: QContextMenuEvent):
        menu = ContextMenu()
        menu.setAnimationEnabled(True)

        self.addSceneContextActions(menu)

        menu.exec(self.scene.mapToGlobal(event.pos()))

    def addSceneContextActions(self, menu: ContextMenu):
        if self.scene.selectedItems() and len(self.scene.selectedItems()) < 2:
            selected_item = self.scene.selectedItems()[0]

            if isinstance(selected_item, PointGroupItem):
                edit_points_action = QAction('Edit Points', menu)
                edit_points_action.triggered.connect(self.parent.pointManager.editPoints)
                to_surface_action = QAction('Convert Points to Surface', menu)
                to_surface_action.triggered.connect(self.parent.pointManager.convertGroupToSurface)

                menu.addAction(edit_points_action)
                menu.addAction(to_surface_action)

        select_all_action = QAction('Select All', menu)
        select_all_action.triggered.connect(self.scene.selectAll)
        clear_selection_action = QAction('Clear Selection', menu)
        clear_selection_action.triggered.connect(self.scene.clearSelection)

        menu.addSeparator()
        menu.addAction(select_all_action)
        menu.addAction(clear_selection_action)
