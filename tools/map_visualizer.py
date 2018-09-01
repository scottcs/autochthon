"""Map visualization tool.

This tool is used to quickly visualize map generation algorithms.

TODO: Gui tool, show layers, save image with visible layers, layer colors, button to regen
TODO: generate multiple runs
TODO: generate from specific seed
TODO: specify layers drawn
TODO: render path analysis and loops analysis

"""
from pathlib import Path
import sys
from typing import Optional

from PySide2.QtCore import Qt, Signal
from PySide2.QtGui import QImage, QPainter, QPalette, QColor, QPixmap
from PySide2.QtWidgets import (QApplication, QAbstractItemView, QDialog, QDialogButtonBox,
                               QFileDialog, QHBoxLayout, QLabel, QLineEdit, QListWidget,
                               QListWidgetItem, QMessageBox, QPushButton, QSpacerItem,
                               QStackedLayout, QTableWidget, QTableWidgetItem, QVBoxLayout,
                               QWidget, QComboBox, QGridLayout, QSizePolicy)

STYLESHEET = Path('static/css/qt_theme.css')
MIN_WIDTH, MIN_HEIGHT = 1200, 800


class MapSizeWidget(QWidget):
    """Map size."""

    def __init__(self, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)

        self.map_width = QLineEdit()
        self.map_width.setAttribute(Qt.WA_MacShowFocusRect, False)  # macOS only
        self.map_width.setFixedWidth(50)
        self.map_height = QLineEdit()
        self.map_height.setAttribute(Qt.WA_MacShowFocusRect, False)  # macOS only
        self.map_height.setFixedWidth(50)

        layout.addWidget(QLabel('Map Size:'))
        layout.addWidget(self.map_width)
        layout.addWidget(QLabel('x'))
        layout.addWidget(self.map_height)
        layout.addStretch()

        self.setLayout(layout)


class AlgorithmWidget(QWidget):
    """Map algorithm."""

    def __init__(self, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)

        self.choice = QComboBox()
        self.choice.addItems(['ClassicMap', 'Cellular Automaton'])

        layout.addWidget(QLabel('Algorithm:'))
        layout.addWidget(self.choice)
        layout.addStretch()

        self.setLayout(layout)


class SeedWidget(QWidget):
    """Map seed."""
    def __init__(self, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)

        self.value = QLineEdit()
        self.value.setAttribute(Qt.WA_MacShowFocusRect, False)  # macOS only

        layout.addWidget(QLabel('Seed:'))
        layout.addWidget(self.value)
        layout.addStretch()

        self.setLayout(layout)


class OptionsWidget(QWidget):
    """Map Visualizer options."""

    def __init__(self, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        layout = QGridLayout()
        layout.setSpacing(0)
        layout.setMargin(0)

        self.map_size = MapSizeWidget()
        self.algorithm = AlgorithmWidget()
        self.seed = SeedWidget()

        layout.addWidget(self.map_size, 0, 0, Qt.AlignTop)
        layout.addWidget(self.algorithm, 0, 1, Qt.AlignTop)
        layout.addWidget(self.seed, 1, 0, Qt.AlignTop)

        self.setLayout(layout)


class ButtonsWidget(QWidget):
    """Map Visualizer bottom buttons."""

    generate_map = Signal()
    save_image = Signal()

    def __init__(self, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)
        layout.setAlignment(Qt.AlignRight)

        self.generate_button = QPushButton('Generate')
        self.generate_button.setObjectName('largeButton')
        self.generate_button.setAutoDefault(True)
        self.generate_button.setDefault(True)
        self.save_image_button = QPushButton('Save Image')
        self.save_image_button.setFocusPolicy(Qt.NoFocus)
        self.save_image_button.setAutoDefault(False)
        self.save_image_button.setDefault(False)

        layout.addStretch()
        layout.addWidget(self.generate_button)
        layout.addStretch()
        layout.addWidget(self.save_image_button)
        self.setLayout(layout)

        self.generate_button.clicked.connect(self._on_generate_map)
        self.save_image_button.clicked.connect(self._on_save_image)

    def _on_generate_map(self) -> None:
        self.generate_map.emit()

    def _on_save_image(self) -> None:
        self.save_image.emit()


class LayersItem(QWidget):
    """Map Visualizer Layer item widget."""

    def __init__(self, name: str, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)

        self.name = QLabel(name)

        layout.addWidget(self.name)

        self.setLayout(layout)


class LayersWidget(QWidget):
    """Map Visualizer layers widget."""

    def __init__(self, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)
        self.setFixedWidth(200)

        layout.addWidget(QLabel('Layers:'))
        layers = ['base', 'walkable', 'transparent', 'spawnable_player',
                  'spawnable_enemy', 'spawnable_item']
        self.layers = []
        for layer in layers:
            item = LayersItem(layer)
            self.layers.append(item)
            layout.addWidget(item)
        layout.addStretch()

        self.setLayout(layout)


class CentralWidget(QWidget):
    """Map Visualizer central widget."""

    def __init__(self, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)

        self.layers = LayersWidget()
        self.canvas = QLabel()
        self.canvas.setMinimumSize(MIN_WIDTH - 10 - self.layers.width(), MIN_HEIGHT - 100)

        layout.addWidget(self.layers)
        layout.addWidget(self.canvas)

        self.setLayout(layout)


class MapVisualizer(QWidget):
    """Map Visualizer parent widget."""

    def __init__(self, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        self.setWindowTitle('Map Visualizer')
        self.setMinimumSize(MIN_WIDTH, MIN_HEIGHT)
        self.setObjectName('MainApp')

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(10)

        self.options = OptionsWidget()
        self.central = CentralWidget()
        self.buttons = ButtonsWidget()

        layout.addWidget(self.options)
        layout.addWidget(self.central)
        layout.addWidget(self.buttons)
        self.setLayout(layout)

        self.buttons.generate_map.connect(self._on_generate_map)
        self.buttons.save_image.connect(self._on_save_image)
        self.buttons.generate_button.setFocus()

    def _on_generate_map(self) -> None:
        print('generate map')

    def _on_save_image(self) -> None:
        print('save image')


def main() -> int:
    """ Main function """
    app = QApplication(sys.argv)
    with STYLESHEET.open() as f:
        app.setStyleSheet(f.read())
    map_visualizer = MapVisualizer()
    map_visualizer.show()
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())

