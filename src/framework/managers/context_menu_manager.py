from src._imports import *
from src.gui.widgets import ContextMenu
from src.framework.items.point_group import PointGroupItem
from src.framework.items.terrain_item import TerrainItem
from src.framework.items.alignment_item import AlignmentItem
from src.framework.items.editable_item import EditableItem


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
        if self.scene.activeSelection():
            selected_item = self.scene.activeSelection()

            if isinstance(selected_item, PointGroupItem):
                edit_points_action = QAction('Edit Points', menu)
                edit_points_action.triggered.connect(self.parent.pointManager.editPoints)
                to_surface_action = QAction('Convert Points to Surface', menu)
                to_surface_action.triggered.connect(self.parent.pointManager.convertGroupToSurface)

                menu.addAction(edit_points_action)
                menu.addAction(to_surface_action)

            elif isinstance(selected_item, TerrainItem):
                to_points_action = QAction('Convert Surface to Points', menu)
                to_points_action.triggered.connect(self.parent.surfaceManager.convertSurfaceToGroup)

                menu.addAction(to_points_action)

            elif isinstance(selected_item, AlignmentItem):
                edit_alignment_action = QAction('Edit Alignment', menu)
                edit_alignment_action.triggered.connect(self.parent.alignmentManager.editAlignment)

                menu.addAction(edit_alignment_action)

            elif isinstance(selected_item, EditableItem):
                edit_value_action = QAction('Edit Value', menu)
                edit_value_action.triggered.connect(selected_item.startEditing)

                menu.addAction(edit_value_action)

        select_all_action = QAction('Select All', menu)
        select_all_action.triggered.connect(self.scene.selectionTool().selectAll)
        unhide_all_action = QAction('Unhide All', menu)
        unhide_all_action.triggered.connect(self.scene.selectionTool().unhideAll)
        clear_selection_action = QAction('Clear Selection', menu)
        clear_selection_action.triggered.connect(self.scene.selectionTool().clearSelection)
        hide_selection_action = QAction('Hide Selection', menu)
        hide_selection_action.triggered.connect(self.scene.selectionTool().hideSelection)

        menu.addSeparator()
        menu.addAction(select_all_action)
        menu.addAction(unhide_all_action)
        menu.addSeparator()
        menu.addAction(clear_selection_action)
        menu.addAction(hide_selection_action)
