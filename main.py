from src.gui.widgets import *
from src.gui.panels import ScenePanel, HomePanel
from src.framework.scene.base_scene import BaseScene
from src.framework.scene.undo_commands import AddItemCommand
from src.framework.managers.unit_manager import UnitManager
from src.framework.managers.point_manager import PointManager
from src.framework.managers.surface_manager import SurfaceManager
from src.framework.managers.alignment_manager import AlignmentManager
from src.framework.items.alignment_item import AlignmentItem


class DOT39(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('DOT39')
        self.setWindowIcon(QIcon('resources/icons/logos/dot39_logo.svg'))

        self.pointManager = PointManager(self)
        self.surfaceManager = SurfaceManager(self)
        self.alignmentManager = AlignmentManager(self)
        self.unit_manager = UnitManager()

        self.point_group_count = 0
        self.point_item_count = 0
        self.terrain_item_count = 0
        self.alignment_item_count = 0

        self._toolbar_panels = []

        self.createUI()

    def createUI(self):
        self.top_toolbar = QToolBar(self)
        self.top_toolbar.setIconSize(QSize(50, 50))
        self.top_toolbar.setMovable(False)
        self.top_toolbar.contextMenuEvent = lambda *event: None
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.top_toolbar)

        self.scene = BaseScene(self)
        self.scene.setParent(self)
        self.setCentralWidget(self.scene)

        self.createToolBarActions()
        self.createShortcuts()
        self.createPanels()

    def createToolBarActions(self):
        self.home_btn = QToolButton()
        self.home_btn.setText('Home')
        self.home_btn.setIcon(QIcon('resources/icons/logos/dot39_logo.svg'))
        self.home_btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.home_btn.setCheckable(True)
        self.home_btn.clicked.connect(self.updateCentralWidget)

        self._toolbar_btn_group = QButtonGroup(self)
        points_panel_widgets_1 = []
        points_panel_widgets_2 = []
        surface_panel_widgets_1 = []
        surface_panel_widgets_2 = []
        alignment_panel_widgets_1 = []
        alignment_panel_widgets_2 = []

        import_points_btn = ToolBarButton('Import Point Data')
        import_points_btn.clicked.connect(self.pointManager.importPoints)
        points_panel_widgets_1.append(import_points_btn)

        edit_points_btn = ToolBarButton('Edit Points')
        edit_points_btn.clicked.connect(self.pointManager.editPoints)
        points_panel_widgets_2.append(edit_points_btn)

        create_surface_from_group = ToolBarButton('Create Surface From Points')
        create_surface_from_group.clicked.connect(self.pointManager.convertGroupToSurface)
        surface_panel_widgets_1.append(create_surface_from_group)

        create_surface_from_file = ToolBarButton('Create Surface From Data')
        create_surface_from_file.clicked.connect(self.surfaceManager.importSurfaceData)
        surface_panel_widgets_2.append(create_surface_from_file)

        create_alignment_btn = ToolBarButton('Create Alignment')
        create_alignment_btn.clicked.connect(self.alignmentManager.createAlignment)
        alignment_panel_widgets_1.append(create_alignment_btn)

        edit_alignment_btn = ToolBarButton('Edit Alignment')
        edit_alignment_btn.clicked.connect(self.alignmentManager.editAlignment)
        alignment_panel_widgets_2.append(edit_alignment_btn)

        points_panel = ToolBarContainer('Points', points_panel_widgets_1)
        points_panel.addRow(points_panel_widgets_2)
        surface_panel = ToolBarContainer('Surface', surface_panel_widgets_1)
        surface_panel.addRow(surface_panel_widgets_2)
        alignment_panel = ToolBarContainer('Alignment', alignment_panel_widgets_1)
        alignment_panel.addRow(alignment_panel_widgets_2)
        self._toolbar_panels.append(points_panel)
        self._toolbar_panels.append(surface_panel)
        self._toolbar_panels.append(alignment_panel)

        self.top_toolbar.addWidget(self.home_btn)
        self.top_toolbar.addWidget(points_panel)
        self.top_toolbar.addWidget(surface_panel)
        self.top_toolbar.addWidget(alignment_panel)

    def createShortcuts(self):
        undo_action = QAction('Undo', self)
        undo_action.setShortcut(QKeySequence('Ctrl+Z'))
        undo_action.triggered.connect(self.scene.undo)

        redo_action = QAction('Redo', self)
        redo_action.setShortcut(QKeySequence('Ctrl+Y'))
        redo_action.triggered.connect(self.scene.redo)

        self.addAction(undo_action)
        self.addAction(redo_action)

    def createPanels(self):
        self.toolbox = ToolBox(self.scene)
        self.toolbox.setCursor(Qt.CursorShape.ArrowCursor)
        self.toolbox.setFixedWidth(300)
        self.toolbox.move(11, 11)

        self.home_panel = HomePanel()
        self.scene_panel = ScenePanel(self.scene, self)

        self.toolbox.addItem(self.scene_panel, 'Scene')
        self.toolbox.addSpacer()

    def addTestObj(self):
        self.pointManager.directImport('sample_data/points.txt')

        alignment = AlignmentItem(self.glScene(), self.glScene().shaderProgram())
        alignment.drawStart(0, 0)
        alignment.drawLine(50, 50)
        alignment.drawClothoid(100, 100)

        self.glScene().addUndoCommand(AddItemCommand(alignment, self.glScene()))

    def updateCentralWidget(self):
        if self.home_btn.isChecked():
            self.setToolBarPanelsEnabled(False)

            # Instead of replacing self.scene, just hide it
            self.scene.setParent(None)
            self.home_panel.setParent(self)
            self.setCentralWidget(self.home_panel)

        else:
            self.setToolBarPanelsEnabled(True)

            # Restore scene only if its not already set
            if self.centralWidget() is not self.scene:
                self.home_panel.setParent(None)
                self.setCentralWidget(self.scene)

    def setToolBarPanelsEnabled(self, enabled: bool):
        for panel in self._toolbar_panels:
            panel.setEnabled(enabled)

    def glScene(self):
        return self.scene

    def toolBarPanels(self) -> list[ToolBarContainer]:
        return self._toolbar_panels

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
    win.updateCentralWidget()

    # Crash handler
    def handle_exception(exctype, value, tb):
        QMessageBox.critical(win, 'Error:(', f'DOT39 encountered an error:\n\n{value}\n')
        sys.__excepthook__(exctype, value, tb)

    # Set the global exception hook
    sys.excepthook = handle_exception

    sys.exit(app.exec())
