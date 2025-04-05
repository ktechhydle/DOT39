from src._imports import *
from src.framework.items.base_item import *
from src.framework.scene.functions import hexToRGB
from itertools import chain


class AxisItem(BaseItem):
    XAxis = 0
    YAxis = 1
    ZAxis = 2

    def __init__(self, scene):
        super().__init__(scene, '')
        self.setSelectable(False)

        self.ctx = scene.ctx
        self.program = scene.program
        self._x_vbo = self.createXVbo()
        self._y_vbo = self.createYVbo()
        self._z_vbo = self.createZVbo()
        self._x_text_vbo = self.createTextVbo('x', AxisItem.XAxis)
        self._y_text_vbo = self.createTextVbo('y', AxisItem.YAxis)
        self._z_text_vbo = self.createTextVbo('z', AxisItem.ZAxis)

    def createXVbo(self):
        vertices = [
            100.0, 0.0, 0.0,
            -10.0, 0.0, 0.0
        ]

        return self.ctx.buffer(np.array(vertices, dtype='f4'))

    def createYVbo(self):
        vertices = [
            0.0, 100.0, 0.0,
            0.0, -10.0, 0.0
        ]

        return self.ctx.buffer(np.array(vertices, dtype='f4'))

    def createZVbo(self):
        vertices = [
            0.0, 0.0, 100.0,
            0.0, 0.0, -10.0
        ]

        return self.ctx.buffer(np.array(vertices, dtype='f4'))

    def createTextVbo(self, text: str, axis: int):
        font = QFont('Arial', 8)

        path = QPainterPath()
        path.addText(QPointF(0, 0), font, text)

        # Convert the path to polygons
        polygons = path.toSubpathPolygons()

        # Extract vertex data
        vertices = []
        for polygon in polygons:
            for point in polygon:
                if axis == AxisItem.XAxis:
                    vertices.extend([point.x() - 7, -point.y() + 1, 0])

                elif axis == AxisItem.YAxis:
                    vertices.extend([point.x() + 1, -point.y() - 7, 0])

                elif axis == AxisItem.ZAxis:
                    vertices.extend([-point.x() - 1, 0, point.y() - 1])

            # Add a break in the drawing sequence
            vertices.append(float('nan'))
            vertices.append(float('nan'))
            vertices.append(float('nan'))

        return self.ctx.buffer(np.array(vertices, dtype='f4'))

    def render(self, color=None):
        super().render()

        og = self.ctx.line_width
        self.ctx.line_width = 1.5

        self.program['color'].value = hexToRGB('#fe2e4e')
        self.ctx.simple_vertex_array(self.program, self._x_vbo, 'in_vert').render(GL.LINES)

        self.program['color'].value = hexToRGB('#399e19')
        self.ctx.simple_vertex_array(self.program, self._y_vbo, 'in_vert').render(GL.LINES)

        self.program['color'].value = hexToRGB('#2883ef')
        self.ctx.simple_vertex_array(self.program, self._z_vbo, 'in_vert').render(GL.LINES)

        self.ctx.line_width = 1.25
        self.program['color'].value = hexToRGB('#ffffff')
        self.ctx.simple_vertex_array(self.program, self._x_text_vbo, 'in_vert').render(GL.LINE_LOOP)
        self.ctx.simple_vertex_array(self.program, self._y_text_vbo, 'in_vert').render(GL.LINE_LOOP)
        self.ctx.simple_vertex_array(self.program, self._z_text_vbo, 'in_vert').render(GL.LINE_LOOP)

        self.ctx.line_width = og

    def update(self):
        self._x_vbo = self.createXVbo()
        self._y_vbo = self.createYVbo()
        self._z_vbo = self.createZVbo()
        self._x_text_vbo = self.createTextVbo('X', AxisItem.XAxis)
        self._y_text_vbo = self.createTextVbo('Y', AxisItem.YAxis)
        self._z_text_vbo = self.createTextVbo('Z', AxisItem.ZAxis)
