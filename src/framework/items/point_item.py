from src._imports import *
from src.framework.items.base_item import *
from src.framework.scene.functions import hexToRGB


class PointItem(BaseItem):
    def __init__(self, scene, program: GL.Program, number, pos: list[float] = [0.0, 0.0, 0.0], name=''):
        super().__init__(scene, name)
        self.setPos(pos)
        self.setColor(hexToRGB('#ff0000'))
        self._point_num = number

        self.program = program
        self.ctx = scene.ctx
        self.vbo = self.createVbo()
        self.text_vbo = self.createTextVbo()
        self.ibo = self.createIbo()

    def pointNumber(self):
        return self._point_num

    def setPointNumber(self, value):
        self._point_num = value

    def createVbo(self):
        # Create a VBO that defines the vertices for the `+` shape
        vertices = np.array([
            # Horizontal line
            -1.0 + self.x(), 0.0 + self.y(), 0.0 + self.z(),
            1.0 + self.x(), 0.0 + self.y(), 0.0 + self.z(),
            # Vertical line
            0.0 + self.x(), -1.0 + self.y(), 0.0 + self.z(),
            0.0 + self.x(), 1.0 + self.y(), 0.0 + self.z(),
        ], dtype='f4')

        vbo = self.ctx.buffer(vertices)
        return vbo

    def createTextVbo(self):
        if self.name():
            font_id = QFontDatabase.addApplicationFont('resources/fonts/Proxy 9.ttf')
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            font = QFont(font_families[0], 1)
            font.setLetterSpacing(QFont.AbsoluteSpacing, 0.5)
            path = QPainterPath()
            path.addText(QPointF(0, 0), font, self.name())

            # Convert the path to polygons
            polygons = path.toSubpathPolygons()

            # Extract vertex data
            vertices = []
            for polygon in polygons:
                for point in polygon:
                    vertices.append(point.x() + (self.x() + 0.5))
                    vertices.append(-point.y() + (self.y() - 2))
                    vertices.append(100000)  # Letters only visible when facing top down

                # Add a break in the drawing sequence
                vertices.append(float('nan'))
                vertices.append(float('nan'))
                vertices.append(float('nan'))

            return self.ctx.buffer(np.array(vertices, dtype='f4'))

        return None

    def createIbo(self):
        # Create a IBO that defines the indices for the `+` shape
        indices = np.array([
            0, 1,  # Horizontal line
            2, 3  # Vertical line
        ], dtype='i4')

        ibo = self.ctx.buffer(indices)
        return ibo

    def render(self, color=None):
        super().render()

        if color:
            self.program['color'].value = (color[0], color[1], color[2])
            self.program['alphaValue'].value = color[3]

        else:
            # Use the shader program and draw
            current_color = self.color()
            if self.isSelected():
                self.program['color'].value = hexToRGB('#007fff')

            elif self.isHovered():
                self.program['color'].value = hexToRGB('#0058b2')

            else:
                self.program['color'].value = current_color

        vao = self.ctx.simple_vertex_array(self.program, self.vbo, 'in_vert', index_buffer=self.ibo)
        vao.render(GL.LINES)

        # Render the text
        if self.text_vbo:
            text_vao = self.ctx.simple_vertex_array(self.program, self.text_vbo, 'in_vert')
            text_vao.render(GL.LINE_LOOP)

    def update(self):
        self.vbo = self.createVbo()
        self.text_vbo = self.createTextVbo()
        self.ibo = self.createIbo()
