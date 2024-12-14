from src._imports import *
from src.framework.items.base_item import *
from src.framework.scene.functions import hexToRGB


class PointItem(BaseItem):
    def __init__(self, scene, program: GL.Program, number, pos: list[float] = [0.0, 0.0, 0.0], name=''):
        super().__init__(scene, name)
        self.setPos(pos)
        self._color = hexToRGB('#ff0000')
        self._point_num = number

        self.program = program
        self.ctx = scene.ctx
        self.vbo = self.createVbo()
        self.ibo = self.createIbo()

    def color(self):
        return self._color

    def pointNumber(self):
        return self._point_num

    def setColor(self, color: str):
        self._color = color

    def createVbo(self):
        # Create a VBO that defines the vertices for the `+` shape
        vertices = np.array([
            # Horizontal line
            -0.01 + self.x(), 0.0 + self.y(), 0.0 + self.z(),
            0.01 + self.x(), 0.0 + self.y(), 0.0 + self.z(),
            # Vertical line
            0.0 + self.x(), -0.01 + self.y(), 0.0 + self.z(),
            0.0 + self.x(), 0.01 + self.y(), 0.0 + self.z(),
        ], dtype='f4')

        vbo = self.ctx.buffer(vertices)
        return vbo

    def createIbo(self):
        # Create a IBO that defines the indices for the `+` shape
        indices = np.array([
            0, 1,  # Horizontal line
            2, 3  # Vertical line
        ], dtype='i4')

        ibo = self.ctx.buffer(indices)
        return ibo

    def render(self):
        super().render()

        # Use the shader program and draw
        self.program['color'].value = self.color()

        vao = self.ctx.simple_vertex_array(self.program, self.vbo, 'in_vert', index_buffer=self.ibo)
        vao.render(GL.LINES)

