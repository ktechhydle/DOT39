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
            raise DOT39StandardError('Not enough points to create a surface (minimum of 3 required)')

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

        else:
            # Render points
            current_color = self.color()
            if self.isSelected():
                self.program['color'].value = hexToRGB('#007fff')

            elif self.isHovered():
                self.program['color'].value = hexToRGB('#0058b2')

            else:
                self.program['color'].value = current_color

        outline_vao = self.ctx.simple_vertex_array(self.program, self.vbo, 'in_vert')
        outline_vao.render(GL.TRIANGLES)

    def update(self):
        self.vbo = self.createVbo()
