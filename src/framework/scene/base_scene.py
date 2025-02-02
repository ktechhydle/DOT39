from src._imports import *
from src.framework.items.base_item import BaseItem
from src.framework.items.point_group import PointGroupItem
from src.framework.items.point_item import PointItem
from src.framework.items.terrain_item import TerrainItem
from src.framework.scene.functions import hexToRGB, vertex_shad, fragment_shad
from src.framework.scene.arcball import ArcBallUtil
from src.framework.scene.undo_commands import *


class BaseScene(QGLWidget):
    def __init__(self, unit_mgr, parent=None):
        super(BaseScene, self).__init__(parent)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.CrossCursor)

        self.unit_manager = unit_mgr

        self.undo_stack = QUndoStack(self)
        self.undo_stack.setUndoLimit(200)

        self.ctx = None
        self.program = None
        self.wireframe = True
        self.bg_color = hexToRGB('#000000')
        self.aspect_ratio = 1.0
        self.camera_zoom = 2.0

        self._items = []

    def initializeGL(self):
        self.ctx = GL.create_context()
        self.ctx.clear(*self.bg_color)
        self.ctx.enable(GL.DEPTH_TEST)
        self.ctx.wireframe = self.wireframe
        self.ctx.line_width = 3.0

        self.program = self.ctx.program(
            vertex_shader=vertex_shad,
            fragment_shader=fragment_shad
        )

        self.view_matrix = self.program['matrix']

        self.arc_ball = ArcBallUtil(self.width(), self.height())
        self.center = np.zeros(3)
        self.scale = 1.0

        # Create Selection Framebuffer
        self.selection_texture = self.ctx.texture((self.width(), self.height()), 4,
                                                  dtype='i4')  # Integer texture for IDs
        self.depth_texture = self.ctx.depth_texture((self.width(), self.height()))
        self.selection_fbo = self.ctx.framebuffer(color_attachments=[self.selection_texture],
                                                  depth_attachment=self.depth_texture)

        # Console Info
        print('---- DOT39 Compiled Successfully ----\n---- OpenGL Attributes Initialized ----')
        print('OpenGL Version: ', self.ctx.version_code)

    def resizeGL(self, w, h):
        width = max(2, w)
        height = max(2, h)
        self.ctx.viewport = (0, 0, width, height)
        self.arc_ball.setBounds(width, height)

        # Resize selection framebuffer
        self.resizeSelectionBuffers(w, h)

        # Console Info
        print(f'OpenGL Viewport Resized To: {width, height}')

    def paintGL(self):
        self.ctx.clear(*self.bg_color)
        self.ctx.enable_only(GL.DEPTH_TEST | GL.BLEND)

        self.aspect_ratio = self.width() / max(1.0, self.height())

        # Orthographic projection
        ortho_size = self.camera_zoom  # Define the size of the orthographic view
        ortho_left = -self.aspect_ratio * ortho_size
        ortho_right = self.aspect_ratio * ortho_size
        ortho_bottom = -ortho_size
        ortho_top = ortho_size
        ortho_near = -10000.0  # Adjust based on your scene
        ortho_far = 10000.0

        orthographic = Matrix44.orthogonal_projection(
            ortho_left, ortho_right, ortho_bottom, ortho_top, ortho_near, ortho_far
        )

        # View transformation (same as before)
        lookat = Matrix44.look_at(
            (0.0, 0.0, self.camera_zoom),
            (0.0, 0.0, 0.0),
            (0.0, 1.0, 0.0)
        )
        self.arc_ball.Transform[3, :3] = -self.arc_ball.Transform[:3, :3].T @ self.center
        self.view_matrix.write((orthographic * lookat * self.arc_ball.Transform).astype('f4'))

        # Render items
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
        if event.buttons() & Qt.MouseButton.LeftButton:
            item = self.itemAt(event.x(), event.y())

            if item:
                if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                    item.setSelected(True)
                    self.update()
                    return

                self.clearSelection()
                item.setSelected(True)

            else:
                self.clearSelection()

        elif (event.buttons() & Qt.MouseButton.MiddleButton) and (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
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
            self.center[0] -= x_movement * (self.camera_zoom / 10)
            self.center[1] += y_movement * (self.camera_zoom / 10)
            self.prev_x = event.x()
            self.prev_y = event.y()

            self.update()

        else:
            item = self.itemAt(event.x(), event.y())

            if item:
                item.hover()
            else:
                self.update()

    def mouseReleaseEvent(self, event):
        if (event.buttons() & Qt.MouseButton.MiddleButton) and (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
            self.arc_ball.onClickLeftUp()

        self.unsetCursor()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.updateArcBall()
            self.update()

    def wheelEvent(self, event):
        self.camera_zoom += -event.angleDelta().y() * 0.001

        if self.camera_zoom < -0.1:
            self.camera_zoom = -0.1

        self.update()

    def unsetCursor(self):
        self.setCursor(Qt.CursorShape.CrossCursor)

    def applyCS(self):
        x, y = self.unit_manager.transformedXY()

        for item in self.items():
            if not hasattr(item, '_translated'):
                item._translated = True

                if isinstance(item, PointGroupItem):
                    for point in item.points():
                        point.setPos([point.x() + x, point.y() + y, point.z()])

                elif isinstance(item, PointItem):
                    item.setPos([item.x() + x, item.y() + y, item.z()])

        print(f'Coordinate System Offset: {x, y}')

    def itemMeshPoints(self):
        """
        Returns a list of all item positions and points
        :return: list[float]
        """

        # Calculate the bounding box of all items
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

        return mesh_points

    def updateArcBall(self):
        if self.items():
            # Create ArcBall
            self.arc_ball = ArcBallUtil(self.width(), self.height())

            mesh_points = self.itemMeshPoints()

            bounding_box_min = np.min(mesh_points, axis=0)
            bounding_box_max = np.max(mesh_points, axis=0)

            self.center = 0.5 * (bounding_box_max + bounding_box_min)
            self.scale = np.linalg.norm(bounding_box_max - self.center)
            self.arc_ball.Transform[:3, :3] /= self.scale
            self.arc_ball.Transform[3, :3] = -self.center / self.scale

    def addItem(self, item: BaseItem):
        """
        Adds the item to the render que
        :param item: BaseItem
        :return: None
        """

        if item not in self._items:
            self._items.append(item)

        print('Item Added')

        self.update()

    def removeItem(self, item: BaseItem):
        """
        Removes items from the render que
        :param item: BaseItem
        :return: None
        """
        self._items.remove(item)

        print('Item Removed')

        self.update()

    def items(self) -> list[BaseItem]:
        """
        Returns a list of items currently in the render que
        :return: list[BaseItem]
        """
        return self._items

    def selectedItems(self):
        return [item for item in self.items() if item.isSelected()]

    def clearSelection(self):
        for item in self.items():
            item.setSelected(False)

        self.update()

    def itemAt(self, x, y) -> BaseItem or None:
        """
        Retrieves the item at the specified x, y screen coordinates
        :param x: float
        :param y: float
        :return: BaseItem
        """
        y = self.height() - y - 1  # Invert Y for OpenGL coordinates
        print('---- Locating Scene Items ----')
        print(f'X: {x}')
        print(f'Y: {y}')
        print('Rendering For Selection')

        # Render to selection framebuffer
        self.renderForSelection()

        # Read the pixel under the cursor
        pixel_data = self.selection_fbo.read(viewport=(x, y, 1, 1), alignment=4, dtype='i4')
        color_values = np.frombuffer(pixel_data, dtype=np.float32)[:3]  # Extract RGB
        object_id = int(color_values[0] * 255)

        self.ctx.screen.use()
        self.update()

        # Find the selected object
        if 0 < object_id <= len(self.items()):
            selected_item = self.items()[object_id - 1]  # IDs start at 1
            return selected_item

        return None

    def renderForSelection(self):
        """
        Renders the scene with object IDs into an offscreen framebuffer
        :return: None
        """
        self.selection_fbo.use()
        self.ctx.clear(0, 0, 0, 0)

        # Use a simple shader for selection rendering
        for i, item in enumerate(self.items(), start=1):  # IDs start at 1
            item.render(color=(i / 255.0, 0, 0, 1))
            print((i / 255.0, 0, 0, 1))

    def resizeSelectionBuffers(self, w, h):
        """
        Resizes the selection framebuffer
        :return: None
        """
        self.selection_texture = self.ctx.texture((w, h), 4, dtype='i4')
        self.depth_texture = self.ctx.depth_texture((w, h))
        self.selection_fbo = self.ctx.framebuffer(color_attachments=[self.selection_texture],
                                                  depth_attachment=self.depth_texture)

    def undo(self):
        self.undo_stack.undo()
        self.update()

    def redo(self):
        self.undo_stack.redo()
        self.update()

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
