from src._imports import *
from src.framework.items.point_group import PointGroupItem
from src.framework.items.point_item import PointItem


class PointManager:
    def __init__(self, parent):
        self._parent = parent

        self.point_group_count = 0
        self.point_item_count = 0

    def importPoints(self):
        file, _ = QFileDialog.getOpenFileName(self.parent(),
                                              'Import Point Data',
                                              '',
                                              '*.csv files;;'
                                              '*.txt files;;')

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
                    for line in f:
                        line = line.strip()  # Remove leading/trailing whitespace

                        if not line:  # Skip empty lines
                            continue

                        row = line.split()  # Split line into parts (default delimiter: whitespace)

                        if len(row) < 4:
                            continue

                        points.append({
                            'Point Number': row[0],  # First value
                            'Northing': float(row[1]),  # Second value
                            'Easting': float(row[2]),  # Third value
                            'Elevation': float(row[3]),  # Fourth value
                            'Description': row[4] if len(row) > 4 else ''  # Optional fifth value
                        })

            print(points, sep='\n')

            self.point_group_count += 1
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
                                 [northing / 10, easting / 10, elevation / 10],
                                 name=f'#{point_number}: {description}')
                point_items.append(item)

            point_group = PointGroupItem(self.parent().scene, point_items)
            self.parent().glScene().addItem(point_group)
            self.parent().glScene().update()

    def parent(self):
        return self._parent
