from src._imports import *
from src.framework.scene.functions import isConvertibleToFloat
from src.gui.dialogs import GetPointGroupDialog, EditPointGroupDialog
from src.framework.items.point_group import PointGroupItem
from src.framework.items.point_item import PointItem
from src.framework.items.terrain_item import TerrainItem
from src.framework.scene.undo_commands import *


class PointManager:
    def __init__(self, parent):
        self._parent = parent

    def importPoints(self):
        file, _ = QFileDialog.getOpenFileName(self.parent(),
                                              'Import Point Data',
                                              '',
                                              'Supported types (*.csv *.txt)')

        if file:
            points = []

            if file.endswith('.csv'):
                with open(file, 'r') as f:
                    reader = csv.reader(f)
                    headers = next(reader)
                    for row in reader:
                        if len(row) < 4:
                            continue
                        points.append({
                            'Point Number': row[0],  # First column
                            'Northing': float(row[1]),  # Second column
                            'Easting': float(row[2]),  # Third column
                            'Elevation': float(row[3]),  # Fourth column
                            'Description': row[4] if len(row) > 4 else ''  # Fifth column (optional)
                        })

            elif file.endswith('.txt'):
                with open(file, 'r') as f:
                    for line in f.readlines():
                        line = line.strip()

                        if not line:  # Skip empty lines
                            continue

                        row = line.split(sep=',')  # Split line into parts (default delimiter: whitespace)

                        if isConvertibleToFloat(row[1]):
                            points.append({
                                'Point Number': row[0],  # First value
                                'Northing': float(row[1]),  # Second value
                                'Easting': float(row[2]),  # Third value
                                'Elevation': float(row[3]),  # Fourth value
                                'Description': row[4] if len(row) > 4 else ''  # Optional fifth value
                            })

            print(points, sep='\n')

            self.parent().point_group_count += 1
            self.processPoints(points)

    def directImport(self, file: str):
        points = []

        if file.endswith('.csv'):
            with open(file, 'r') as f:
                reader = csv.reader(f)
                headers = next(reader)
                for row in reader:
                    if len(row) < 4:
                        continue
                    points.append({
                        'Point Number': row[0],  # First column
                        'Northing': float(row[1]),  # Second column
                        'Easting': float(row[2]),  # Third column
                        'Elevation': float(row[3]),  # Fourth column
                        'Description': row[4] if len(row) > 4 else ''  # Fifth column (optional)
                    })

        elif file.endswith('.txt'):
            with open(file, 'r') as f:
                for line in f.readlines():
                    line = line.strip()

                    if not line:  # Skip empty lines
                        continue

                    row = line.split(sep=',')  # Split line into parts (default delimiter: whitespace)

                    if isConvertibleToFloat(row[1]):
                        points.append({
                            'Point Number': row[0],  # First value
                            'Northing': float(row[1]),  # Second value
                            'Easting': float(row[2]),  # Third value
                            'Elevation': float(row[3]),  # Fourth value
                            'Description': row[4] if len(row) > 4 else ''  # Optional fifth value
                        })

        print(points, sep='\n')

        self.parent().point_group_count += 1
        self.processPoints(points)

    def processPoints(self, points: list[dict]):
        if points:
            point_items = []

            for point_dict in points:
                # Extract the values in order as a list
                values = list(point_dict.values())

                # Assign values to variables based on their position in the list
                point_number = values[0]
                northing = float(values[1])
                easting = float(values[2])
                elevation = float(values[3])
                description = values[4] if len(values) > 4 else ''

                item = PointItem(self.parent().glScene(),
                                 self.parent().glScene().shaderProgram(),
                                 point_number,
                                 [easting, northing, elevation],
                                 name=f'{description}')
                point_items.append(item)

            point_group = PointGroupItem(self.parent().scene, point_items,
                                         name=f'Point Item Group #{self.parent().point_group_count}')
            self.parent().glScene().addUndoCommand(AddItemCommand(point_group, self.parent().glScene()))
            self.parent().glScene().updateArcBall()

    def convertGroupToSurface(self):
        item = self.parent().glScene().activeSelection()
        point_group = None

        if item and isinstance(item, PointGroupItem):
            point_group = self.parent().glScene().activeSelection()

        else:
            dialog = GetPointGroupDialog(self.parent().glScene(), self.parent())
            dialog.exec()

            if dialog.activeResult():
                point_group = dialog.activeResult()

        if point_group:
            self.parent().terrain_item_count += 1

            points = []

            for item in point_group.points():
                points.append((item.x(), item.y(), item.z()))

            surface_item = TerrainItem(self.parent().glScene(),
                                       self.parent().glScene().shaderProgram(),
                                       points=points,
                                       name=f'Terrain Item #{self.parent().terrain_item_count}')

            self.parent().glScene().addUndoCommand(PointsToSurfaceCommand(point_group,
                                                                          surface_item,
                                                                          self.parent().glScene()))

    def editPoints(self):
        item = self.parent().glScene().activeSelection()
        point_group = None

        if item and isinstance(item, PointGroupItem):
            point_group = self.parent().glScene().activeSelection()

        else:
            dialog = GetPointGroupDialog(self.parent().glScene(), self.parent())
            dialog.exec()

            if dialog.activeResult():
                point_group = dialog.activeResult()

        editor = EditPointGroupDialog(self.parent().glScene(), point_group, self.parent())
        editor.show()

    def parent(self):
        return self._parent
