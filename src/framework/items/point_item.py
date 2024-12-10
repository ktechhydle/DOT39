from src._imports import *
from src.framework.items.base_item import *
from src.framework.scene.functions import hexToRGB


class PointItem(BaseItem):
    def __init__(self, scene, program, pos: list[float]):
        super().__init__(scene)
        self.setPos(pos)
        self._color = hexToRGB('#ff0000')

        self.program = program
        self.ctx = scene.ctx
        self.vbo = self.createVbo()

    def color(self):
        return self._color

    def setColor(self, color: str):
        self._color = color

    def createVbo(self):
        # Create a VBO that defines the vertices for the `+` shape
        vertices = np.array([
            # Horizontal line
            -0.1, 0.0, 0.0,
            0.1, 0.0, 0.0,
            # Vertical line
            0.0, -0.1, 0.0,
            0.0, 0.1, 0.0,
        ], dtype='f4')

        vbo = self.ctx.buffer(vertices)
        return vbo

    def render(self):
        super().render()

        # Use the shader program and draw
        self.program['model'].write(np.eye(4, dtype='f4').tobytes())
        self.program['color'].value = self.color()
        self.program['alphaValue'].value = 1.0

        vao = self.ctx.simple_vertex_array(self.program, self.vbo, 'in_vert')
        vao.render(LINES)

