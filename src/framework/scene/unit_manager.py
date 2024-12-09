class UnitManager:
    def __init__(self):
        self._scale_factors = {
            '1 in. = 40 ft.': '1 : 40',
            '1 in. = 50 ft.': '1 : 50',
            '1 in. = 75 ft.': '1 : 75',
            '1 in. = 100 ft.': '1 : 100',
        }

        # Scale factor
        self._scale_factor = '1 : 40'

    def setScaleFactor(self, scale_factor):
        self._scale_factor = scale_factor

    def scaleFactor(self):
        # Parse the scale factor
        lhs = int(self._scale_factor.split()[0])  # Left-hand side
        rhs = int(self._scale_factor.split()[2])  # Right-hand side

        # Scale factor is the real-world value per drawing unit
        return rhs / lhs

    def scaleFactors(self):
        return self._scale_factors

    def actualScale(self, x, y):
        # Use the scale factor to compute real-world coordinates
        scale = self.scaleFactor()
        real_x = x * scale
        real_y = y * scale
        return real_x, real_y
