from src._imports import *


class BaseItem(object):
    def __init__(self, scene, name: str = ''):
        self._scene = scene
        self._name = name
        self._color = (0.0, 0.0, 0.0)
        self._pos = [0.0, 0.0, 0.0]
        self._visible = True
        self._is_selectable = True
        self._selected = False
        self._hovered = False

    def name(self):
        return self._name

    def setName(self, name: str):
        self._name = name

    def setColor(self, color: tuple[float, float, float]):
        self._color = color

    def setSelected(self, s: bool):
        if self._is_selectable:
            self._selected = s

    def setHovered(self, hovered: bool):
        self._hovered = hovered

    def setVisible(self, v: bool):
        self._visible = v

    def isSelected(self):
        return self._selected

    def isVisible(self):
        return self._visible

    def isHovered(self):
        return self._hovered

    def setSelectable(self, s: bool):
        self._is_selectable = s

    def isSelectable(self):
        return self._is_selectable

    def setPos(self, pos: list[float]):
        self._pos = pos

    def pos(self):
        return [self._pos[0], self._pos[1], self._pos[2]]

    def x(self):
        return self.pos()[0]

    def y(self):
        return self.pos()[1]

    def z(self):
        return self.pos()[2]

    def color(self):
        return self._color

    def scene(self):
        return self._scene

    def render(self, color=None):
        if not self._visible:
            return

    def update(self):
        pass
