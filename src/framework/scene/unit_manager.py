class UnitManager:
    def __init__(self):
        self._unit_type = 'ft.'

    def unitType(self):
        return self._unit_type

    def setUnitType(self, unit_type: str):
        self._unit_type = unit_type
