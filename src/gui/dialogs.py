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
        self.point_group_combo.currentIndexChanged.connect(self.valChanged)

        for k, v in self.potential_list.items():
            self.point_group_combo.addItem(k, v)

        self.button_group = QDialogButtonBox(self)
        self.button_group.addButton('Ok', QDialogButtonBox.AcceptRole)
        self.button_group.addButton('Cancel', QDialogButtonBox.RejectRole)
        self.button_group.accepted.connect(self.accept)
        self.button_group.rejected.connect(self.close)

        self.layout().addWidget(self.point_group_combo)
        self.layout().addWidget(self.button_group)

    def valChanged(self):
        self.scene.clearSelection()

        item = self.point_group_combo.itemData(self.point_group_combo.currentIndex())
        item.setSelected(True)

    def accept(self):
        self._result = self.point_group_combo.itemData(self.point_group_combo.currentIndex())

        self.close()

    def activeResult(self) -> PointGroupItem:
        return self._result

    def close(self):
        self.scene.clearSelection()

        super().close()


class EditPointGroupDialog(QDialog):
    def __init__(self, scene, point_group, parent):
        super().__init__(parent)
        self.setWindowTitle('Point Editor')
        self.setWindowFlag(Qt.WindowType.Tool)

        self.scene = scene
        self.point_group = point_group

        self.createUI()

    def createUI(self):
        self.setLayout(QVBoxLayout())

        self.editor = QTableWidget(self)
        self.editor.setColumnCount(5)

        self.button_group = QDialogButtonBox(self)
        self.button_group.addButton('Ok', QDialogButtonBox.AcceptRole)
        self.button_group.addButton('Cancel', QDialogButtonBox.RejectRole)
        self.button_group.accepted.connect(self.accept)
        self.button_group.rejected.connect(self.cancel)

        self.layout().addWidget(self.editor)
        self.layout().addWidget(self.button_group)

    def accept(self):
        self.close()

    def cancel(self):
        self.close()
