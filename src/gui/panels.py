from src._imports import *
from src.gui.widgets import ToolBarContainer, AnimatedLabel, ColorButton
from src.framework.items.point_group import PointGroupItem
from src.framework.items.terrain_item import TerrainItem
from src.framework.items.alignment_item import AlignmentItem
from src.framework.items.editable_item import EditableItem
from src.framework.scene.functions import hexToRGB


class BasePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def createUI(self):
        pass


class HomePanel(BasePanel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(50, 20, 50, 20)

        self.createUI()

    def createUI(self):
        title_label = AnimatedLabel('<h1>Welcome to DOT39</h1>', self)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        new_file_label = QLabel('<h1>New File</h1>', self)
        recent_files_label = QLabel('<h1>Recent Files</h1>', self)

        self.layout().addWidget(title_label)
        self.layout().addSpacing(20)
        self.layout().addWidget(new_file_label)
        self.layout().addSpacing(20)
        self.layout().addWidget(recent_files_label)
        self.layout().addStretch()


class ScenePanel(BasePanel):
    def __init__(self, scene, parent=None):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        self.setMinimumHeight(200)

        self.scene = scene

        self.createUI()

    def createUI(self):
        wireframe_btn = QPushButton('Wireframe')
        wireframe_btn.setCheckable(True)
        wireframe_btn.clicked.connect(self.changeViewportType)
        solid_btn = QPushButton('Solid')
        solid_btn.setCheckable(True)
        solid_btn.clicked.connect(self.changeViewportType)
        self.view_type_btn_group = QButtonGroup(self)
        self.view_type_btn_group.addButton(wireframe_btn)
        self.view_type_btn_group.addButton(solid_btn)
        view_type_container = ToolBarContainer('View Mode', [wireframe_btn, solid_btn])

        self.layout().addWidget(view_type_container)
        self.layout().addStretch()

    def changeViewportType(self):
        if self.view_type_btn_group.buttons()[0].isChecked():
            self.scene.setWireframe(True)

        else:
            self.scene.setWireframe(False)


class LayersPanel(BasePanel):
    def __init__(self, scene, parent=None):
        super().__init__(parent)
        self.setLayout(QVBoxLayout())
        self.setMinimumHeight(300)

        self.scene = scene

        self.createUI()
        self.createLayerList()

    def createUI(self):
        reset_btn = QPushButton('Reset')
        reset_btn.clicked.connect(self.resetLayers)

        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        self.list_widget.itemChanged.connect(self.updateItems)

        self.layout().addWidget(reset_btn)
        self.layout().addWidget(self.list_widget)
        self.layout().addStretch()

    def createLayerList(self):
        point_item = QListWidgetItem('Point Group')
        point_item.setCheckState(Qt.CheckState.Checked)
        point_item.item_type = 0
        point_color_btn = ColorButton(self)
        point_color_btn.setButtonColor('#ff0000')
        point_color_btn.colorChanged.connect(self.updateItems)

        terrain_item = QListWidgetItem('Terrain')
        terrain_item.setCheckState(Qt.CheckState.Checked)
        terrain_item.item_type = 1
        terrain_color_btn = ColorButton(self)
        terrain_color_btn.setButtonColor('#00ff00')
        terrain_color_btn.colorChanged.connect(self.updateItems)

        alignment_item = QListWidgetItem('Alignment')
        alignment_item.setCheckState(Qt.CheckState.Checked)
        alignment_item.item_type = 2
        alignment_color_btn = ColorButton(self)
        alignment_color_btn.setButtonColor('#ff0000')
        alignment_color_btn.colorChanged.connect(self.updateItems)

        editable_item = QListWidgetItem('Editable Value')
        editable_item.setCheckState(Qt.CheckState.Checked)
        editable_item.item_type = 3
        editable_color_btn = ColorButton(self)
        editable_color_btn.setButtonColor('#cc6000')
        editable_color_btn.colorChanged.connect(self.updateItems)

        self.list_widget.addItem(point_item)
        self.list_widget.addItem(terrain_item)
        self.list_widget.addItem(alignment_item)
        self.list_widget.addItem(editable_item)
        self.list_widget.setItemWidget(point_item, point_color_btn)
        self.list_widget.setItemWidget(terrain_item, terrain_color_btn)
        self.list_widget.setItemWidget(alignment_item, alignment_color_btn)
        self.list_widget.setItemWidget(editable_item, editable_color_btn)

        self.updateItems()

    def updateItems(self):
        for i in range(self.list_widget.count()):
            list_item = self.list_widget.item(i)
            color_button = self.list_widget.itemWidget(list_item)

            if hasattr(list_item, 'item_type'):
                for item in self.scene.items():
                    if list_item.item_type == 0 and isinstance(item, PointGroupItem):
                        item.setVisible(True if list_item.checkState() else False)
                        item.setColor(hexToRGB(color_button.color()))
                    elif list_item.item_type == 1 and isinstance(item, TerrainItem):
                        item.setVisible(True if list_item.checkState() else False)
                        item.setColor(hexToRGB(color_button.color()))
                    elif list_item.item_type == 2 and isinstance(item, AlignmentItem):
                        item.setVisible(True if list_item.checkState() else False)
                        item.setColor(hexToRGB(color_button.color()))
                    elif list_item.item_type == 3 and isinstance(item, EditableItem):
                        item.setVisible(True if list_item.checkState() else False)
                        item.setColor(hexToRGB(color_button.color()))

    def resetLayers(self):
        self.list_widget.clear()

        point_item = QListWidgetItem('Point Group')
        point_item.setCheckState(Qt.CheckState.Checked)
        point_item.item_type = 0
        point_color_btn = ColorButton(self)
        point_color_btn.setButtonColor('#ff0000')
        point_color_btn.colorChanged.connect(self.updateItems)

        terrain_item = QListWidgetItem('Terrain')
        terrain_item.setCheckState(Qt.CheckState.Checked)
        terrain_item.item_type = 1
        terrain_color_btn = ColorButton(self)
        terrain_color_btn.setButtonColor('#00ff00')
        terrain_color_btn.colorChanged.connect(self.updateItems)

        alignment_item = QListWidgetItem('Alignment')
        alignment_item.setCheckState(Qt.CheckState.Checked)
        alignment_item.item_type = 2
        alignment_color_btn = ColorButton(self)
        alignment_color_btn.setButtonColor('#ff0000')
        alignment_color_btn.colorChanged.connect(self.updateItems)

        editable_item = QListWidgetItem('Editable Value')
        editable_item.setCheckState(Qt.CheckState.Checked)
        editable_item.item_type = 3
        editable_color_btn = ColorButton(self)
        editable_color_btn.setButtonColor('#cc6000')
        editable_color_btn.colorChanged.connect(self.updateItems)

        self.list_widget.addItem(point_item)
        self.list_widget.addItem(terrain_item)
        self.list_widget.addItem(alignment_item)
        self.list_widget.addItem(editable_item)
        self.list_widget.setItemWidget(point_item, point_color_btn)
        self.list_widget.setItemWidget(terrain_item, terrain_color_btn)
        self.list_widget.setItemWidget(alignment_item, alignment_color_btn)
        self.list_widget.setItemWidget(editable_item, editable_color_btn)

        self.updateItems()
