from mp_software_stylesheets.styles import blenderCSS
from src._imports import *


class DOT39(QMainWindow):
    def __init__(self):
        super().__init__()

        self.createUI()

    def createUI(self):
        pass


if __name__ == '__main__':
    app = QApplication([])
    app.setStyleSheet(blenderCSS)

    win = DOT39()
    win.show()

    sys.exit(app.exec())
