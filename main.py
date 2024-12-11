from src._imports import *
from src.gui.widgets import *
from src.framework.scene.base_scene import BaseScene
from mp_software_stylesheets.styles import blenderCSS


class DOT39(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('DOT39')
        self.setWindowIcon(QIcon('icons/logos/dot39_logo.svg'))
        self.resize(800, 800)

        self.createUI()

    def createUI(self):
        self.toolbar = QToolBar(self)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)

        self.scene = BaseScene(self)
        self.setCentralWidget(self.scene)

        self.createToolBarActions()
        self.createShortcuts()

    def createToolBarActions(self):
        widgets = []

        import_surface_btn = QPushButton('TIN Import')
        widgets.append(import_surface_btn)

        surface_panel = ToolBarContainer('Surface & Terrain', widgets)

        self.toolbar.addWidget(surface_panel)

    def createShortcuts(self):
        undo_action = QAction('Undo', self)
        undo_action.setShortcut(QKeySequence('Ctrl+Z'))
        undo_action.triggered.connect(self.scene.undoStack().undo)

        redo_action = QAction('Redo', self)
        redo_action.setShortcut(QKeySequence('Ctrl+Y'))
        redo_action.triggered.connect(self.scene.undoStack().redo)

        self.addAction(undo_action)
        self.addAction(redo_action)


if __name__ == '__main__':
    app = QApplication([])
    app.setStyleSheet(blenderCSS)

    win = DOT39()
    win.show()

    sys.exit(app.exec())
