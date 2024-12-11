from src._imports import *
from src.framework.items.base_item import *
from src.framework.scene.functions import hexToRGB
from scipy.spatial import ConvexHull


class TerrainItem(BaseItem):
    def __init__(self, scene, program, points: list[tuple[float, float, float]]):
        super().__init__(scene)
        self._color = hexToRGB('#00ff00')
        self._outline_color = hexToRGB('#00ff00')
        self._points = points

        self.program = program
        self.ctx = scene.ctx
        self.vbo = self.createVbo()
        self.outline_vbo = self.createOutlineVbo()  # Add outline VBO

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

    def setPoints(self, points: list[tuple[float, float, float]]):
        self._points = points
        self.vbo = self.createVbo()
        self.outline_vbo = self.createOutlineVbo()  # Update outline VBO

    def createVbo(self):
        array = []

        for point in self.points():
            array.extend([point[0] / 100, point[1] / 100, point[2] / 100])

        vertices = np.array(array, dtype='f4')
        vbo = self.ctx.buffer(vertices)
        return vbo

    def createOutlineVbo(self):
        if len(self.points()) < 3:
            return None  # Not enough points for an outline

        points_2d = np.array([(p[0], p[1]) for p in self.points()])
        hull = ConvexHull(points_2d)
        edges = []

        # Add edges of the convex hull
        for simplex in hull.simplices:
            edges.extend([points_2d[simplex[0]], points_2d[simplex[1]]])

        # Flatten and scale
        edges_flat = []
        for edge in edges:
            edges_flat.extend([edge[0] / 100, edge[1] / 100, 0.0])  # Assume z=0 for outline

        vertices = np.array(edges_flat, dtype='f4')
        vbo = self.ctx.buffer(vertices)
        return vbo

    def render(self):
        super().render()

        # Render points
        self.program['color'].value = self.color()

        vao = self.ctx.simple_vertex_array(self.program, self.vbo, 'in_vert')
        vao.render(GL.POINTS)

        # Render outline
        if self.outline_vbo:
            self.program['color'].value = self.outlineColor()  # Outline color
            outline_vao = self.ctx.simple_vertex_array(self.program, self.outline_vbo, 'in_vert')
            outline_vao.render(GL.LINES)

