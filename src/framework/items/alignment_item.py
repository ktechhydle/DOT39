from src._imports import *
from src.errors.standard_error import DOT39StandardError
from src.framework.items.base_item import BaseItem
from src.framework.scene.functions import hexToRGB
from scipy.special import fresnel


class AlignmentItem(BaseItem):
    CurveTypeClothoid = 0
    CurveTypeCircular = 1

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

    def autoGenerateCurves(self, speed_mph: int, min_radius: float, max_radius: float, curve_type: int) -> QPainterPath:
        path = QPainterPath()

        elements = [self.coordAt(i) for i in range(self.horizontalPath().elementCount())]
        start_pos_x, start_pos_y = elements[0][0], elements[0][1]

        path.moveTo(start_pos_x, start_pos_y)

        for i in range(1, len(elements)):
            x1, y1 = elements[i - 1]
            x2, y2 = elements[i]

            if curve_type == AlignmentItem.CurveTypeClothoid:
                pass

            elif curve_type == AlignmentItem.CurveTypeCircular:
                pass

        return path
