from src._imports import *


class BaseItem(object):
    def __init__(self, scene):
        self._scene = scene
        self._pos = [0.0, 0.0, 0.0]
        self._visible = True
        self._is_selectable = True
        self._selected = False

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
        return [self._pos[0] / 100, self._pos[1] / 100, self._pos[2] / 100]

    def scene(self):
        return self._scene

    def render(self):
        if not self.isVisible():
            return

    def destroy(self):
        pass
