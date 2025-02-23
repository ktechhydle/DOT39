class ToolManager(object):
    NoTool = 0
    SelectionTool = 1
    AlignmentTool = 2

    def __init__(self, scene):
        self._scene = scene
        self._current_tool = 1

    def setCurrentTool(self, tool: int):
        self._current_tool = tool

    def resetTools(self):
        self.setCurrentTool(self.SelectionTool)

    def currentTool(self) -> int:
        return self._current_tool

    def scene(self):
        return self._scene