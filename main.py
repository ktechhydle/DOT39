from src.gui.widgets import *
from src.framework.scene.base_scene import BaseScene
from src.framework.managers.unit_manager import UnitManager
from src.framework.managers.point_manager import PointManager
from src.framework.managers.surface_manager import SurfaceManager


class DOT39(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('DOT39')
        self.setWindowIcon(QIcon('resources/icons/logos/dot39_logo.svg'))

        self.pointManager = PointManager(self)
        self.surfaceManager = SurfaceManager(self)
        self.unit_manager = UnitManager()

        self.point_group_count = 0
        self.point_item_count = 0
        self.terrain_item_count = 0

        self.createUI()

    def createUI(self):
        self.toolbar = QToolBar(self)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)

        self.scene = BaseScene(self.unit_manager, self)
        self.setCentralWidget(self.scene)

        self.createToolBarActions()
        self.createShortcuts()

    def createToolBarActions(self):
        points_panel_widgets_1 = []
        points_panel_widgets_2 = []
        surface_panel_widgets_1 = []
        surface_panel_widgets_2 = []

        import_points_btn = QPushButton('Import Point Data')
        import_points_btn.setObjectName('toolbarButton')
        import_points_btn.clicked.connect(self.pointManager.importPoints)
        points_panel_widgets_1.append(import_points_btn)

        edit_points_btn = QPushButton('Edit Points')
        edit_points_btn.setObjectName('toolbarButton')
        edit_points_btn.clicked.connect(self.pointManager.editPoints)
        points_panel_widgets_2.append(edit_points_btn)

        create_surface_from_group = QPushButton('Create Surface From Points')
        create_surface_from_group.setObjectName('toolbarButton')
        create_surface_from_group.clicked.connect(self.pointManager.convertGroupToSurface)
        surface_panel_widgets_1.append(create_surface_from_group)

        create_surface_from_file = QPushButton('Create Surface From Data')
        create_surface_from_file.setObjectName('toolbarButton')
        create_surface_from_file.clicked.connect(self.surfaceManager.importSurfaceData)
        surface_panel_widgets_2.append(create_surface_from_file)

        points_panel = ToolBarContainer('Points', points_panel_widgets_1)
        points_panel.addRow(points_panel_widgets_2)
        surface_panel = ToolBarContainer('Surface', surface_panel_widgets_1)
        surface_panel.addRow(surface_panel_widgets_2)

        self.toolbar.addWidget(points_panel)
        self.toolbar.addWidget(surface_panel)

    def createShortcuts(self):
        undo_action = QAction('Undo', self)
        undo_action.setShortcut(QKeySequence('Ctrl+Z'))
        undo_action.triggered.connect(self.scene.undo)

        redo_action = QAction('Redo', self)
        redo_action.setShortcut(QKeySequence('Ctrl+Y'))
        redo_action.triggered.connect(self.scene.redo)

        self.addAction(undo_action)
        self.addAction(redo_action)

    def addTestObj(self):
        self.pointManager.directImport('sample_data/points.txt')

    def glScene(self):
        return self.scene

    def unitManager(self):
        return self.unit_manager


if __name__ == '__main__':
    from mp_software_stylesheets.styles import blenderCSS

    app = QApplication(sys.argv + ['-platform', 'windows:darkmode=1'])
    app.setStyleSheet(blenderCSS)

    win = DOT39()
    win.show()
    win.showMaximized()
    win.addTestObj()

    sys.exit(app.exec())
