from src._imports import *
from src.framework.items.base_item import *
from src.framework.scene.functions import hexToRGB


class PointItem(BaseItem):
    def __init__(self, scene, number, pos: list[float] = [0.0, 0.0, 0.0], name=''):
        super().__init__(scene, name)
        self.setPos(pos)
        self.setColor(hexToRGB('#ff0000'))
        self._point_num = number

        self.ctx = scene.ctx
        self.program = scene.program
        self.vbo = self.createVbo()
        self.text_vbo = self.createTextVbo()
        self.ibo = self.createIbo()

    def pointNumber(self):
        return self._point_num

    def setPointNumber(self, value):
        self._point_num = value

    def createVbo(self):
        vertices = [
            # Horizontal line
            -1.0 + self.x(), 0.0 + self.y(), 0.0 + self.z(),
            1.0 + self.x(), 0.0 + self.y(), 0.0 + self.z(),
            # Vertical line
            0.0 + self.x(), -1.0 + self.y(), 0.0 + self.z(),
            0.0 + self.x(), 1.0 + self.y(), 0.0 + self.z(),
        ]

        return self.ctx.buffer(np.array(vertices, dtype='f4'))

    def createTextVbo(self):
        if self.name():
            font_id = QFontDatabase.addApplicationFont('resources/fonts/Simplex.ttf')
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            font = QFont(font_families[0], 10)

            path = QPainterPath()

            # Define the text with newlines
            lines = [
                f'{self.name()}',
                f'X: {self.x()}',
                f'Y: {self.y()}'
            ]

            # Set the starting point for the text
            current_position = QPointF(0, 0)

            # Loop over each line and add it at the appropriate position
            for line in lines:
                path.addText(current_position, font, line)
                # Adjust the current_position for the next line (move it down)
                current_position.setY(current_position.y() + font.pointSize() + 5)

            # Convert the path to polygons
            polygons = path.toSubpathPolygons()

            # Extract vertex data
            vertices = []
            for polygon in polygons:
                for point in polygon:
                    vertices.append((point.x() * 0.1) + (self.x() + 0.5))
                    vertices.append((-point.y() * 0.1) + (self.y() - 2))
                    vertices.append(100000)  # Letters only visible when facing top down

                # Add a break in the drawing sequence
                vertices.append(float('nan'))
                vertices.append(float('nan'))
                vertices.append(float('nan'))

            return self.ctx.buffer(np.array(vertices, dtype='f4'))

        return None

    def createIbo(self):
        indices = [
            0, 1,  # Horizontal line
            2, 3  # Vertical line
        ]

        return self.ctx.buffer(np.array(indices, dtype='i4'))

    def render(self, color=None):
        super().render()

        def set_color(color_value):
            self.program['color'].value = color_value[:3]
            self.program['alphaValue'].value = color_value[3]

        if color:
            set_color(color)
        else:
            current_color = self.color()
            if self.isSelected():
                self.program['color'].value = hexToRGB('#007fff')
            elif self.isHovered():
                self.program['color'].value = hexToRGB('#0058b2')
            else:
                self.program['color'].value = current_color

        self.ctx.simple_vertex_array(self.program, self.vbo, 'in_vert', index_buffer=self.ibo).render(GL.LINES)

        if self.text_vbo:
            if color:
                set_color(color)
            else:
                self.program['color'].value = hexToRGB('#007fff') if self.isSelected() else (
                    hexToRGB('#0058b2') if self.isHovered() else hexToRGB('#c800ff')
                )

            og = self.ctx.line_width
            self.ctx.line_width = 1.5

            self.ctx.simple_vertex_array(self.program, self.text_vbo, 'in_vert').render(GL.LINE_LOOP)

            self.ctx.line_width = og

    def update(self):
        self.vbo = self.createVbo()
        self.text_vbo = self.createTextVbo()
        self.ibo = self.createIbo()
