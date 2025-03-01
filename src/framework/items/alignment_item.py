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
                    vertices.append(0)

            return self.ctx.buffer(np.array(vertices, dtype='f4'))

        return None

    def drawCircularCurve(self, to_x, to_y):
        prev_point = self._horizontal_path.currentPosition()
        prev_x, prev_y = prev_point.x(), prev_point.y()

        dx = to_x - prev_x
        dy = to_y - prev_y
        distance = math.hypot(dx, dy)
        if distance == 0:
            return  # No movement needed

        # Flip the normal vector direction to invert the curve
        normal_x = dy / distance  # Previously: -dy / distance
        normal_y = -dx / distance  # Previously: dx / distance

        curvature = 0.5  # Adjust curvature (0 < curvature < 1)

        # Calculate offset (h) and radius
        h = curvature * distance
        radius = math.sqrt((distance / 2) ** 2 + h ** 2)

        # Midpoint between prev and to points
        mid_x = (prev_x + to_x) / 2
        mid_y = (prev_y + to_y) / 2

        # Center of the circle (offset by flipped normal)
        center_x = mid_x + normal_x * h
        center_y = mid_y + normal_y * h

        # Start and end angles
        start_angle = math.atan2(prev_y - center_y, prev_x - center_x)
        end_angle = math.atan2(to_y - center_y, to_x - center_x)

        # Determine sweep direction (clockwise for inverted y-axis)
        angle_diff = end_angle - start_angle
        if angle_diff > 0:
            angle_diff -= 2 * math.pi  # Force clockwise sweep

        num_points = 100
        angle_step = angle_diff / num_points

        for i in range(num_points + 1):
            angle = start_angle + i * angle_step
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            self._horizontal_path.lineTo(x, y)

        self._draw_calls.append({'Circular Curve': (to_x, to_y)})
        self.update()

    def drawLine(self, to_x, to_y):
        self._horizontal_path.lineTo(to_x, to_y)
        self._draw_calls.append({'Line': (to_x, to_y)})

        self.update()

    def drawStart(self, x, y):
        self._horizontal_path.moveTo(x, y)
        self._draw_calls.append({'Start Position': (x, y)})

        self.update()

    def drawCalls(self) -> list[dict[str, tuple]]:
        return self._draw_calls

    def setDrawCalls(self, calls: list[dict[str, tuple]]):
        self._draw_calls = calls

    def clearHorizontalPath(self):
        self._horizontal_path.clear()
        self._draw_calls = []

        self.update()

    def setHorizontalPath(self, path: QPainterPath):
        self._horizontal_path = path

        self.update()

    def horizontalPath(self):
        return self._horizontal_path

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
