from src._imports import *
from src.framework.items.base_item import BaseItem
from src.framework.items.point_item import PointItem
from src.framework.scene.functions import hexToRGB
from scipy.spatial import Delaunay


class TerrainItem(BaseItem):
    def __init__(self, scene, program, points: list[tuple[float]] = [(0.0, 0.0, 0.0)], name=''):
        super().__init__(scene, name)
        self._color = hexToRGB('#00ff00')
        self._outline_color = hexToRGB('#00ff00')
        self._points = points

        self.program = program
        self.ctx = scene.ctx
        self.vbo = self.createVbo()

    def color(self):
        return self._color

    def outlineColor(self):
        return self._outline_color

    def setColor(self, color: str):
        self._color = color

    def setOutlineColor(self, color: str):
        self._outline_color = color

    def points(self):
        return self._points

    def fromPointItems(self, point_items: list[PointItem]):
        points = []

        for item in point_items:
            points.append((item.x(), item.y(), item.z()))

        self.setPoints(points)

    def setPoints(self, points: list[tuple[float, float, float]]):
        self._points = points
        self.vbo = self.createVbo()

    def createVbo(self):
        if len(self.points()) < 3:
            return None  # Not enough points for triangulated mesh

            # Convert points to a numpy array
        points = np.array(self.points(), dtype='f4')

        # Use only the x, y coordinates for triangulation
        points_2d = points[:, :2]

        # Perform Delaunay triangulation
        tri = Delaunay(points_2d)

        # Extract triangle vertices
        triangles = points[tri.simplices]

        # Flatten the array for the VBO
        vertices = triangles.reshape(-1, 3).astype('f4')

        # Create the VBO
        vbo = self.ctx.buffer(vertices.tobytes())
        return vbo

    def render(self, color=None):
        super().render()

        if color:
            self.program['color'].value = (color[0], color[1], color[2])
            self.program['alphaValue'].value = color[3]

            outline_vao = self.ctx.simple_vertex_array(self.program, self.vbo, 'in_vert')
            outline_vao.render(GL.TRIANGLES)

        else:
            # Render points
            current_color = self.outlineColor()
            if self.isSelected():
                # Invert the color
                inverted_color = tuple(1.0 - c for c in current_color)
                self.program['color'].value = inverted_color
            else:
                self.program['color'].value = current_color

            outline_vao = self.ctx.simple_vertex_array(self.program, self.vbo, 'in_vert')
            outline_vao.render(GL.TRIANGLES)

    def hover(self):
        self.program['alphaValue'].value = 0.75

        vao = self.ctx.simple_vertex_array(self.program, self.vbo, 'in_vert')
        vao.render(GL.LINES)

    def update(self):
        self.vbo = self.createVbo()

