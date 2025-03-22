from src._imports import *
import re


class ToolBarContainer(QWidget):
    def __init__(self, name: str, widgets: list[QWidget], parent=None):
        super().__init__(parent)

        self._name = name
        self._widgets = widgets

        self._createUI()

    def _createUI(self):
        self.setLayout(QVBoxLayout())

        hlayout1 = QHBoxLayout()
        hlayout2 = QHBoxLayout()

        label = QLabel(self.name())
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hlayout1.addWidget(label)

        for w in self.widgets():
            hlayout2.addWidget(w)

        self.layout().addLayout(hlayout1)
        self.layout().addLayout(hlayout2)

    def addRow(self, widgets: list[QWidget]):
        hlayout = QHBoxLayout()

        for w in widgets:
            hlayout.addWidget(w)

        self.layout().addLayout(hlayout)

    def name(self):
        return self._name

    def widgets(self):
        return self._widgets


class ToolBarButton(QPushButton):
    def __init__(self, text: str, checkable=False, toolbar_group=None):
        super().__init__(text)
        self.setCheckable(checkable)
        self.setObjectName('toolbarButton')

        if toolbar_group:
            toolbar_group.addButton(self)


class ToolBoxButton(QPushButton):
    def __init__(self, text):
        super().__init__()
        self.setFixedHeight(27)

        self._text = text

    def paintEvent(self, event):
        super().paintEvent(event)

        pixmap = QPixmap('mp_software_stylesheets/assets/triangle-right.svg')

        if self.isChecked():
            transform = QTransform()
            transform.rotate(90)
            pixmap = pixmap.transformed(transform, Qt.TransformationMode.SmoothTransformation)

        padding_x = 30
        padding_y = 18
        new_pos = QPoint(padding_x, padding_y)

        painter = QPainter(self)
        painter.drawPixmap(QRect(0, -2, 30, 30), pixmap, pixmap.rect())
        painter.drawText(new_pos, self._text)
        painter.end()

    def mousePressEvent(self, event):
        # Check if the mouse is within the top 30 pixels of the button
        if event.y() < 30:
            super().mousePressEvent(event)

    def setFixedHeight(self, h):
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(100)

        start_geometry = self.geometry()
        end_geometry = self.geometry()
        end_geometry.setHeight(h)

        self.animation.setStartValue(start_geometry)
        self.animation.setEndValue(end_geometry)

        self.animation.valueChanged.connect(lambda: super(ToolBoxButton, self).setFixedHeight(
            self.animation.currentValue().height()))

        self.animation.start()

    def restoreSize(self):
        self.setFixedHeight(27)


class ToolBox(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.horizontalScrollBar().setEnabled(False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)

        self.container = QWidget()
        self.container.setObjectName('customScrollArea')
        self.setStyleSheet('QWidget { border-radius: 5px; }')
        self.container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.container.setLayout(QVBoxLayout())
        self.container.layout().setContentsMargins(10, 10, 10, 10)
        self.setWidget(self.container)

        self._control_parent = parent
        self._buttons = []
        self._radius = 5

    def contextMenuEvent(self, event):
        menu = ContextMenu()
        menu.setAnimationEnabled(True)

        collapse_all_action = QAction('Collapse All', self)
        collapse_all_action.triggered.connect(self.collapseAll)
        expand_all_action = QAction('Expand All', self)
        expand_all_action.triggered.connect(self.expandAll)

        menu.addAction(collapse_all_action)
        menu.addSeparator()
        menu.addAction(expand_all_action)

        menu.exec(self.mapToGlobal(event.pos()))

    def resizeEvent(self, event):
        path = QPainterPath()
        rect = QRectF(self.rect()).adjusted(.5, .5, -1.5, -1.5)
        path.addRoundedRect(rect, self._radius, self._radius)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(0, 0, 0, 200))  # Set the color
        self.setPalette(palette)

        region = QRegion(path.toFillPolygon(QTransform()).toPolygon())
        self.setMask(region)

    def addItem(self, widget: QWidget, text: str, icon: QIcon = None):
        button = ToolBoxButton(text)
        button.setObjectName('panelTitle')
        button.setCheckable(True)
        button.widget = widget
        button.widget.setVisible(False)
        button.clicked.connect(lambda: self.toggleWidget(button))

        button.setLayout(QVBoxLayout())
        button.layout().setContentsMargins(0, 30, 0, 0)
        button.layout().addWidget(button.widget)

        if icon:
            button.setIcon(icon)

        self._buttons.append(button)
        self.container.layout().insertWidget(self.container.layout().count(), button)

    def addSpacer(self):
        self.container.layout().addStretch()

    def collapseAll(self):
        for button in self.buttons():
            button.setChecked(False)
            self.toggleWidget(button)

    def expandAll(self):
        for button in self.buttons():
            button.setChecked(True)
            self.toggleWidget(button)

    def toggleWidget(self, button: ToolBoxButton):
        if button.isChecked():
            if not button.widget.isVisible():
                button.widget.setVisible(True)
                if not hasattr(button, 'expandedHeight'):
                    button.expandedHeight = button.widget.height() + button.height()
                button.setFixedHeight(button.expandedHeight)
                self.ensureWidgetVisible(button.widget)
        else:
            button.widget.setVisible(False)
            button.restoreSize()

    def buttons(self) -> list[QPushButton]:
        return self._buttons

    def setCurrentWidget(self, widget: QWidget):
        self.collapseAll()

        for button in self.buttons():
            if button.widget == widget:
                button.setChecked(True)
                self.toggleWidget(button)

    def setCurrentIndex(self, index: int):
        self.buttons()[index].setChecked(True)
        self.toggleWidget(self.buttons()[index])

    def controlParent(self) -> QWidget:
        return self._control_parent


class AnimatedLabel(QLabel):
    def __init__(self, text, parent=None, interval=100):
        super().__init__('', parent)

        self.full_html = text
        self.full_text = self.stripHTMLTags(text)
        self.current_index = 0
        self.typing_speed = interval
        self.deleting = False  # New state variable

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateText)
        self.timer.start(self.typing_speed)

    def stripHTMLTags(self, html):
        return re.sub(r'<[^>]+>', '', html)

    def rebuildHTML(self, visible_text):
        rebuilt_text = self.full_html.replace(self.full_text, visible_text, 1)
        return rebuilt_text

    def updateText(self):
        if self.isVisible():
            if not self.deleting:  # Typing phase
                if self.current_index < len(self.full_text):
                    self.current_index += 1
                    self.setText(self.rebuildHTML(self.full_text[:self.current_index]))
                else:
                    self.timer.stop()
                    QTimer.singleShot(1500, self.startDeleting)
            else:  # Deleting phase
                if self.current_index > 0:
                    self.current_index -= 1
                    self.setText(self.rebuildHTML(self.full_text[:self.current_index]))
                else:
                    self.timer.stop()
                    QTimer.singleShot(500, self.restartTyping)

    def startDeleting(self):
        self.deleting = True
        self.timer.start(self.typing_speed)

    def restartTyping(self):
        self.deleting = False
        self.timer.start(self.typing_speed)


class HomeButton(QToolButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText('Home')
        self.setIcon(QIcon('resources/icons/logos/dot39_logo.svg'))
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.setCheckable(True)


class IntegerInput(QWidget):
    def __init__(self, title: str,
                 range: tuple[int, int],
                 layout: QVBoxLayout or QHBoxLayout,
                 suffix: str='',
                 parent=None):
        super().__init__(parent)
        self.setLayout(layout)
        self.layout().setContentsMargins(0, 0, 0, 0)

        self._title = title
        self._range = range
        self._suffix = suffix
        self._default_value = 0

        self._create()

    def _create(self):
        self._label = QLabel(self._title, self)
        self._spinbox = QSpinBox(self)
        self._spinbox.setRange(*self._range)
        self._spinbox.setSuffix(self._suffix)
        self._spinbox.setValue(self._default_value)

        self.layout().addWidget(self._label)
        self.layout().addWidget(self._spinbox)

    def _update(self):
        self._label.setText(self._title)
        self._spinbox.setRange(*self._range)
        self._spinbox.setSuffix(self._suffix)
        self._spinbox.setValue(self._default_value)

    def setTitle(self, title: str):
        self._title = title

        self._update()

    def setRange(self, range: tuple[int, int]):
        self._range = range

        self._update()

    def setSuffix(self, suffix: str):
        self._suffix = suffix

        self._update()

    def setDefaultValue(self, value: int):
        self._default_value = value

        self._update()

    def title(self) -> str:
        return self._title

    def range(self) -> tuple[int, int]:
        return self._range

    def suffix(self) -> str:
        return self._suffix

    def defaultValue(self) -> int:
        return self._default_value

    def value(self) -> int:
        return self._spinbox.value()


class FloatInput(QWidget):
    def __init__(self, title: str,
                 range: tuple[float, float],
                 layout: QVBoxLayout or QHBoxLayout,
                 step: float = 0.1,
                 suffix: str='',
                 parent=None):
        super().__init__(parent)
        self.setLayout(layout)
        self.layout().setContentsMargins(0, 0, 0, 0)

        self._title = title
        self._range = range
        self._step = step
        self._suffix = suffix
        self._default_value = 0.0

        self._create()

    def _create(self):
        self._label = QLabel(self._title, self)
        self._spinbox = QDoubleSpinBox(self)
        self._spinbox.setRange(*self._range)
        self._spinbox.setSingleStep(self._step)
        self._spinbox.setSuffix(self._suffix)
        self._spinbox.setValue(self._default_value)

        self.layout().addWidget(self._label)
        self.layout().addWidget(self._spinbox)

    def _update(self):
        self._label.setText(self._title)
        self._spinbox.setRange(*self._range)
        self._spinbox.setSingleStep(self._step)
        self._spinbox.setSuffix(self._suffix)
        self._spinbox.setValue(self._default_value)

    def setTitle(self, title: str):
        self._title = title

        self._update()

    def setRange(self, range: tuple[float, float]):
        self._range = range

        self._update()

    def setStep(self, step: float):
        self._step = step

    def setSuffix(self, suffix: str):
        self._suffix = suffix

        self._update()

    def setDefaultValue(self, value: float):
        self._default_value = value

        self._update()

    def title(self) -> str:
        return self._title

    def range(self) -> tuple[float, float]:
        return self._range

    def step(self) -> float:
        return self._step

    def suffix(self) -> str:
        return self._suffix

    def defaultValue(self) -> float:
        return self._default_value

    def value(self) -> float:
        for i in range(self.layout().count()):
            item = self.layout().itemAt(i)

            if isinstance(item.widget(), QDoubleSpinBox):
                return item.widget().value()


class StringInput(QWidget):
    def __init__(self, title: str,
                 layout: QVBoxLayout or QHBoxLayout,
                 placeholder: str = '',
                 parent=None):
        super().__init__(parent)
        self.setLayout(layout)
        self.layout().setContentsMargins(0, 0, 0, 0)

        self._title = title
        self._placeholder = placeholder
        self._default_value = ''

        self._create()

    def _create(self):
        self._label = QLabel(self._title, self)
        self._input = QLineEdit(self)
        self._input.setPlaceholderText(self._placeholder)
        self._input.setText(self._default_value)

        self.layout().addWidget(self._label)
        self.layout().addWidget(self._input)

    def _update(self):
        self._label.setText(self._title)
        self._input.setPlaceholderText(self._placeholder)
        self._input.setText(self._default_value)

    def setTitle(self, title: str):
        self._title = title

        self._update()

    def setPlaceholder(self, text: str):
        self._placeholder = text

        self._update()

    def setDefaultValue(self, value: str):
        self._default_value = value

        self._update()

    def title(self) -> str:
        return self._title

    def placeholder(self) -> str:
        return self._placeholder

    def defaultValue(self) -> str:
        return self._default_value

    def value(self) -> str:
        for i in range(self.layout().count()):
            item = self.layout().itemAt(i)

            if isinstance(item.widget(), QLineEdit):
                return item.widget().text()


class OptionInput(QWidget):
    def __init__(self, title: str,
                 values: dict[str, any],
                 layout: QVBoxLayout or QHBoxLayout,
                 on_change=None,
                 parent=None):
        super().__init__(parent)
        self.setLayout(layout)
        self.layout().setContentsMargins(0, 0, 0, 0)

        self._title = title
        self._values = values
        self._on_change = on_change

        self._create()

    def _create(self):
        self._label = QLabel(self._title, self)
        self._combobox = QComboBox(self)

        for k, v in self.values().items():
            self._combobox.addItem(k, v)

        if self._on_change:
            self._combobox.currentIndexChanged.connect(self._on_change)

        self.layout().addWidget(self._label)
        self.layout().addWidget(self._combobox)

    def _update(self):
        self._label.setText(self._title)

    def setTitle(self, title: str):
        self._title = title

        self._update()

    def setValues(self, values: dict[str, any]):
        self._values = values

        self._update()

    def title(self) -> str:
        return self._title

    def values(self) -> dict[str, any]:
        return self._values

    def value(self) -> object:
        for i in range(self.layout().count()):
            item = self.layout().itemAt(i)

            if isinstance(item.widget(), QComboBox):
                return item.widget().itemData(item.widget().currentIndex())


class ContextMenu(QMenu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setObjectName('customMenu')
        self.setMinimumSize(150, 30)

        self.radius = 10
        self._animation_enabled = False

    def addMenu(self, menu, parent=None):
        if isinstance(menu, QMenu):
            super().addMenu(menu)

        else:
            m = ContextMenu(menu, parent=None if parent is None else parent)
            super().addMenu(m)
            return m

    def resizeEvent(self, event):
        path = QPainterPath()
        rect = QRectF(self.rect()).adjusted(.5, .5, -1.5, -1.5)
        path.addRoundedRect(rect, self.radius, self.radius)

        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(0, 0, 0, 200))  # Set the color
        self.setPalette(palette)

        region = QRegion(path.toFillPolygon(QTransform()).toPolygon())
        self.setMask(region)

    def exec(self, pos=None):
        if pos and self.animationEnabled():
            screen_rect = QApplication.primaryScreen().availableGeometry()

            # Get the menu's size (this is available after it's created)
            menu_size = self.sizeHint()

            # Check if the menu would go off the right or bottom of the screen
            if pos.x() + menu_size.width() > screen_rect.right():
                pos.setX(screen_rect.right() - menu_size.width())
            if pos.y() + menu_size.height() > screen_rect.bottom():
                pos.setY(screen_rect.bottom() - menu_size.height())

            # If animation is enabled
            self.animation = QPropertyAnimation(self, b'pos')
            self.animation.setDuration(100)
            self.animation.setStartValue(QPoint(pos.x(), pos.y() + 10))
            self.animation.setEndValue(pos)

            self.animation.start()

        super().exec(pos)

    def setAnimationEnabled(self, enabled: bool):
        self._animation_enabled = enabled

    def animationEnabled(self):
        return self._animation_enabled