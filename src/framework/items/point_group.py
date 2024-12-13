from src._imports import *
from src.framework.items.base_item import BaseItem
from src.framework.items.point_item import PointItem
from src.framework.scene.functions import hexToRGB


class PointGroupItem(BaseItem):
    def __init__(self, scene, points: list[PointItem], name=''):
        super().__init__(scene, name)
        self._color = hexToRGB('#ff0000')
        self._points = points

    def color(self):
        return self._color

    def points(self) -> list[PointItem]:
        return self._points

    def setColor(self, color: str):
        for point in self.points():
            point.setColor(color)

        self._color = color

    def setPoints(self, points: list[PointItem]):
        self._points = points

