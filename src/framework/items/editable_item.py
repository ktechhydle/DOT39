from src._imports import *
from src.gui.dialogs import EditValueDialog
from src.framework.items.base_item import *
from src.framework.scene.functions import hexToRGB


class EditableItem(BaseItem):
    InputTypeInt = 0
    InputTypeFloat = 1
    InputTypeString = 2
    valueChanged = pyqtSignal(object)

    def __init__(self, scene, program: GL.Program, value: object, input_type: int, pos: list[float] = [0.0, 0.0, 0.0], name=''):
        super().__init__(scene, name)
        self.setPos(pos)
        self.setColor(hexToRGB('#cc6000'))
        self._value = value
        self._input_type = input_type

        self.program = program
        self.ctx = scene.ctx
        self.vbo = self.createVbo()

    def createVbo(self):
        font_id = QFontDatabase.addApplicationFont('resources/fonts/Simplex.ttf')
        font_families = QFontDatabase.applicationFontFamilies(font_id)
        font = QFont(font_families[0], 10)

        path = QPainterPath()
        path.addText(QPointF(0, 0), font, f'{self._value}')

        # Convert the path to polygons
        polygons = path.toSubpathPolygons()

        # Extract vertex data
        vertices = []
        for polygon in polygons:
            for point in polygon:
                vertices.append((point.x() * 0.1) + self.x())
                vertices.append((-point.y() * 0.1) + self.y())
                vertices.append(100000)  # Letters only visible when facing top down

            # Add a break in the drawing sequence
            vertices.append(float('nan'))
            vertices.append(float('nan'))
            vertices.append(float('nan'))

        return self.ctx.buffer(np.array(vertices, dtype='f4'))

    def value(self):
        return self._value

    def inputType(self):
        return self._input_type

    def setValue(self, value):
        self._value = value
        #self.valueChanged.emit(self._value)

        self.update()

    def setInputType(self, type: int):
        self._input_type = type

    def startEditing(self):
        dialog = EditValueDialog(self)
        dialog.exec()

    def render(self, color=None):
        super().render()

        def set_color(color_value):
            self.program['color'].value = color_value[:3]
            self.program['alphaValue'].value = color_value[3]

        # Set color for main object
        if color:
            set_color(color)
        else:
            current_color = self.color()
            if self.isSelected():
                self.program['color'].value = hexToRGB('#007fff')
            elif self.isHovered():
                self.program['color'].value = hexToRGB('#0058b2')
            else:
                self.program['color'].value = current_color

        # Render main object
        self.ctx.simple_vertex_array(self.program, self.vbo, 'in_vert').render(GL.LINE_LOOP)

    def update(self):
        self.vbo = self.createVbo()
