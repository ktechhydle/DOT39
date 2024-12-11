from src._imports import *


class ToolBarContainer(QWidget):
    def __init__(self, name: str, widgets: list[QWidget], parent=None):
        super().__init__(parent)

        self._name = name
        self._widgets = widgets

        self._createUI()

    def _createUI(self):
        self.setLayout(QVBoxLayout())

        hlayout1 = QHBoxLayout()
        hlayout2 = QHBoxLayout()

        label = QLabel(self.name())
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hlayout1.addWidget(label)

        for w in self.widgets():
            hlayout2.addWidget(w)

        self.layout().addLayout(hlayout1)
        self.layout().addLayout(hlayout2)

    def name(self):
        return self._name

    def widgets(self):
        return self._widgets