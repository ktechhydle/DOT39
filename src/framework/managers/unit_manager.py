from pyproj import Transformer, CRS


class UnitManager:
    def __init__(self):
        self._unit_type = ''
        self._input_espg_code = None
        self._target_espg_code = None

    def setInputESPG(self, code: int):
        self._input_espg_code = code

    def setTargetESPG(self, code: int):
        self._target_espg_code = code

    def setUnitType(self, unit_type: str):
        self._unit_type = unit_type

    def inputESPG(self):
        return self._input_espg_code

    def targetESPG(self):
        return self._target_espg_code

    def unitType(self):
        return self._unit_type

    def transformedXY(self, x=None, y=None):
        """
        Transforms coordinates using input and target EPSG codes.
        If no coordinates are provided, defaults to (0, 0).

        :param x: Optional X coordinate (e.g., Longitude or Easting). Defaults to 0.
        :param y: Optional Y coordinate (e.g., Latitude or Northing). Defaults to 0.
        :return: Transformed X, Y coordinates.
        """
        # Define the input CRS (default to EPSG 2236 - NAD83 / Florida East)
        input_crs = CRS.from_epsg(self.inputESPG() if self.inputESPG() else 2236)

        # Define the target CRS (default to EPSG 3857)
        target_crs = CRS.from_epsg(self.targetESPG() if self.targetESPG() else 3857)

        # Default to (0, 0) if coordinates are not provided
        x = x if x is not None else 0
        y = y if y is not None else 0

        # Create a transformer
        transformer = Transformer.from_crs(input_crs, target_crs, always_xy=True)

        # Transform coordinates
        x_transformed, y_transformed = transformer.transform(x, y)

        return x_transformed, y_transformed

