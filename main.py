from src._imports import *
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


if __name__ == '__main__':
    app = QApplication([])
    app.setStyleSheet(blenderCSS)

    win = DOT39()
    win.show()

    sys.exit(app.exec())
