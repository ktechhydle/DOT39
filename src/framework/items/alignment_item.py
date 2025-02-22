from src._imports import *
from src.errors.standard_error import DOT39StandardError
from src.framework.items.base_item import BaseItem
from src.framework.scene.functions import hexToRGB
from scipy.special import fresnel


class AlignmentItem(BaseItem):
    def __init__(self, scene, program, name=''):
        super().__init__(scene, name)
        self.setColor(hexToRGB('#ff0000'))

        self.program = program
        self.ctx = scene.ctx
        self._horizontal_path = QPainterPath()
        self.vbo = self.createVbo()

    def createVbo(self):
        if not self._horizontal_path.isEmpty():
            polygons = self._horizontal_path.toSubpathPolygons()

            # Extract vertex data
            vertices = []
            for polygon in polygons:
                for point in polygon:
                    vertices.append(point.x())
                    vertices.append(point.y())
                    vertices.append(0)

            return self.ctx.buffer(np.array(vertices, dtype='f4'))

        return None

    def drawCircularCurve(self, center, radius, start_angle, end_angle, segments=50):
        x_c, y_c = center
        angles = np.linspace(np.radians(start_angle), np.radians(end_angle), segments)

        for theta in angles:
            x = x_c + radius * np.cos(theta)
            y = y_c + radius * np.sin(theta)
            self._horizontal_path.lineTo(x, y)

        self.update()

    def drawReverseCurve(self, center1, radius1, start_angle1, end_angle1, center2, radius2, start_angle2,
                         end_angle2, segments=50):
        self.drawCircularCurve(center1, radius1, start_angle1, end_angle1, segments)
        self.drawCircularCurve(center2, radius2, start_angle2, end_angle2, segments)

    def drawSpiralCurve(self, start, length, A, segments=50):
        x0, y0 = start
        t_vals = np.linspace(0, length / A, segments)

        for t in t_vals:
            S, C = fresnel(t)
            x = x0 + A * C
            y = y0 + A * S
            self._horizontal_path.lineTo(x, y)

        self.update()

    def drawLine(self, to_x, to_y):
        self._horizontal_path.lineTo(to_x, to_y)

        self.update()

    def drawStart(self, x, y):
        self._horizontal_path.moveTo(x, y)

        self.update()

    def clearHorizontalPath(self):
        self._horizontal_path.clear()
        self.update()

    def render(self, color=None):
        super().render()

        if color:
            self.program['color'].value = (color[0], color[1], color[2])
            self.program['alphaValue'].value = color[3]

        else:
            # Render points
            current_color = self.color()
            if self.isSelected():
                self.program['color'].value = hexToRGB('#007fff')

            elif self.isHovered():
                self.program['color'].value = hexToRGB('#0058b2')

            else:
                self.program['color'].value = current_color

        if self.vbo:
            vao = self.ctx.simple_vertex_array(self.program, self.vbo, 'in_vert')
            vao.render(GL.LINE_STRIP)

    def update(self):
        self.vbo = self.createVbo()
