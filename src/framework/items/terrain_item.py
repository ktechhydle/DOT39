from src._imports import *
from src.framework.items.base_item import BaseItem
from src.framework.items.point_item import PointItem
from src.framework.scene.functions import hexToRGB
from scipy.spatial import ConvexHull


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
            return None  # Not enough points for an outline

        points_3d = np.array([(p[0], p[1], p[2]) for p in self.points()])
        hull = ConvexHull(points_3d)
        edges = []

        # Add edges of the convex hull
        for simplex in hull.simplices:
            edges.append(points_3d[simplex[0]])  # First point
            edges.append(points_3d[simplex[1]])  # Second point
            edges.append(points_3d[simplex[1]])  # Second point
            edges.append(points_3d[simplex[2]])  # Third point
            edges.append(points_3d[simplex[2]])  # Third point
            edges.append(points_3d[simplex[0]])  # First point

        # Flatten and scale
        edges_flat = []
        for edge in edges:
            edges_flat.extend([edge[0], edge[1], edge[2]])

        vertices = np.array(edges_flat, dtype='f4')
        vbo = self.ctx.buffer(vertices)
        return vbo

    def render(self):
        super().render()

        if self.outline_vbo:
            # Render points
            self.program['color'].value = self.outlineColor()  # Outline color
            outline_vao = self.ctx.simple_vertex_array(self.program, self.outline_vbo, 'in_vert')
            outline_vao.render(GL.LINES)

