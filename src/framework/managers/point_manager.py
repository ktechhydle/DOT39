from src._imports import *


class PointManager:
    def __init__(self, parent):
        self._parent = parent

    def importPoints(self):
        file, _ = QFileDialog.getOpenFileName(self.parent(),
                                              'Import Point Data',
                                              '',
                                              '*.csv files;;'
                                              '*.txt files;;'
                                              '*.xml (LandXML) files;;'
                                              '*.fbk (Field Book) files')

        if file:
            match file.endswith():
                case '.csv':
                    with open(file, 'r') as f:
                        reader = csv.DictReader(f)
                        points = []
                        for row in reader:
                            points.append({
                                'Point Number': row['Point Number'],
                                'Northing': float(row['Northing']),
                                'Easting': float(row['Easting']),
                                'Elevation': float(row['Elevation']),
                                'Description': row['Description']
                            })

    def parent(self):
        return self._parent
