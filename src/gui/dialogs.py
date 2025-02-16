from src._imports import *
from src.framework.items.point_group import PointGroupItem
from src.framework.scene.undo_commands import *


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
        self.scene.selectionTool().clearSelection()

        item = self.point_group_combo.itemData(self.point_group_combo.currentIndex())
        item.setSelected(True)

    def accept(self):
        self._result = self.point_group_combo.itemData(self.point_group_combo.currentIndex())

        self.close()

    def activeResult(self) -> PointGroupItem:
        return self._result

    def close(self):
        self.scene.selectionTool().clearSelection()

        super().close()


class EditPointGroupDialog(QDialog):
    def __init__(self, scene, point_group: PointGroupItem, parent):
        super().__init__(parent)
        self.setWindowTitle('Point Editor')
        self.setWindowFlag(Qt.WindowType.Tool)
        self.resize(800, 300)

        self.scene = scene
        self.point_group = point_group

        # Undo storage
        self.og_point_attr = []

        self.createUI()
        self.createTable()

    def createUI(self):
        self.setLayout(QVBoxLayout())

        self.editor = QTableWidget(self)
        self.editor.setColumnCount(5)
        self.editor.setHorizontalHeaderLabels(['Point Number',
                                               f'Northing ({self.parent().unitManager().unitType()})',
                                               f'Easting ({self.parent().unitManager().unitType()})',
                                               f'Elevation ({self.parent().unitManager().unitType()})',
                                               'Description'])
        self.editor.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)

        self.button_group = QDialogButtonBox(self)
        self.button_group.addButton('Ok', QDialogButtonBox.AcceptRole)
        self.button_group.addButton('Cancel', QDialogButtonBox.RejectRole)
        self.button_group.accepted.connect(self.accept)
        self.button_group.rejected.connect(self.cancel)

        self.layout().addWidget(self.editor)
        self.layout().addWidget(self.button_group)

    def createTable(self):
        row_count = 0

        self.editor.setRowCount(len(self.point_group.points()))

        for point in self.point_group.points():
            point_attr = {
                'num': point.pointNumber(),
                'north': point.y(),
                'east': point.x(),
                'elev': point.z(),
                'desc': point.name()
            }
            self.og_point_attr.append(point_attr)

            point_num_item = QTableWidgetItem(f'{point.pointNumber()}')
            point_northing_item = QTableWidgetItem(f'{round(point.y(), 4)}')
            point_easting_item = QTableWidgetItem(f'{round(point.x(), 4)}')
            point_elevation_item = QTableWidgetItem(f'{round(point.z(), 4)}')
            point_description_item = QTableWidgetItem(point.name())

            self.editor.setItem(row_count, 0, point_num_item)
            self.editor.setItem(row_count, 1, point_northing_item)
            self.editor.setItem(row_count, 2, point_easting_item)
            self.editor.setItem(row_count, 3, point_elevation_item)
            self.editor.setItem(row_count, 4, point_description_item)

            row_count += 1

    def accept(self):
        new_point_attr = []

        # Iterate through each row of the table
        for row in range(self.editor.rowCount()):
            # Extract values from the table items for the current row
            num = int(self.editor.item(row, 0).text())
            north = float(self.editor.item(row, 1).text())
            east = float(self.editor.item(row, 2).text())
            elev = float(self.editor.item(row, 3).text())
            desc = self.editor.item(row, 4).text()

            # Create a dictionary similar to point_attr
            point_attr = {
                'num': num,
                'north': north,
                'east': east,
                'elev': elev,
                'desc': desc
            }
            new_point_attr.append(point_attr)

        self.scene.addUndoCommand(EditPointsCommand(self.point_group, self.og_point_attr, new_point_attr))

        self.close()

    def cancel(self):
        self.close()
