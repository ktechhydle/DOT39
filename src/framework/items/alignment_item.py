from src._imports import *
from src.errors.standard_error import DOT39StandardError
from src.framework.items.base_item import BaseItem
from src.framework.scene.functions import hexToRGB
from scipy.special import fresnel


class AlignmentHorizontalPath(QPainterPath):
    StartPos = 'start_pos'
    Line = 'line'
    Fillet = 'fillet'

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

    def filletPoint(self, index: int, radius: float):
        pass

    def modifyElement(self, index, new_params):
        if 0 <= index < len(self._segments):
            segment_type, _ = self._segments[index]

            if segment_type == AlignmentHorizontalPath.StartPos:
                self._segments[index] = (AlignmentHorizontalPath.StartPos, new_params)

            elif segment_type == AlignmentHorizontalPath.Line:
                self._segments[index] = (AlignmentHorizontalPath.Line, new_params)

            elif segment_type == AlignmentHorizontalPath.Fillet:
                self._segments[index] = (AlignmentHorizontalPath.Fillet, new_params)

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

        for fillet in self._segments:
            if fillet[0] == AlignmentHorizontalPath.Fillet:
                _, (index, radius) = fillet
                self.filletPoint(index, radius)

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

    def generateFillets(self, speed_mph: int) -> AlignmentHorizontalPath:
        """
        Generates fillets at each point of the original alignment,
        by first generating a list of points (fillets included) than
        using lineTo() to construct a new path
        :param speed_mph: The speed in Miles Per Hour (mph)
        :return: AlignmentHorizontalPath
        """
        new_path = self.horizontalPath()
        points = [(seg[1], seg[2]) for seg in self._horizontal_path._segments if
                  seg[0] in [AlignmentHorizontalPath.StartPos, AlignmentHorizontalPath.Line]]

        e = 0.10 - (0.001 * speed_mph)  # superelevation factor
        f = 0.35 - (0.0033 * speed_mph)  # side friction factor
        min_fillet_radius = (speed_mph ** 2) / (15 * (e + f))
        new_path.moveTo(*points[0])

        for i in range(len(points)):
            # new_path.filletPoint(i, min_fillet_radius)
            pass

        return new_path
