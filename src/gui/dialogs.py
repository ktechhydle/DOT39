from src._imports import *
from src.framework.items.point_group import PointGroupItem


class GetPointGroupDialog(QDialog):
    def __init__(self, scene, parent):
        super().__init__(parent)
        self.setWindowTitle('Choose Point Group')
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        self.scene = scene
        self._result = None

        self.createPotentialList()
        self.createUI()

    def createPotentialList(self):
        self.potential_list = {}

        for item in self.scene.items():
            if isinstance(item, PointGroupItem):
                self.potential_list[item.name()] = item

    def createUI(self):
        self.setLayout(QVBoxLayout())

        self.point_group_combo = QComboBox(self)

        for k, v in self.potential_list.items():
            self.point_group_combo.addItem(k, v)

        self.button_group = QDialogButtonBox(self)
        self.button_group.addButton('Ok', QDialogButtonBox.AcceptRole)
        self.button_group.addButton('Cancel', QDialogButtonBox.RejectRole)
        self.button_group.accepted.connect(self.accept)
        self.button_group.rejected.connect(self.close)

        self.layout().addWidget(self.point_group_combo)
        self.layout().addWidget(self.button_group)

    def accept(self):
        self._result = self.point_group_combo.itemData(self.point_group_combo.currentIndex())

        self.close()

    def activeResult(self) -> PointGroupItem:
        return self._result
