from src._imports import *
from src.gui.widgets import IntegerInput, FloatInput, StringInput, OptionInput
from src.framework.items.point_group import PointGroupItem
from src.framework.items.alignment_item import AlignmentItem
from src.framework.items.terrain_item import TerrainItem
from src.framework.scene.functions import isConvertibleToFloat
from src.framework.scene.undo_commands import *
from src.framework.viewers.vertical_alignment_viewer import VerticalAlignmentViewer


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


class GetAlignmentDialog(QDialog):
    def __init__(self, scene, parent):
        super().__init__(parent)
        self.setWindowTitle('Choose Alignment')
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        self.scene = scene
        self._result = None

        self.createPotentialList()
        self.createUI()

    def createPotentialList(self):
        self.potential_list = {}

        for item in self.scene.items():
            if isinstance(item, AlignmentItem):
                self.potential_list[item.name()] = item

    def createUI(self):
        self.setLayout(QVBoxLayout())

        self.alignment_combo = QComboBox(self)
        self.alignment_combo.currentIndexChanged.connect(self.valChanged)

        for k, v in self.potential_list.items():
            self.alignment_combo.addItem(k, v)

        self.button_group = QDialogButtonBox(self)
        self.button_group.addButton('Ok', QDialogButtonBox.AcceptRole)
        self.button_group.addButton('Cancel', QDialogButtonBox.RejectRole)
        self.button_group.accepted.connect(self.accept)
        self.button_group.rejected.connect(self.close)

        self.layout().addWidget(self.alignment_combo)
        self.layout().addWidget(self.button_group)

    def valChanged(self):
        self.scene.selectionTool().clearSelection()

        item = self.alignment_combo.itemData(self.alignment_combo.currentIndex())
        item.setSelected(True)

    def accept(self):
        self._result = self.alignment_combo.itemData(self.alignment_combo.currentIndex())

        self.close()

    def activeResult(self) -> AlignmentItem:
        return self._result

    def close(self):
        self.scene.selectionTool().clearSelection()

        super().close()


class GetTerrainDialog(QDialog):
    def __init__(self, scene, parent):
        super().__init__(parent)
        self.setWindowTitle('Choose Terrain')
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        self.scene = scene
        self._result = None

        self.createPotentialList()
        self.createUI()

    def createPotentialList(self):
        self.potential_list = {}

        for item in self.scene.items():
            if isinstance(item, TerrainItem):
                self.potential_list[item.name()] = item

    def createUI(self):
        self.setLayout(QVBoxLayout())

        self.terrain_combo = QComboBox(self)
        self.terrain_combo.currentIndexChanged.connect(self.valChanged)

        for k, v in self.potential_list.items():
            self.terrain_combo.addItem(k, v)

        self.button_group = QDialogButtonBox(self)
        self.button_group.addButton('Ok', QDialogButtonBox.AcceptRole)
        self.button_group.addButton('Cancel', QDialogButtonBox.RejectRole)
        self.button_group.accepted.connect(self.accept)
        self.button_group.rejected.connect(self.close)

        self.layout().addWidget(self.terrain_combo)
        self.layout().addWidget(self.button_group)

    def valChanged(self):
        self.scene.selectionTool().clearSelection()

        item = self.terrain_combo.itemData(self.terrain_combo.currentIndex())
        item.setSelected(True)

    def accept(self):
        self._result = self.terrain_combo.itemData(self.terrain_combo.currentIndex())

        self.close()

    def activeResult(self) -> TerrainItem:
        return self._result

    def close(self):
        self.scene.selectionTool().clearSelection()

        super().close()


class EditPointGroupDialog(QDialog):
    def __init__(self, scene, point_group: PointGroupItem, parent):
        super().__init__(parent)
        self.setWindowTitle('Point Editor')
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
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
            QHeaderView.ResizeMode.Stretch)
        self.editor.verticalHeader().setHidden(True)

        self.layout().addWidget(self.editor)

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

        self.editor.cellChanged.connect(self.applyChanges)

    def applyChanges(self):
        new_point_attr = []

        # Iterate through each row of the table
        for row in range(self.editor.rowCount()):
            try:
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
            except:
                pass

        self.scene.addUndoCommand(EditPointsCommand(self.point_group, self.og_point_attr, new_point_attr))

        self.og_point_attr = new_point_attr


class EditAlignmentDialog(QDialog):
    def __init__(self, scene, alignment: AlignmentItem, parent):
        super().__init__(parent)
        self.setWindowTitle('Alignment Editor')
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.resize(800, 300)

        self.scene = scene
        self.alignment = alignment
        self._editor_row_count = 1

        # Undo storage
        self.og_path = self.alignment.horizontalPath()
        self.og_calls = self.alignment.drawCalls()

        self.createUI()
        self.createTable()

    def createUI(self):
        self.setLayout(QVBoxLayout())

        self.add_point_btn = QPushButton('+')
        self.add_point_btn.setToolTip('Add a new point along the alignment')
        self.add_point_btn.setFixedWidth(25)
        self.add_point_btn.clicked.connect(self.addNewPointOnAlignment)
        self.remove_point_btn = QPushButton('-')
        self.remove_point_btn.setToolTip('Remove the most recent point on the alignment')
        self.remove_point_btn.setFixedWidth(25)
        self.remove_point_btn.clicked.connect(self.removePointOnAlignment)

        self.editor = QTableWidget(self)
        self.editor.setColumnCount(3)
        self.editor.setHorizontalHeaderLabels(['Type', 'X', 'Y'])
        self.editor.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        self.editor.verticalHeader().setHidden(True)

        self.layout().addWidget(self.add_point_btn)
        self.layout().addWidget(self.remove_point_btn)
        self.layout().addWidget(self.editor)

    def createTable(self):
        self.editor.setRowCount(len(self.alignment.drawCalls()))

        for container in self.alignment.drawCalls():
            for draw_type, coord in container.items():
                x, y = coord

                type_item = QTableWidgetItem(draw_type)
                type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
                x_item = QTableWidgetItem(f'{x}')
                y_item = QTableWidgetItem(f'{y}')

                self.editor.setItem(self._editor_row_count - 1, 0, type_item)
                self.editor.setItem(self._editor_row_count - 1, 1, x_item)
                self.editor.setItem(self._editor_row_count - 1, 2, y_item)

                self._editor_row_count += 1

        self.editor.cellChanged.connect(self.applyChanges)
        self._editor_row_count -= 1

    def itemTextInRow(self, row, column) -> str:
        if self.editor.item(row, column):
            return self.editor.item(row, column).text()

        return ''

    def addNewPointOnAlignment(self):
        self._editor_row_count += 1
        self.editor.setRowCount(self._editor_row_count)

        type_item = QTableWidgetItem('Line')
        type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
        x_item = QTableWidgetItem('0')
        y_item = QTableWidgetItem('0')

        self.editor.setItem(self._editor_row_count - 1, 0, type_item)
        self.editor.setItem(self._editor_row_count - 1, 1, x_item)
        self.editor.setItem(self._editor_row_count - 1, 2, y_item)

        self.applyChanges()

    def removePointOnAlignment(self):
        if self.editor.rowCount() > 1:
            self._editor_row_count -= 1
            self.editor.removeRow(self._editor_row_count)

        self.applyChanges()

    def applyChanges(self):
        new_path = AlignmentItem(self.scene, self.scene.shaderProgram())

        # Iterate through each row of the table
        for i in range(self.editor.rowCount() + 1):
            if self.editor.item(i, 0):
                type = self.itemTextInRow(i, 0)
                x = self.itemTextInRow(i, 1)
                y = self.itemTextInRow(i, 2)

                try:
                    if type == 'Start Position':
                        new_path.drawStart(float(x), float(y))
                    elif type == 'Line':
                        new_path.drawLine(float(x), float(y))
                except:
                    pass

        self.scene.addUndoCommand(EditHorizontalAlignmentCommand(self.alignment, self.og_path, self.og_calls,
                                                                 new_path.horizontalPath(), new_path.drawCalls()))

        self.og_path = new_path.horizontalPath()


class AlignmentCreatorDialog(QDialog):
    def __init__(self, scene, parent):
        super().__init__(parent)
        self.setWindowTitle('Create Alignment')
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.resize(800, 300)

        self.scene = scene
        self._editor_row_count = 1
        self._alignment_item = AlignmentItem(self.scene, self.scene.shaderProgram())

        self.createUI()
        self.createTable()

    def createUI(self):
        self.parent().alignment_item_count += 1

        self.setLayout(QVBoxLayout())

        self.add_point_btn = QPushButton('+')
        self.add_point_btn.setToolTip('Add a new point along the alignment')
        self.add_point_btn.setFixedWidth(25)
        self.add_point_btn.clicked.connect(self.addNewPointOnAlignment)
        self.remove_point_btn = QPushButton('-')
        self.remove_point_btn.setToolTip('Remove the most recent point on the alignment')
        self.remove_point_btn.setFixedWidth(25)
        self.remove_point_btn.clicked.connect(self.removePointOnAlignment)

        self.editor = QTableWidget(self)
        self.editor.setColumnCount(3)
        self.editor.setHorizontalHeaderLabels(['Type', 'X', 'Y'])
        self.editor.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch)
        self.editor.verticalHeader().setHidden(True)
        self.editor.cellChanged.connect(self.updateAlignment)

        self.button_group = QDialogButtonBox(self)
        self.button_group.addButton('Ok', QDialogButtonBox.AcceptRole)
        self.button_group.addButton('Cancel', QDialogButtonBox.RejectRole)
        self.button_group.accepted.connect(self.accept)
        self.button_group.rejected.connect(lambda: self.close(remove=True))

        self.layout().addWidget(self.add_point_btn)
        self.layout().addWidget(self.remove_point_btn)
        self.layout().addWidget(self.editor)
        self.layout().addWidget(self.button_group)

    def createTable(self):
        self.editor.setRowCount(self._editor_row_count)

        type_item = QTableWidgetItem('Start Position')
        type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
        x_item = QTableWidgetItem('0')
        y_item = QTableWidgetItem('0')

        self.editor.setItem(self._editor_row_count - 1, 0, type_item)
        self.editor.setItem(self._editor_row_count - 1, 1, x_item)
        self.editor.setItem(self._editor_row_count - 1, 2, y_item)

    def addNewPointOnAlignment(self):
        self._editor_row_count += 1
        self.editor.setRowCount(self._editor_row_count)

        type_item = QTableWidgetItem('Line')
        type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
        x_item = QTableWidgetItem('0')
        y_item = QTableWidgetItem('0')

        self.editor.setItem(self._editor_row_count - 1, 0, type_item)
        self.editor.setItem(self._editor_row_count - 1, 1, x_item)
        self.editor.setItem(self._editor_row_count - 1, 2, y_item)

        self.updateAlignment()

    def removePointOnAlignment(self):
        if self.editor.rowCount() > 1:
            self._editor_row_count -= 1
            self.editor.removeRow(self._editor_row_count)

        self.updateAlignment()

    def updateAlignment(self):
        self._alignment_item.clearHorizontalPath()

        for i in range(self.editor.rowCount()):
            if self.editor.item(i, 0):
                type = self.itemTextInRow(i, 0)
                x = self.itemTextInRow(i, 1)
                y = self.itemTextInRow(i, 2)

                try:
                    if type == 'Start Position':
                        self._alignment_item.drawStart(float(x), float(y))
                    elif type == 'Line':
                        self._alignment_item.drawLine(float(x), float(y))
                except:
                    pass

        self.scene.addItem(self._alignment_item)

    def itemTextInRow(self, row, column) -> str:
        if self.editor.item(row, column):
            return self.editor.item(row, column).text()

        return ''

    def accept(self):
        self._alignment_item.setName(f'Alignment Item #{self.parent().alignment_item_count}')
        self.scene.addUndoCommand(AddItemCommand(self._alignment_item, self.scene))

        self.close()

    def close(self, remove=False):
        if remove:
            self.scene.removeItem(self._alignment_item)
            self.parent().alignment_item_count -= 1

        super().close()


class VerticalAlignmentCreatorDialog(QDialog):
    def __init__(self, scene, alignment: AlignmentItem, terrain: TerrainItem, parent):
        super().__init__(parent)
        self.setWindowTitle('Vertical Alignment')
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.resize(800, 300)

        self.scene = scene
        self.alignment_item = alignment
        self.terrain_item = terrain

        self.createUI()

    def createUI(self):
        self.setLayout(QVBoxLayout())

        self.viewer = VerticalAlignmentViewer(self.alignment_item, self.terrain_item, QPushButton(), self)

        self.button_group = QDialogButtonBox(self)
        self.button_group.addButton('Ok', QDialogButtonBox.AcceptRole)
        self.button_group.addButton('Cancel', QDialogButtonBox.RejectRole)
        self.button_group.accepted.connect(self.accept)
        self.button_group.rejected.connect(lambda: self.close(remove=True))

        self.layout().addWidget(self.viewer)
        self.layout().addWidget(self.button_group)

    def accept(self):
        self.close()

    def close(self, remove=False):
        if remove:
            self.alignment_item.clearVerticalPath()

        super().close()


class AlignmentAutoGeneratorDialog(QDialog):
    def __init__(self, scene, alignment: AlignmentItem, parent):
        super().__init__(parent)
        self.setWindowTitle('Auto Generate Alignment')
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.resize(250, 400)

        self.scene = scene
        self._alignment_item = alignment
        self._spacing = 15

        self.createUI()

    def createUI(self):
        self.setLayout(QVBoxLayout())

        self.speed_input = IntegerInput('Speed',
                                        (10, 100),
                                        QVBoxLayout(),
                                        ' mph',
                                        parent=self)
        self.curve_input = OptionInput('Curve Type',
                                       {'Clothoid': AlignmentItem.CurveTypeClothoid,
                                        'Circular': AlignmentItem.CurveTypeCircular},
                                       QVBoxLayout(),
                                       parent=self)

        self.button_group = QDialogButtonBox(self)
        self.button_group.addButton('Ok', QDialogButtonBox.AcceptRole)
        self.button_group.addButton('Cancel', QDialogButtonBox.RejectRole)
        self.button_group.accepted.connect(self.accept)
        self.button_group.rejected.connect(self.close)

        self.layout().addWidget(self.speed_input)
        self.layout().addSpacing(self._spacing)
        self.layout().addWidget(self.curve_input)
        self.layout().addSpacing(self._spacing)
        self.layout().addStretch()
        self.layout().addWidget(self.button_group)

    def accept(self):
        self.close()


class EditValueDialog(QDialog):
    def __init__(self, editable_item, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Edit Value')
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.resize(250, 125)

        self._editable_item = editable_item

        self.createUI()

    def createUI(self):
        self.setLayout(QVBoxLayout())

        if self._editable_item.inputType() == self._editable_item.InputTypeInt:
            self.input = IntegerInput('Value', (0, 10000), QVBoxLayout())
        elif self._editable_item.inputType() == self._editable_item.InputTypeFloat:
            self.input = FloatInput('Value', (0, 10000), QVBoxLayout())
        else:
            self.input = StringInput('Value', QVBoxLayout(), 'Edit here...')

        self.input.setDefaultValue(self._editable_item.value())

        self.button_group = QDialogButtonBox(self)
        self.button_group.addButton('Ok', QDialogButtonBox.AcceptRole)
        self.button_group.addButton('Cancel', QDialogButtonBox.RejectRole)
        self.button_group.accepted.connect(self.accept)
        self.button_group.rejected.connect(self.close)

        self.layout().addWidget(self.input)
        self.layout().addStretch()
        self.layout().addWidget(self.button_group)

    def accept(self):
        if self._editable_item.value() != self.input.value():
            self._editable_item.scene().addUndoCommand(ValueChangedCommand(
                self._editable_item,
                self.input.value(),
                self._editable_item.value()
            ))

        self.close()
