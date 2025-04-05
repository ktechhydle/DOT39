from src._imports import *
from src.gui.widgets import ToolBarContainer, AnimatedLabel, ColorButton, ColorInput
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
        wireframe_btn.setChecked(True)
        wireframe_btn.clicked.connect(self.changeViewportType)
        solid_btn = QPushButton('Solid')
        solid_btn.setCheckable(True)
        solid_btn.clicked.connect(self.changeViewportType)
        self.view_type_btn_group = QButtonGroup(self)
        self.view_type_btn_group.addButton(wireframe_btn)
        self.view_type_btn_group.addButton(solid_btn)
        view_type_container = ToolBarContainer('View Mode', [wireframe_btn, solid_btn])
        view_type_container.layout().setContentsMargins(0, 0, 0, 10)

        scene_background_color_btn = ColorInput('Background Color:',
                                                QHBoxLayout(),
                                                on_change=self.scene.setBackgroundColor)

        self.layout().addWidget(view_type_container)
        self.layout().addWidget(scene_background_color_btn)
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
        self.setMinimumHeight(350)

        self.scene = scene

        self.createUI()
        self.createLayerList()

    def createUI(self):
        reset_btn = QPushButton('Reset')
        reset_btn.clicked.connect(self.resetLayers)

        self.list_widget = QListWidget(self)
        self.list_widget.setFixedHeight(325)
        self.list_widget.setSelectionMode(QListWidget.SelectionMode.NoSelection)

        self.layout().addWidget(reset_btn)
        self.layout().addWidget(self.list_widget)
        self.layout().addStretch()

    def createLayerList(self):
        items = [
            ('Point Group', '#ff0000', 0),
            ('Terrain', '#00ff00', 1),
            ('Alignment', '#ff0000', 2),
            ('Editable Value', '#cc6000', 3)
        ]

        for label, color, item_type in items:
            item = QListWidgetItem()
            item.item_type = item_type

            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)

            text_label = QLabel(label)
            color_button = ColorButton()
            color_button.setButtonColor(color)
            color_button.colorChanged.connect(self.updateItems)
            check_button = QCheckBox('Visible', self)
            check_button.setChecked(True)
            check_button.clicked.connect(self.updateItems)
            container.color = color_button.color
            container.checked = check_button.isChecked

            layout.addWidget(text_label)
            layout.addWidget(check_button)
            layout.addWidget(color_button)

            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, container)

        self.updateItems()

    def updateItems(self):
        item_type_map = {
            0: PointGroupItem,
            1: TerrainItem,
            2: AlignmentItem,
            3: EditableItem,
        }

        for i in range(self.list_widget.count()):
            list_item = self.list_widget.item(i)
            container = self.list_widget.itemWidget(list_item)

            if hasattr(list_item, 'item_type') and list_item.item_type in item_type_map:
                target_item_type = item_type_map[list_item.item_type]
                for item in self.scene.items():
                    if isinstance(item, target_item_type):
                        item.setVisible(container.checked())
                        item.setColor(hexToRGB(container.color()))

        self.scene.update()

    def resetLayers(self):
        self.list_widget.clear()

        items = [
            ('Point Group', '#ff0000', 0),
            ('Terrain', '#00ff00', 1),
            ('Alignment', '#ff0000', 2),
            ('Editable Value', '#cc6000', 3)
        ]

        for label, color, item_type in items:
            item = QListWidgetItem()
            item.item_type = item_type

            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)

            text_label = QLabel(label)
            color_button = ColorButton()
            color_button.setButtonColor(color)
            color_button.colorChanged.connect(self.updateItems)
            check_button = QCheckBox('Visible', self)
            check_button.setChecked(True)
            check_button.clicked.connect(self.updateItems)
            container.color = color_button.color
            container.checked = check_button.isChecked

            layout.addWidget(text_label)
            layout.addWidget(check_button)
            layout.addWidget(color_button)

            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, container)

        self.updateItems()
