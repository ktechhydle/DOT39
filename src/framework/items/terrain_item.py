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
        self.outline_vbo = self.createOutlineVbo()

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
            points.append((item.pos()[0], item.pos()[1], item.pos()[2]))

        self.setPoints(points)

    def setPoints(self, points: list[tuple[float, float, float]]):
        self._points = points
        self.outline_vbo = self.createOutlineVbo()

    def createOutlineVbo(self):
        if len(self.points()) < 3:
            return None  # Not enough points for triangulated mesh

            # Convert points to a numpy array
        points = np.array(self.points(), dtype='f4')

        # Use only the x, y coordinates for triangulation
        points_2d = points[:, :2]  # Assuming points have (x, y, z) format

        # Perform Delaunay triangulation
        tri = Delaunay(points_2d)

        # Extract triangle vertices
        triangles = points[tri.simplices]

        # Flatten the array for the VBO
        vertices = triangles.reshape(-1, 3).astype('f4')

        # Create the VBO
        vbo = self.ctx.buffer(vertices.tobytes())
        return vbo

    def render(self):
        super().render()

        if self.outline_vbo:
            # Render points
            self.program['color'].value = self.outlineColor()  # Outline color
            outline_vao = self.ctx.simple_vertex_array(self.program, self.outline_vbo, 'in_vert')
            outline_vao.render(GL.TRIANGLES)

