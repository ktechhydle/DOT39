from src._imports import *
from src.gui.widgets import ToolBarContainer, AnimatedLabel


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
