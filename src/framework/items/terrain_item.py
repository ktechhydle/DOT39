from src._imports import *
from src.framework.items.base_item import *
from src.framework.scene.functions import hexToRGB


class TerrainItem(BaseItem):
    def __init__(self, scene, program, points: list[tuple[float, float, float]]):
        super().__init__(scene)
        self._color = hexToRGB('#00ff00')
        self._points = points

        self.program = program
        self.ctx = scene.ctx
        self.vbo = self.createVbo()

    def color(self):
        return self._color

    def setColor(self, color: str):
        self._color = color

    def points(self):
        return self._points

    def setPoints(self, points: list[tuple[float, float, float]]):
        self._points = points

    def createVbo(self):
        array = []

        for point in self.points():
            array.extend([point[0] / 100, point[1] / 100, point[2] / 100])

        vertices = np.array(array, dtype='f4')

        vbo = self.ctx.buffer(vertices)
        return vbo

    def render(self):
        super().render()

        # Use the shader program and draw
        self.program['model'].write(np.eye(4, dtype='f4').tobytes())
        self.program['color'].value = self.color()
        self.program['alphaValue'].value = 1.0

        vao = self.ctx.simple_vertex_array(self.program, self.vbo, 'in_vert')
        vao.render(POINTS)

