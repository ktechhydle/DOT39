import numpy as np

from src._imports import *
from src.framework.scene.arcball import ArcBallUtil


class Camera(object):
    def __init__(self, scene):
        self.scene = scene

        self._view_matrix = self.scene.program['matrix']
        self._arc_ball = ArcBallUtil(self.scene.width(), self.scene.height())
        self._center = np.zeros(3)
        self._scale = 1.0
        self._aspect_ratio = self.scene.width() / max(1.0, self.scene.height())
        self._camera_zoom = 1.0
        self._prev_x = 0
        self._prev_y = 0

    def update(self):
        """
        Updates the Camera matrix
        """
        self._aspect_ratio = self.scene.width() / max(1.0, self.scene.height())

        ortho_size = self._camera_zoom
        ortho_left = -self._aspect_ratio * ortho_size
        ortho_right = self._aspect_ratio * ortho_size
        ortho_bottom = -ortho_size
        ortho_top = ortho_size
        ortho_near = -10000.0
        ortho_far = 10000.0

        orthographic = Matrix44.orthogonal_projection(
            ortho_left, ortho_right, ortho_bottom, ortho_top, ortho_near, ortho_far
        )

        # View transformation
        lookat = Matrix44.look_at(
            (0.0, 0.0, self._aspect_ratio),
            (0.0, 0.0, 0.0),
            (0.0, 1.0, 0.0)
        )
        self._arc_ball.Transform[3, :3] = -self._arc_ball.Transform[:3, :3].T @ self._center
        self._view_matrix.write((orthographic * lookat * self._arc_ball.Transform).astype('f4'))

    def resize(self, w, h):
        self._arc_ball.setBounds(w, h)

    def reset(self):
        """
        Resets the Camera's view and bounding area
        """
        if self.scene.visibleItems():
            self._arc_ball = ArcBallUtil(self.scene.width(), self.scene.height())

            if self.scene.itemMeshPoints():
                mesh_points = self.scene.itemMeshPoints()
            else:
                # nothing on the scene, so we just use the axis item's bounding box
                mesh_points = [np.zeros(3), [100, 100, 100]]

            bounding_box_min = np.min(mesh_points, axis=0)
            bounding_box_max = np.max(mesh_points, axis=0)

            self._center = 0.5 * (bounding_box_max + bounding_box_min)
            self._scale = np.linalg.norm(bounding_box_max - self._center)
            self._arc_ball.Transform[:3, :3] /= self._scale
            self._arc_ball.Transform[3, :3] = -self._center / self._scale

            self._camera_zoom = 1.0

    def setAspectRatio(self, aspect_ratio: float):
        self._aspect_ratio = aspect_ratio

    def setCameraZoom(self, camera_zoom: float):
        self._camera_zoom = camera_zoom

    def aspectRatio(self) -> float:
        return self._aspect_ratio

    def cameraZoom(self) -> float:
        return self._camera_zoom

    def onOrbitStart(self, x, y):
        self._arc_ball.onClickLeftDown(x, y)

    def onOrbit(self, x, y):
        self._arc_ball.onDrag(x, y)

    def onOrbitEnd(self):
        self._arc_ball.onClickLeftUp()

    def onPanStart(self, x, y):
        self._prev_x = x
        self._prev_y = y

    def onPan(self, x, y):
        # Panning logic
        x_movement = x - self._prev_x
        y_movement = y - self._prev_y

        right = self._arc_ball.Transform[:3, 0]
        up = self._arc_ball.Transform[:3, 1]

        # Normalize the vectors
        right = right / np.linalg.norm(right)
        up = up / np.linalg.norm(up)

        movement = (x_movement * right - y_movement * up) * (self._camera_zoom * self._scale * 0.002)
        self._center -= movement

        self._prev_x = x
        self._prev_y = y

    def onZoom(self, event: QWheelEvent):
        zoom_delta = -event.angleDelta().y() * 0.001
        self._camera_zoom = max(0.1, self._camera_zoom + zoom_delta)