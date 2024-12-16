from src._imports import *
from src.framework.items.base_item import BaseItem
from src.framework.items.point_group import PointGroupItem
from src.framework.items.point_item import PointItem
from src.framework.items.terrain_item import TerrainItem
from src.framework.scene.functions import hexToRGB, vertex_shad, fragment_shad
from src.framework.scene.arcball import ArcBallUtil
from src.framework.scene.undo_commands import *


class BaseScene(QGLWidget):
    def __init__(self, parent=None):
        super(BaseScene, self).__init__(parent)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.CrossCursor)

        self.undo_stack = QUndoStack(self)
        self.undo_stack.setUndoLimit(200)

        self.ctx = None
        self.program = None
        self.wireframe = True
        self.bg_color = hexToRGB('#000000')
        self.aspect_ratio = 1.0
        self.camera_zoom = 2.0

        self._items = []
        self._selected_items = []

    def initializeGL(self):
        self.ctx = GL.create_context()
        self.ctx.clear(*self.bg_color)
        self.ctx.enable(GL.DEPTH_TEST)
        self.ctx.wireframe = self.wireframe

        self.program = self.ctx.program(
            vertex_shader=vertex_shad,
            fragment_shader=fragment_shad
        )

        self.view_matrix = self.program['matrix']

        self.arc_ball = ArcBallUtil(self.width(), self.height())
        self.center = np.zeros(3)
        self.scale = 1.0

        # Console Info
        print('---- DOT39 Compiled Successfully ----\n---- OpenGL Attributes Initialized ----')
        print('OpenGL Version: ', self.ctx.version_code)

    def resizeGL(self, w, h):
        width = max(2, w)
        height = max(2, h)
        self.ctx.viewport = (0, 0, width, height)
        self.arc_ball.setBounds(width, height)

        # Console Info
        print(f'OpenGL Viewport Resized To: {width, height}')

    def paintGL(self):
        self.ctx.clear(*self.bg_color)
        self.ctx.enable_only(GL.DEPTH_TEST | GL.BLEND)

        self.aspect_ratio = self.width() / max(1.0, self.height())

        perspective = Matrix44.perspective_projection(60.0, self.aspect_ratio, 0.0001, 10000.0)
        lookat = Matrix44.look_at(
            (0.0, 0.0, self.camera_zoom),
            (0.0, 0.0, 0.0),
            (0.0, 1.0, 0.0)
        )
        self.arc_ball.Transform[3, :3] = -self.arc_ball.Transform[:3, :3].T @ self.center
        self.view_matrix.write((perspective * lookat * self.arc_ball.Transform).astype('f4'))

        for item in self.items():
            item.render()

        # Console Info
        print('---- Repainting OpenGL Viewport ----')
        print(f'Rendering {len(self.items())} Items')
        print('Current Color: ', self.program['color'].value)
        print('Current Alpha Value: ', self.program['alphaValue'].value)
        print('Current Zoom Amount: ', self.camera_zoom)
        print('Current Matrix: ', self.program['matrix'].value)

    def mousePressEvent(self, event):
        if (event.buttons() & Qt.MouseButton.MiddleButton) and (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
            self.arc_ball.onClickLeftDown(event.x(), event.y())
        elif event.buttons() & Qt.MouseButton.MiddleButton:
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            self.prev_x = event.x()
            self.prev_y = event.y()

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.MouseButton.MiddleButton) and (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
            self.arc_ball.onDrag(event.x(), event.y())

            self.update()

        elif event.buttons() & Qt.MouseButton.MiddleButton:
            x_movement = event.x() - self.prev_x
            y_movement = event.y() - self.prev_y
            self.center[0] -= x_movement * (self.camera_zoom / 750)
            self.center[1] += y_movement * (self.camera_zoom / 750)
            self.prev_x = event.x()
            self.prev_y = event.y()

            self.update()

    def mouseReleaseEvent(self, event):
        if (event.buttons() & Qt.MouseButton.MiddleButton) and (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
            self.arc_ball.onClickLeftUp()

        self.unsetCursor()

    def wheelEvent(self, event):
        self.camera_zoom += -event.angleDelta().y() * 0.001

        if self.camera_zoom < -0.1:
            self.camera_zoom = -0.1

        self.update()

    def unsetCursor(self):
        self.setCursor(Qt.CursorShape.CrossCursor)

    def mapMouseToViewport(self, mouse_x, mouse_y):
        """
        Maps mouse screen coordinates to the OpenGL scene viewport.

        :param mouse_x: The X position of the mouse in screen coordinates.
        :param mouse_y: The Y position of the mouse in screen coordinates.
        :return: A 3D coordinate in the OpenGL scene.
        """
        # Get viewport dimensions
        viewport = self.ctx.viewport
        width, height = viewport[2], viewport[3]

        # Normalize mouse coordinates to range [-1, 1]
        norm_x = (2.0 * mouse_x) / width - 1.0
        norm_y = 1.0 - (2.0 * mouse_y) / height  # Flip y-axis
        norm_z = 1.0  # Default to near plane

        # Create the normalized device coordinates (NDC)
        ndc = np.array([norm_x, norm_y, norm_z, 1.0], dtype=np.float32)

        # Retrieve matrices
        projection_matrix = Matrix44.perspective_projection(60.0, self.aspect_ratio, 0.0001, 10000.0)
        lookat_matrix = Matrix44.look_at(
            (0.0, 0.0, self.camera_zoom),  # Camera position
            (0.0, 0.0, 0.0),  # Look-at target
            (0.0, 1.0, 0.0)  # Up vector
        )
        view_matrix = self.arc_ball.Transform

        # Combine matrices
        transform_matrix = projection_matrix * lookat_matrix * view_matrix
        inverse_transform = np.linalg.inv(transform_matrix)

        # Convert NDC back to world space
        world_coords = np.dot(inverse_transform, ndc)
        world_coords /= world_coords[3]  # Normalize by w component

        return Vector3(world_coords[:3])

    def updateArcBall(self):
        if self.items():
            # Create ArcBall
            self.arc_ball = ArcBallUtil(self.width(), self.height())

            mesh_points = []

            for item in self.items():
                if isinstance(item, PointGroupItem):
                    for p in item.points():
                        mesh_points.append(p.pos())
                elif isinstance(item, TerrainItem):
                    for p in item.points():
                        mesh_points.append([*p])
                else:
                    mesh_points.append(item.pos())

            print(mesh_points)

            bounding_box_min = np.min(mesh_points, axis=0)
            bounding_box_max = np.max(mesh_points, axis=0)

            self.center = 0.5 * (bounding_box_max + bounding_box_min)
            self.scale = np.linalg.norm(bounding_box_max - self.center)
            self.arc_ball.Transform[:3, :3] /= self.scale
            self.arc_ball.Transform[3, :3] = -self.center / self.scale

    def addItem(self, item: BaseItem):
        if item not in self._items:
            self._items.append(item)

        print('Item Added')

        self.update()

    def removeItem(self, item: BaseItem):
        self._items.remove(item)

        print('Item Removed')

        self.update()

    def items(self) -> list[BaseItem]:
        return self._items

    def selectedItems(self):
        return [item for item in self.items() if item.isSelected()]

    def clearSelection(self):
        for item in self.items():
            item.setSelected(False)

        self.update()

    def itemAt(self, pos):
        pass

    def undoStack(self) -> QUndoStack:
        return self.undo_stack

    def addUndoCommand(self, command: QUndoCommand):
        self.undo_stack.push(command)

        print(f'Undo Command: {command}')

        self.update()

    def setBackgroundColor(self, color: str):
        self.bg_color = hexToRGB(color)

        self.update()

    def isWireframe(self):
        return self.wireframe

    def setWireframe(self, enabled: bool):
        self.wireframe = enabled

        self.update()

    def context(self) -> GL.Context:
        return self.ctx

    def shaderProgram(self) -> GL.Program:
        return self.program
