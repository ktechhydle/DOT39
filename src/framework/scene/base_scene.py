from src._imports import *
from src.framework.items.base_item import BaseItem
from src.framework.items.point_group import PointGroupItem
from src.framework.items.point_item import PointItem
from src.framework.items.terrain_item import TerrainItem
from src.framework.items.alignment_item import AlignmentItem
from src.framework.items.editable_item import EditableItem
from src.framework.items.axis_item import AxisItem
from src.framework.scene.functions import hexToRGB, vertex_shad, fragment_shad
from src.framework.scene.camera import Camera
from src.framework.scene.undo_commands import *
from src.framework.managers.context_menu_manager import ContextMenuManager
from src.framework.managers.tool_manager import ToolManager
from src.framework.tools.selection_tool import SelectionTool


class BaseScene(QGLWidget):
    def __init__(self, parent):
        format = QGLFormat()
        format.setSamples(4)
        super(BaseScene, self).__init__(format, parent)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.CrossCursor)

        # Public
        self.undo_stack = QUndoStack(self)
        self.undo_stack.setUndoLimit(200)
        self.ctx = None
        self.program = None
        self.bg_color = hexToRGB('#000000')

        # Private
        self._items = []
        self._wireframe = True
        self._context_menu_manager = ContextMenuManager(self, parent)
        self._tool_manager = ToolManager(self)
        self._selection_tool = SelectionTool(self)

    def initializeGL(self):
        self.ctx = GL.create_context()
        self.ctx.clear(*self.bg_color)
        self.ctx.enable(GL.DEPTH_TEST)
        self.ctx.wireframe = self.isWireframe()
        self.ctx.line_width = 3.0

        self.program = self.ctx.program(
            vertex_shader=vertex_shad,
            fragment_shader=fragment_shad
        )

        self.camera = Camera(self)

        # Create Selection Framebuffer
        self.selection_texture = self.ctx.texture((self.width(), self.height()), 4,
                                                  dtype='i4')  # Integer texture for IDs
        self.depth_texture = self.ctx.depth_texture((self.width(), self.height()))
        self.selection_fbo = self.ctx.framebuffer(color_attachments=[self.selection_texture],
                                                  depth_attachment=self.depth_texture)

        self.addItem(AxisItem(self, self.program))

        # Console Info
        print('---- DOT39 Compiled Successfully ----\n---- OpenGL Attributes Initialized ----')
        print('OpenGL Version: ', self.ctx.version_code)

    def resizeGL(self, w, h):
        self.parent().toolbox.setFixedHeight(h - 22)

        width = max(2, w)
        height = max(2, h)
        self.ctx.viewport = (0, 0, width, height)
        self.camera.resize(width, height)

        # Resize selection framebuffer
        self._resizeSelectionBuffers(w, h)

        # Console Info
        print(f'OpenGL Viewport Resized To: {width, height}')

    def paintGL(self):
        self.ctx.wireframe = self.isWireframe()
        self.ctx.clear(*self.bg_color)
        self.ctx.enable_only(GL.DEPTH_TEST | GL.BLEND)

        self.camera.update()

        # Render items
        for item in self.visibleItems():
            item.render()

        # Console Info
        print('---- Repainting OpenGL Viewport ----')
        print(f'Rendering {len(self.visibleItems())} Items')
        print('Current Color: ', self.program['color'].value)
        print('Current Alpha Value: ', self.program['alphaValue'].value)
        print('Current Zoom Amount: ', self.camera.cameraZoom())
        print('Current Matrix: ', self.program['matrix'].value)

    def mousePressEvent(self, event: QMouseEvent):
        if event.buttons() & Qt.MouseButton.LeftButton:
            if self._tool_manager.currentTool() == ToolManager.SelectionTool:
                self._selection_tool.mousePress(event)

        elif (event.buttons() & Qt.MouseButton.MiddleButton) and (
                event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
            self.setCursor(Qt.CursorShape.SizeAllCursor)
            self.camera.onOrbitStart(event.x(), event.y())

        elif event.buttons() & Qt.MouseButton.MiddleButton:
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            self.camera.onPanStart(event.x(), event.y())

    def mouseMoveEvent(self, event: QMouseEvent):
        if (event.buttons() & Qt.MouseButton.MiddleButton) and (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
            self.camera.onOrbit(event.x(), event.y())
            self.update()

        elif event.buttons() & Qt.MouseButton.MiddleButton:
            self.camera.onPan(event.x(), event.y())
            self.update()

        else:
            self._selection_tool.mouseMove(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if (event.buttons() & Qt.MouseButton.MiddleButton) and (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
            self.camera.onOrbitEnd()

        self.unsetCursor()

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.camera.reset()
            self.update()
        elif event.button() == Qt.MouseButton.LeftButton:
            if self.activeSelection() and isinstance(self.activeSelection(), EditableItem):
                self.activeSelection().startEditing()

    def wheelEvent(self, event: QWheelEvent):
        self.camera.onZoom(event)

        self.selectionTool().clearHover()
        self.update()

    def contextMenuEvent(self, event):
        self._context_menu_manager.showSceneMenu(event)

    def unsetCursor(self):
        self.setCursor(Qt.CursorShape.CrossCursor)

    def itemMeshPoints(self):
        """
        Returns a list of all item positions and points
        :return: list[float]
        """

        # Calculate the bounding box of all items
        mesh_points = []

        for item in self.visibleItems():
            if isinstance(item, PointGroupItem):
                for p in item.points():
                    mesh_points.append(p.pos())

            elif isinstance(item, TerrainItem):
                for p in item.points():
                    mesh_points.append([*p])

            elif isinstance(item, AlignmentItem):
                polygons = item.horizontalPath().toSubpathPolygons()

                for polygon in polygons:
                    for point in polygon:
                        mesh_points.append([point.x(), point.y(), 0])

            elif isinstance(item, (EditableItem, AxisItem)):
                continue

            else:
                mesh_points.append(item.pos())

        return mesh_points

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

    def visibleItems(self) -> list[BaseItem]:
        l = []

        for item in self.items():
            if item.isVisible():
                l.append(item)

        return l

    def selectedItems(self):
        return [item for item in self.visibleItems() if item.isSelected()]

    def activeSelection(self) -> BaseItem or None:
        """
        Returns the selected item (if there is only one item selected
        on the scene)

        :return: BaseItem
        """
        if self.selectedItems() and len(self.selectedItems()) < 2:
            return self.selectedItems()[0]

        return None

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
        self._renderForSelection()

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

    def _renderForSelection(self):
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

    def _resizeSelectionBuffers(self, w, h):
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
        return self._wireframe

    def setWireframe(self, enabled: bool):
        self._wireframe = enabled

        self.update()

    def context(self) -> GL.Context:
        return self.ctx

    def shaderProgram(self) -> GL.Program:
        return self.program

    def sceneCamera(self) -> Camera:
        return self.camera

    def toolManager(self) -> ToolManager:
        return self._tool_manager

    def selectionTool(self) -> SelectionTool:
        return self._selection_tool
