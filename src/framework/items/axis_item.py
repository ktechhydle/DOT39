from src._imports import *
from src.framework.items.base_item import *
from src.framework.scene.functions import hexToRGB


class AxisItem(BaseItem):
    def __init__(self, scene, program: GL.Program):
        super().__init__(scene, '')
        self.program = program
        self.ctx = scene.ctx
        self._x_vbo = self.createXVbo()
        self._y_vbo = self.createYVbo()
        self._z_vbo = self.createZVbo()

    def createXVbo(self):
        vertices = [
            10000.0, 0.0, 0.0,
            -10.0, 0.0, 0.0
        ]

        return self.ctx.buffer(np.array(vertices, dtype='f4'))

    def createYVbo(self):
        vertices = [
            0.0, 10000.0, 0.0,
            0.0, -10.0, 0.0
        ]

        return self.ctx.buffer(np.array(vertices, dtype='f4'))

    def createZVbo(self):
        vertices = [
            0.0, 0.0, 10000.0,
            0.0, 0.0, -10.0
        ]

        return self.ctx.buffer(np.array(vertices, dtype='f4'))

    def render(self, color=None):
        super().render()

        og = self.ctx.line_width
        self.ctx.line_width = 1.0

        self.program['color'].value = hexToRGB('#fe2e4e')
        self.ctx.simple_vertex_array(self.program, self._x_vbo, 'in_vert').render(GL.LINES)

        self.program['color'].value = hexToRGB('#399e19')
        self.ctx.simple_vertex_array(self.program, self._y_vbo, 'in_vert').render(GL.LINES)

        self.program['color'].value = hexToRGB('#2883ef')
        self.ctx.simple_vertex_array(self.program, self._z_vbo, 'in_vert').render(GL.LINES)

        self.ctx.line_width = og

    def update(self):
        self._x_vbo = self.createXVbo()
        self._y_vbo = self.createYVbo()
        self._z_vbo = self.createZVbo()
