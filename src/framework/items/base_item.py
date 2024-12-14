from src._imports import *


class BaseItem(object):
    def __init__(self, scene, name: str = ''):
        self._scene = scene
        self._name = name
        self._pos = [0.0, 0.0, 0.0]
        self._visible = True
        self._is_selectable = True
        self._selected = False
        self._standard_div = 10.0

    def name(self):
        return self._name

    def standardDiv(self):
        return self._standard_div

    def setName(self, name: str):
        self._name = name

    def setStandardDiv(self, div: float):
        self._standard_div = div

    def setSelected(self, s: bool):
        self._selected = s

    def setVisible(self, v: bool):
        self._visible = v

    def isSelected(self):
        return self._selected

    def isVisible(self):
        return self._visible

    def setSelectable(self, s: bool):
        self._is_selectable = s

    def isSelectable(self):
        return self._is_selectable

    def setPos(self, pos: list[float]):
        self._pos = pos

    def pos(self):
        return [self._pos[0] / self.standardDiv(), self._pos[1] / self.standardDiv(), self._pos[2] / self.standardDiv()]

    def x(self):
        return self.pos()[0]

    def y(self):
        return self.pos()[1]

    def z(self):
        return self.pos()[2]

    def scene(self):
        return self._scene

    def render(self):
        if not self.isVisible():
            return

    def destroy(self):
        pass
