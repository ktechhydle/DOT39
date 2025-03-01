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
        # Get the current position (previous point)
        prev_point = self._horizontal_path.currentPosition()
        prev_x, prev_y = prev_point.x(), prev_point.y()

        # Calculate the direction vectors (tangent directions) for the line from the previous point to the target point
        dx = to_x - prev_x
        dy = to_y - prev_y

        # Calculate the normal vector of the line (perpendicular to the direction of the line)
        normal_length = math.sqrt(dx ** 2 + dy ** 2)
        normal_x = -dy / normal_length
        normal_y = dx / normal_length

        # You can control the curvature with this factor (the radius will be proportional to the curvature)
        curvature = 0.5  # This determines how "tight" the curve is. Increase for tighter curves, decrease for wider.

        # The center of the circle will be offset from the midpoint of the line by the normal vector scaled by the radius.
        radius = normal_length * curvature
        center_x = (prev_x + to_x) / 2 + normal_x * radius
        center_y = (prev_y + to_y) / 2 + normal_y * radius

        # Calculate the angle of the arc (we will assume it's a half-circle)
        start_angle = math.atan2(prev_y - center_y, prev_x - center_x)
        end_angle = math.atan2(to_y - center_y, to_x - center_x)

        # Ensure the angle goes around 360 degrees if necessary
        if end_angle < start_angle:
            end_angle += 2 * math.pi  # Wrap the end angle

        # Check whether to flip the curve based on the direction
        # If the normal vector points up, draw the curve to the left
        flip_curve = normal_x < 0

        # We can now create points along the arc
        num_points = 100  # Number of points to sample along the curve
        angle_step = (end_angle - start_angle) / num_points

        # Add the arc points to the path
        for i in range(num_points + 1):
            angle = start_angle + i * angle_step
            x = center_x + radius * math.cos(angle)

            # Flip the y-direction if necessary based on `flip_curve`
            if flip_curve:
                y = center_y + radius * math.sin(angle)  # Draw to the left
            else:
                y = center_y - radius * math.sin(angle)  # Draw to the right

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
