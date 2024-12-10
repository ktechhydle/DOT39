from src._imports import *
from src.framework.items.base_item import *
from src.framework.scene.functions import hexToRGB


class PointItem(BaseItem):
    def __init__(self, scene, pos: list[float]):
        super().__init__(scene)
        self.setPos(pos)
        self._color = hexToRGB('#ff0000')

        self.ctx = scene.ctx
        self.shader = self.createShader()
        self.vbo = self.createVbo()

    def color(self):
        return self._color

    def setColor(self, color: str):
        self._color = color

    def createShader(self):
        vertex_shader = '''
                #version 330
                in vec2 in_vert;
                uniform mat4 model;
                void main() {
                    gl_Position = model * vec4(in_vert, 0.0, 1.0);
                }
                '''

        fragment_shader = '''
                #version 330
                out vec4 fragColor;
                uniform vec3 color;
                void main() {
                    fragColor = vec4(color, 1.0);
                }
                '''

        return self.ctx.program(
            vertex_shader=vertex_shader,
            fragment_shader=fragment_shader
        )

    def createVbo(self):
        # Create a VBO that defines the vertices for the `+` shape
        vertices = np.array([
            # Horizontal line
            -0.1, 0.0,
            0.1, 0.0,
            # Vertical line
            0.0, -0.1,
            0.0, 0.1,
        ], dtype='f4')

        vbo = self.ctx.buffer(vertices)
        return vbo

    def render(self):
        super().render()
        
        # Use the shader program and draw
        self.shader['model'].write(np.eye(4, dtype='f4').tobytes())
        self.shader['color'].value = self.color()

        vao = self.ctx.simple_vertex_array(self.shader, self.vbo, 'in_vert')
        vao.render(LINES)

