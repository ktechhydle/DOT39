from src._imports import *
from src.errors.standard_error import DOT39StandardError
from src.framework.items.base_item import BaseItem
from src.framework.items.point_item import PointItem
from src.framework.scene.functions import hexToRGB
from scipy.spatial import Delaunay


class TerrainItem(BaseItem):
    def __init__(self, scene, program, points: list[tuple[float, float, float]] = [(0.0, 0.0, 0.0)], name=''):
        super().__init__(scene, name)
        self.setColor(hexToRGB('#00ff00'))
        self._points = points

        self.program = program
        self.ctx = scene.ctx
        self.vbo = self.createVbo()

        # Prepare Delaunay triangulation
        self._points_np = np.array(self._points, dtype='f4')
        self._points_2d = self._points_np[:, :2]
        self.tri = Delaunay(self._points_2d)

    def points(self):
        return self._points

    def fromPointItems(self, point_items: list[PointItem]):
        points = []

        for item in point_items:
            points.append((item.x(), item.y(), item.z()))

        self.setPoints(points)

    def setPoints(self, points: list[tuple[float, float, float]]):
        self._points = points

        self.update()

    def getElevationAt(self, x, y):
        # Find the simplex (triangle) containing the point (x, y)
        simplex = self.tri.find_simplex([x, y])

        if simplex == -1:
            return None

        # Get the indices of the vertices of the triangle
        triangle_vertices = self.tri.simplices[simplex]

        # Extract the 3 points of the triangle
        p0, p1, p2 = self._points_np[triangle_vertices]

        # Calculate the barycentric coordinates (lambda1, lambda2, lambda3) of the point (x, y) within the triangle
        # These are calculated using the inverse of the matrix formed by the triangle's points and the point (x, y)
        denom = (p1[1] - p2[1]) * (p0[0] - p2[0]) + (p2[0] - p1[0]) * (p0[1] - p2[1])
        if denom == 0:
            return None

        lambda1 = ((p1[1] - p2[1]) * (x - p2[0]) + (p2[0] - p1[0]) * (y - p2[1])) / denom
        lambda2 = ((p2[1] - p0[1]) * (x - p2[0]) + (p0[0] - p2[0]) * (y - p2[1])) / denom
        lambda3 = 1 - lambda1 - lambda2

        # Calculate the elevation (z-value) using the barycentric coordinates
        elevation = lambda1 * p0[2] + lambda2 * p1[2] + lambda3 * p2[2]

        return elevation

    def createVbo(self):
        if len(self.points()) < 3:
            raise DOT39StandardError('Not enough points to create a surface (minimum of 3 required)')

        # Convert points to a numpy array
        points = np.array(self.points(), dtype='f4')
        points_2d = points[:, :2]

        tri = Delaunay(points_2d)
        triangles = points[tri.simplices]
        vertices = triangles.reshape(-1, 3).astype('f4')

        # Create the VBO
        return self.ctx.buffer(vertices.tobytes())

    def render(self, color=None):
        super().render()

        if color:
            self.program['color'].value = (color[0], color[1], color[2])
            self.program['alphaValue'].value = color[3]

        else:
            current_color = self.color()
            if self.isSelected():
                self.program['color'].value = hexToRGB('#007fff')

            elif self.isHovered():
                self.program['color'].value = hexToRGB('#0058b2')

            else:
                self.program['color'].value = current_color

        self.ctx.simple_vertex_array(self.program, self.vbo, 'in_vert').render(GL.TRIANGLES)

    def update(self):
        self._points_np = np.array(self._points, dtype='f4')
        self._points_2d = self._points_np[:, :2]
        self.tri = Delaunay(self._points_2d)
        self.vbo = self.createVbo()
