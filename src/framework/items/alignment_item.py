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
        self._vertical_path = QPainterPath()
        self._draw_calls = []
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

                    if not self._vertical_path.isEmpty():
                        for pg in self._vertical_path.toSubpathPolygons():
                            for p in pg:
                                vertices.append(p.y())
                    else:
                        vertices.append(0)

            return self.ctx.buffer(np.array(vertices, dtype='f4'))

        return None

    def drawCircularCurve(self, to_x, to_y, segments=50):
        # Get the previous point
        prev_point = self._horizontal_path.currentPosition()
        x1, y1 = prev_point.x(), prev_point.y()

        # Compute the midpoint
        mid_x, mid_y = (x1 + to_x) / 2, (y1 + to_y) / 2

        # Compute the perpendicular bisector's normal vector
        dx, dy = to_x - x1, to_y - y1
        normal_x, normal_y = -dy, dx

        # Estimate a simple arc center by offsetting the midpoint
        center_x, center_y = mid_x + normal_x * 0.5, mid_y + normal_y * 0.5
        radius = np.hypot(x1 - center_x, y1 - center_y)

        # Compute start and end angles
        start_angle = np.degrees(np.arctan2(y1 - center_y, x1 - center_x))
        end_angle = np.degrees(np.arctan2(to_y - center_y, to_x - center_x))

        # Ensure proper angle direction
        if end_angle < start_angle:
            end_angle += 360

        angles = np.linspace(np.radians(start_angle), np.radians(end_angle), segments)

        # Draw the curve
        for theta in angles:
            x = center_x + radius * np.cos(theta)
            y = center_y + radius * np.sin(theta)
            self._horizontal_path.lineTo(x, y)

        self.update()

    def drawClothoid(self, to_x, to_y, num_points=100, a=1.0):
        p1 = self._horizontal_path.currentPosition()
        x0, y0 = p1.x(), p1.y()

        dx = to_x - x0
        dy = to_y - y0
        distance = math.hypot(dx, dy)
        theta = math.atan2(dy, dx)

        t_values = np.linspace(0, 1, num_points)

        for t in t_values:
            # Compute Fresnel integrals for clothoid
            S, C = fresnel(a * t)

            # Transform clothoid points to global coordinates
            x = x0 + distance * (C * np.cos(theta) + S * np.sin(theta))
            y = y0 + distance * (C * np.sin(theta) - S * np.cos(theta))

            self._horizontal_path.lineTo(x, y)

        self.update()

    def drawLine(self, to_x, to_y):
        self._horizontal_path.lineTo(to_x, to_y)
        self._draw_calls.append({'Line': (to_x, to_y)})

        self.update()

    def drawStart(self, x, y):
        self._horizontal_path.moveTo(x, y)
        self._draw_calls.append({'Start Position': (x, y)})

        self.update()

    def coordAt(self, i):
        return 0, 0

    def drawCalls(self) -> list[dict[str, tuple]]:
        return self._draw_calls

    def setDrawCalls(self, calls: list[dict[str, tuple]]):
        self._draw_calls = calls

    def clearHorizontalPath(self):
        self._horizontal_path.clear()
        self._draw_calls = []

        self.update()

    def clearVerticalPath(self):
        self._vertical_path.clear()

        self.update()

    def setHorizontalPath(self, path: QPainterPath):
        self._horizontal_path = path

        self.update()

    def setVerticalPath(self, path: QPainterPath):
        self._vertical_path = path

        self.update()

    def horizontalPath(self):
        return self._horizontal_path

    def verticalPath(self):
        return self._vertical_path

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
