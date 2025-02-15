from src._imports import QMouseEvent


class BaseTool(object):
    def __init__(self, scene):
        self._scene = scene

    def mousePress(self, event: QMouseEvent):
        pass

    def mouseMove(self, event: QMouseEvent):
        pass

    def mouseRelease(self, event: QMouseEvent):
        pass

    def specialToolTip(self, event: QMouseEvent):
        pass

    def scene(self):
        return self._scene