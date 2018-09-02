"""Map visualization tool.

This tool is used to quickly visualize map generation algorithms.

TODO: Gui tool, show layers, save image with visible layers, layer colors, button to regen
TODO: generate multiple runs
TODO: generate from specific seed
TODO: specify layers drawn
TODO: render path analysis and loops analysis

"""
import json
from pathlib import Path
import sys
from typing import Optional, Any, Tuple

from PySide2.QtCore import Qt, Signal
from PySide2.QtGui import QImage, QPainter, QPalette, QColor, QPixmap, qRgb, QIntValidator
from PySide2.QtWidgets import (QApplication, QAbstractItemView, QDialog, QDialogButtonBox,
                               QFileDialog, QHBoxLayout, QLabel, QLineEdit, QListWidget,
                               QListWidgetItem, QMessageBox, QPushButton, QSpacerItem,
                               QStackedLayout, QTableWidget, QTableWidgetItem, QVBoxLayout,
                               QWidget, QComboBox, QGridLayout, QSizePolicy, QScrollArea)

from game.core.map import ClassicMap, Map

CONFIG_FILE = Path('data') / Path('config.json')
STYLESHEET = Path('static/css/qt_theme.css')
MIN_WIDTH, MIN_HEIGHT = 1240, 800


class MapSizeWidget(QWidget):
    """Map size."""

    size_changed = Signal()

    def __init__(self, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)

        v_size = QIntValidator(10, 234, self)
        v_scale = QIntValidator(1, 20, self)
        self.map_width = QLineEdit()
        self.map_width.setAttribute(Qt.WA_MacShowFocusRect, False)  # macOS only
        self.map_width.setFixedWidth(50)
        self.map_width.setText('100')
        self.map_width.setValidator(v_size)
        self.map_height = QLineEdit()
        self.map_height.setAttribute(Qt.WA_MacShowFocusRect, False)  # macOS only
        self.map_height.setFixedWidth(50)
        self.map_height.setText('100')
        self.map_height.setValidator(v_size)
        self.map_scale = QLineEdit()
        self.map_scale.setAttribute(Qt.WA_MacShowFocusRect, False)  # macOS only
        self.map_scale.setFixedWidth(50)
        self.map_scale.setText('10')
        self.map_scale.setValidator(v_scale)

        layout.addWidget(QLabel('Map Size: '))
        layout.addWidget(self.map_width)
        layout.addWidget(QLabel('x'))
        layout.addWidget(self.map_height)
        layout.addWidget(QLabel('   Scale: '))
        layout.addWidget(self.map_scale)
        layout.addStretch()

        self.setLayout(layout)

        self.map_width.editingFinished.connect(self._on_size_changed)
        self.map_height.editingFinished.connect(self._on_size_changed)
        self.map_scale.editingFinished.connect(self._on_size_changed)

    def get_size(self) -> Tuple[int, int, int]:
        """Get the requested size and scale of the map."""
        w = max(1, int(self.map_width.text()))
        h = max(1, int(self.map_height.text()))
        s = max(1, int(self.map_scale.text()))
        return w, h, s

    def _on_size_changed(self) -> None:
        self.size_changed.emit()


class AlgorithmWidget(QWidget):
    """Map algorithm."""

    algorithm_changed = Signal()

    def __init__(self, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)

        self.choice = QComboBox()
        self.choice.addItems(['ClassicMap', 'CellularAutomaton'])

        layout.addWidget(QLabel('Algorithm:'))
        layout.addWidget(self.choice)
        layout.addStretch()

        self.setLayout(layout)

        self.choice.currentTextChanged.connect(self._on_algorithm_changed)

    def get_algorithm(self) -> str:
        """Get the chosen algorithm."""
        return self.choice.currentText()

    def _on_algorithm_changed(self) -> None:
        self.algorithm_changed.emit()


class SeedWidget(QWidget):
    """Map seed."""

    seed_changed = Signal()

    def __init__(self, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)

        self.value = QLineEdit()
        self.value.setAttribute(Qt.WA_MacShowFocusRect, False)  # macOS only
        self.value.setText('1')

        layout.addWidget(QLabel('Seed:'))
        layout.addWidget(self.value)
        layout.addStretch()

        self.setLayout(layout)

        self.value.editingFinished.connect(self._on_seed_changed)

    def get_seed(self) -> str:
        """Get the seed."""
        return self.value.text()

    def _on_seed_changed(self) -> None:
        self.seed_changed.emit()


class OptionsWidget(QWidget):
    """Map Visualizer options."""

    options_changed = Signal(dict)

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

        self.map_size.size_changed.connect(self._on_options_changed)
        self.algorithm.algorithm_changed.connect(self._on_options_changed)
        self.seed.seed_changed.connect(self._on_options_changed)

    def _on_options_changed(self) -> None:
        self.options_changed.emit(self.get_options())

    def get_options(self) -> dict:
        """Get all options."""
        width, height, scale = self.map_size.get_size()
        return {
            'width': width,
            'height': height,
            'scale': scale,
            'algorithm': self.algorithm.get_algorithm(),
            'seed': self.seed.get_seed(),
        }


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


class ImageWidget(QWidget):
    """Widget to display the map image."""
    def __init__(self, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        self.img = None
        self.pixmap = None
        self.show()

    def draw_map(self, game_map: Map, scale_factor: int) -> None:
        """Draw the map to an image."""
        # TODO: Use QImage.Format_ARGB32_Premultiplied?
        self.img = QImage(game_map.width, game_map.height, QImage.Format_RGB32)

        for cell in game_map:
            if cell.spawnable_player:
                color = qRgb(100, 100, 165)
            elif cell.spawnable_enemy:
                color = qRgb(165, 165, 165)
            elif cell.walkable:
                color = qRgb(100, 100, 100)
            else:
                color = qRgb(65, 43, 21)
            self.img.setPixel(cell.x, cell.y, color)
        self.pixmap = QPixmap.fromImage(self.img).scaled(game_map.width * scale_factor,
                                                         game_map.height * scale_factor,
                                                         Qt.KeepAspectRatio)
        self.setMinimumSize(self.pixmap.width(), self.pixmap.height())
        self.setMaximumSize(self.pixmap.width(), self.pixmap.height())

    def save(self, filename: Path) -> None:
        """Save the image as a file.

        Args:
            filename: Path to the output file.

        """
        if self.img:
            self.img.save(str(filename))

    def paintEvent(self, *args: Any, **kwargs: Any) -> None:
        """Override paint method; draw this widget."""
        if self.pixmap:
            painter = QPainter(self)
            painter.setViewport(0, 0, self.width(), self.height())
            painter.setWindow(0, 0, self.width(), self.height())
            painter.drawPixmap(0, 0, self.pixmap)
            painter.end()


class CentralWidget(QWidget):
    """Map Visualizer central widget."""

    def __init__(self, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)

        self.layers = LayersWidget()
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName('image')
        self.image_widget = ImageWidget()
        self.scroll_area.setWidget(self.image_widget)

        layout.addWidget(self.layers)
        layout.addWidget(self.scroll_area)

        self.setLayout(layout)

    def set_map(self, game_map: Map, scale_factor: int) -> None:
        """Set our map."""
        self.image_widget.draw_map(game_map, scale_factor)
        self.image_widget.repaint()


class MapVisualizer(QWidget):
    """Map Visualizer parent widget."""

    def __init__(self, map_config: dict, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        self.map_config = map_config
        self.setWindowTitle('Map Visualizer')
        self.setMinimumSize(MIN_WIDTH, MIN_HEIGHT)
        self.setObjectName('MainApp')

        layout = QVBoxLayout()
        layout.setSpacing(10)
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
        self.options.options_changed.connect(self._on_options_changed)

        self.buttons.generate_button.setFocus()
        self._on_options_changed(self.options.get_options())

    def _on_generate_map(self) -> None:
        # TODO: create based on map type
        # TODO: use seed
        game_map = ClassicMap(self.map_config['max_tiles_w'],
                              self.map_config['max_tiles_h'])
        game_map.create()
        self.central.set_map(game_map, self.map_config.get('gui_scale', 1))

    def _on_save_image(self) -> None:
        # TODO: File save dialog
        print('save image')

    def _on_options_changed(self, opts: dict) -> None:
        self.map_config['max_tiles_w'] = opts['width']
        self.map_config['max_tiles_h'] = opts['height']
        self.map_config['gui_scale'] = opts['scale']
        self.map_config['algorithm'] = opts['algorithm']
        self.map_config['seed'] = opts['seed']
        self._on_generate_map()


def main() -> int:
    """ Main function """
    app = QApplication(sys.argv)
    with STYLESHEET.open() as f:
        app.setStyleSheet(f.read())
    with CONFIG_FILE.open() as f:
        map_config = json.load(f)['map']
    map_visualizer = MapVisualizer(map_config)
    map_visualizer.show()
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())

