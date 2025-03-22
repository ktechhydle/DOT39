from src._imports import *
from src.errors.standard_error import DOT39StandardError
from src.framework.items.base_item import BaseItem
from src.framework.scene.functions import hexToRGB
from scipy.special import fresnel


class AlignmentHorizontalPath(QPainterPath):
    StartPos = 'start_pos'
    Line = 'line'
    CircularCurve = 'circular_curve'
    ClothoidCurve = 'clothoid_curve'

    def __init__(self):
        super().__init__()

        self._segments = []

    def moveTo(self, x, y):
        self._segments.append((AlignmentHorizontalPath.StartPos, x, y))

        super().moveTo(x, y)

    def lineTo(self, x, y, ignore=False):
        if not ignore:
            self._segments.append((AlignmentHorizontalPath.Line, x, y))

        super().lineTo(x, y)

    def circularCurveTo(self, start: tuple[float, float], end: tuple[float, float], pi: tuple[float, float], radius: float):
        self._segments.append((AlignmentHorizontalPath.CircularCurve, start, end, pi, radius))

        cx, cy = pi
        sx, sy = start
        ex, ey = end

        theta1 = np.arctan2(sy - cy, sx - cx)
        theta2 = np.arctan2(ey - cy, ex - cx)

        if theta1 > theta2:
            theta1, theta2 = theta2, theta1

        num_points = 100
        theta_vals = np.linspace(theta1, theta2, num_points)
        points = [(cx + radius * np.cos(theta), cy + radius * np.sin(theta)) for theta in theta_vals]

        for px, py in points:
            self.lineTo(px, py, ignore=True)

    def clothoidCurveTo(self, x1, y1, theta1, length, A):
        self._segments.append((AlignmentHorizontalPath.ClothoidCurve, x1, y1, theta1, length, A))

        num_points = 100
        t = np.linspace(0, length / A, num_points)

        S, C = fresnel(t)
        X = A * np.sqrt(np.pi) * C
        Y = A * np.sqrt(np.pi) * S

        cos_theta, sin_theta = np.cos(theta1), np.sin(theta1)
        points = [(x1 + cos_theta * x - sin_theta * y,
                   y1 + sin_theta * x + cos_theta * y) for x, y in zip(X, Y)]

        # Draw curve using line segments
        for px, py in points:
            self.lineTo(px, py, ignore=True)

    def modifyElement(self, index, new_params):
        if 0 <= index < len(self._segments):
            segment_type, _ = self._segments[index]

            if segment_type == AlignmentHorizontalPath.StartPos:
                self._segments[index] = (AlignmentHorizontalPath.StartPos, new_params)

            elif segment_type == AlignmentHorizontalPath.Line:
                self._segments[index] = (AlignmentHorizontalPath.Line, new_params)

            elif segment_type == AlignmentHorizontalPath.ClothoidCurve:
                self._segments[index] = (AlignmentHorizontalPath.ClothoidCurve, new_params)

            elif segment_type == AlignmentHorizontalPath.CircularCurve:
                self._segments[index] = (AlignmentHorizontalPath.CircularCurve, new_params)

            self.rebuild()

    def rebuild(self):
        self.clear()

        for segment in self._segments:
            if segment[0] == AlignmentHorizontalPath.StartPos:
                _, (x, y) = segment
                self.moveTo(x, y)

            elif segment[0] == AlignmentHorizontalPath.Line:
                _, (x, y) = segment
                self.lineTo(x, y)

            elif segment[0] == AlignmentHorizontalPath.CircularCurve:
                _, cx, cy, r, start, end = segment
                self.circularCurveTo(cx, cy, r, start, end)

            elif segment[0] == AlignmentHorizontalPath.ClothoidCurve:
                _, x1, y1, theta1, length, A = segment
                self.clothoidCurveTo(x1, y1, theta1, length, A)

    def segmentCount(self) -> int:
        return len(self._segments)


class AlignmentItem(BaseItem):
    CurveTypeClothoid = 0
    CurveTypeCircular = 1

    def __init__(self, scene, program, name=''):
        super().__init__(scene, name)
        self.setColor(hexToRGB('#ff0000'))

        self.program = program
        self.ctx = scene.ctx
        self._horizontal_path = AlignmentHorizontalPath()
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

    def drawLine(self, to_x, to_y):
        self._horizontal_path.lineTo(to_x, to_y)
        self._draw_calls.append({'Line': (to_x, to_y)})

        self.update()

    def drawStart(self, x, y):
        self._horizontal_path.moveTo(x, y)
        self._draw_calls.append({'Start Position': (x, y)})

        self.update()

    def coordAt(self, i):
        if i < 0 or i >= self._horizontal_path.elementCount():
            return None

            # Get the element at index i
        element = self._horizontal_path.elementAt(i)

        # Return the x and y coordinates
        return element.x, element.y

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

    def autoGenerateCurves(self, speed_mph: int, curve_type: int) -> AlignmentHorizontalPath:
        path = AlignmentHorizontalPath()
        points = [(seg[1], seg[2]) for seg in self._horizontal_path._segments if
                  seg[0] in [AlignmentHorizontalPath.StartPos, AlignmentHorizontalPath.Line]]

        e = 0.10 - (0.001 * speed_mph)  # superelevation factor
        f = 0.35 - (0.0033 * speed_mph)  # side friction factor
        min_arc_radius = (speed_mph ** 2) / (15 * (e + f))
        min_clothoid_length = (speed_mph ** 3) / (46.5 * (e + f))

        path.moveTo(*points[0])

        for i in range(1, len(points) - 1):
            x1, y1 = points[i - 1]
            x2, y2 = points[i]
            x3, y3 = points[i + 1]

            angle1 = np.arctan2(y2 - y1, x2 - x1)
            angle2 = np.arctan2(y3 - y2, x3 - x2)
            delta_angle = np.degrees(angle2 - angle1)
            delta_angle = (delta_angle + 180) % 360 - 180

            if abs(delta_angle) > 0.001:
                if curve_type == AlignmentItem.CurveTypeCircular:
                    # path.circularCurveTo()
                    pass

                elif curve_type == AlignmentItem.CurveTypeClothoid:
                    # path.clothoidCurveTo()
                    pass

            else:
                path.lineTo(x2, y2)

        path.lineTo(*points[-1])
        return path
