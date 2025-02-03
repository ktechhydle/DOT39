from src._imports import *
from src.framework.scene.functions import isConvertibleToFloat
from src.framework.items.terrain_item import TerrainItem
from src.framework.scene.undo_commands import *
import rasterio


class SurfaceManager:
    def __init__(self, parent):
        self._parent = parent

    def importSurfaceData(self):
        file, _ = QFileDialog.getOpenFileName(self.parent(),
                                              'Import Surface Data',
                                              '',
                                              'Supported types (*.csv *.txt *.tif *.tiff)')

        if file:
            points = []

            if file.endswith('.csv'):
                with open(file, 'r') as f:
                    reader = csv.reader(f)
                    headers = next(reader)
                    for row in reader:
                        if len(row) < 4:
                            continue
                        points.append((float(row[2]), float(row[1]), float(row[3])))

            elif file.endswith('.txt'):
                with open(file, 'r') as f:
                    for line in f.readlines():
                        line = line.strip()

                        if not line:  # Skip empty lines
                            continue

                        row = line.split(sep=',')  # Split line into parts (default delimiter: whitespace)

                        if isConvertibleToFloat(row[1]):
                            points.append((float(row[2]), float(row[1]), float(row[3])))

            elif file.endswith('.tiff') or file.endswith('.tif'):
                with rasterio.open(file) as dataset:
                    band1 = dataset.read(1)  # Read the first band (elevation or intensity)
                    transform = dataset.transform  # Get affine transformation
                    rows, cols = band1.shape

                    for row in range(rows):
                        for col in range(cols):
                            value = band1[row, col]
                            if np.isnan(value):  # Ignore NoData values
                                continue

                            # Convert pixel coordinates to real-world coordinates
                            lon, lat = rasterio.transform.xy(transform, row, col)
                            points.append((lon, lat, value))

            self.parent().terrain_item_count += 1

            item = TerrainItem(self.parent().glScene(), self.parent().glScene().shaderProgram(), points,
                               name=f'Terrain Item #{self.parent().terrain_item_count}')
            self.parent().glScene().addUndoCommand(AddItemCommand(item, self.parent().glScene()))

    def parent(self):
        return self._parent