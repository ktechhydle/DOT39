from src._imports import *
from src.gui.dialogs import GetTerrainDialog
from src.framework.scene.functions import isConvertibleToFloat
from src.framework.scene.undo_commands import *
from src.framework.items.terrain_item import TerrainItem
from src.framework.items.point_item import PointItem
from src.framework.items.point_group import PointGroupItem
from src.errors.pnezd_data_error import DOT39PNEZDDataError


class SurfaceManager:
    def __init__(self, parent):
        self._parent = parent

    def importSurfaceData(self):
        file, _ = QFileDialog.getOpenFileName(self.parent(),
                                              'Import Surface Data',
                                              '',
                                              'Supported types (*.csv *.txt)')

        if file:
            points = []

            try:
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

                            if not line:
                                continue

                            row = line.split(sep=',')

                            if isConvertibleToFloat(row[1]):
                                points.append((float(row[2]), float(row[1]), float(row[3])))
            except:
                raise DOT39PNEZDDataError()

            # Potential GEOTIFF Import
            '''elif file.endswith('.tiff') or file.endswith('.tif'):
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
                            points.append((lon, lat, value))'''

            self.parent().terrain_item_count += 1

            item = TerrainItem(self.parent().glScene(), self.parent().glScene().shaderProgram(), points,
                               name=f'Terrain Item #{self.parent().terrain_item_count}')
            self.parent().glScene().addUndoCommand(AddItemCommand(item, self.parent().glScene()))

    def convertSurfaceToGroup(self):
        item = self.parent().glScene().activeSelection()
        terrain_item = None

        if item and isinstance(item, TerrainItem):
            terrain_item = self.parent().glScene().activeSelection()

        else:
            dialog = GetTerrainDialog(self.parent().glScene(), self.parent())
            dialog.exec()

            if dialog.activeResult():
                terrain_item = dialog.activeResult()

        if terrain_item:
            self.parent().terrain_item_count -= 1
            self.parent().point_group_count += 1

            points = []

            for point_num, point in enumerate(terrain_item.points()):
                item = PointItem(self.parent().glScene(),
                                 f'{point_num + 1}',
                                 pos=[*point],
                                 name=f'POINT #{point_num + 1}')
                points.append(item)

            point_group_item = PointGroupItem(self.parent().glScene(),
                                              points,
                                              f'Point Item Group #{self.parent().point_group_count}')

            self.parent().glScene().addUndoCommand(SurfaceToPointsCommand(point_group_item,
                                                                           terrain_item,
                                                                           self.parent().glScene(), ))

    def parent(self):
        return self._parent
