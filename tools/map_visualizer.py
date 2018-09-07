"""Map visualization tool.

This tool is used to quickly visualize map generation algorithms.

TODO: render path analysis and loops analysis

"""
import json
from pathlib import Path
import pydoc
import sys
from typing import Optional, Any, Tuple, Mapping, MutableMapping

from PySide2.QtCore import Qt, Signal
from PySide2.QtGui import QImage, QPainter, QPixmap, qRgb, QIntValidator
from PySide2.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel, QLineEdit,
                               QMessageBox, QPushButton, QSpacerItem, QVBoxLayout, QCheckBox,
                               QWidget, QComboBox, QGridLayout, QScrollArea)

from game.core.map import ClassicMap, Map, MapCell
from game.utils.random import RNGCache

CONFIG_FILE = Path('data') / Path('config.json')
STYLESHEET = Path('static/css/theme.qss')
MIN_WIDTH, MIN_HEIGHT = 1150, 800

MAP_LAYERS = {
    'base': qRgb(65, 43, 21),
    'transparent': qRgb(165, 100, 165),
    'walkable': qRgb(100, 100, 100),
    'spawnable_enemy': qRgb(165, 165, 165),
    'spawnable_item': qRgb(100, 165, 100),
    'spawnable_player': qRgb(165, 255, 255),
    'alt_tile_1': qRgb(165, 100, 100),
    'alt_tile_2': qRgb(195, 100, 100),
    'alt_tile_3': qRgb(225, 100, 100),
}

# Rather than using `globals()`, add map algorithms to a table
# TODO: Maybe we can define this in the map module and use it there too? Or in data files?
ALGORITHMS = {
    'ClassicMap': {
        'class': ClassicMap,
        'opts': {
            'max_rooms': {'type': 'int', 'min': 0, 'max': 1000, 'default': 50},
            'room_min_size': {'type': 'int', 'min': 0, 'max': 1000, 'default': 5},
            'room_max_size': {'type': 'int', 'min': 0, 'max': 1000, 'default': 20},
        },
    },
}


def msg_error(msg: str, parent: Optional[QWidget]=None) -> None:
    """Show an error message."""
    QMessageBox().critical(parent, 'Error!', msg)


class MapSizeWidget(QWidget):
    """Map size."""

    size_changed = Signal()
    scale_changed = Signal()

    def __init__(self, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)

        v_size = QIntValidator(10, 234, self)
        v_scale = QIntValidator(1, 20, self)
        self.map_width = QLineEdit()
        self.map_width.setAttribute(Qt.WA_MacShowFocusRect, False)  # macOS only
        self.map_width.setFixedWidth(32)
        self.map_width.setText('100')
        self.map_width.setValidator(v_size)
        self.map_height = QLineEdit()
        self.map_height.setAttribute(Qt.WA_MacShowFocusRect, False)  # macOS only
        self.map_height.setFixedWidth(32)
        self.map_height.setText('100')
        self.map_height.setValidator(v_size)
        self.map_scale = QLineEdit()
        self.map_scale.setAttribute(Qt.WA_MacShowFocusRect, False)  # macOS only
        self.map_scale.setFixedWidth(24)
        self.map_scale.setText('6')
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
        self.map_scale.editingFinished.connect(self._on_scale_changed)

    def get_size(self) -> Tuple[int, int]:
        """Get the requested size of the map."""
        w = max(1, int(self.map_width.text()))
        h = max(1, int(self.map_height.text()))
        return w, h

    def get_scale(self) -> int:
        """Get the requested scale of the map."""
        return max(1, int(self.map_scale.text()))

    def _on_size_changed(self) -> None:
        self.size_changed.emit()

    def _on_scale_changed(self) -> None:
        self.scale_changed.emit()


class AlgorithmParametersWidget(QWidget):
    """Map algorithm parameters."""

    params_changed = Signal()

    def __init__(self, algorithm: str, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        self.algorithm = algorithm
        self.line_edits = {}

        layout = QGridLayout()
        layout.setSpacing(4)
        layout.setMargin(0)

        row = 0
        for opt, data in ALGORITHMS[algorithm]['opts'].items():
            layout.addWidget(QLabel(f'{opt.capitalize()}: '), row, 0, Qt.AlignVCenter)
            if data['type'] == 'int':
                self.line_edits[opt] = QLineEdit()
                self.line_edits[opt].setAttribute(Qt.WA_MacShowFocusRect, False)  # macOS only
                self.line_edits[opt].setFixedWidth(50)
                self.line_edits[opt].setText(str(data['default']))
                self.line_edits[opt].setValidator(QIntValidator(data['min'], data['max'], self))
                layout.addWidget(self.line_edits[opt], row, 1, Qt.AlignTop)
                self.line_edits[opt].editingFinished.connect(self._on_params_changed)
            else:
                msg_error(f'Option type {data["type"]} is not implemented!', self)
                break
            row += 1
        layout.setColumnStretch(2, 1)
        self.setLayout(layout)

    def get_params(self) -> dict:
        """Get the params as a dict."""
        params = {}
        for opt, line in self.line_edits.items():
            data = ALGORITHMS[self.algorithm]['opts'][opt]
            params[opt] = pydoc.locate(data['type'])(line.text())
        return params

    def _on_params_changed(self) -> None:
        self.params_changed.emit()


class AlgorithmWidget(QWidget):
    """Map algorithm."""

    algorithm_changed = Signal()

    def __init__(self, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setMargin(0)

        choice_layout = QHBoxLayout()
        choice_layout.setSpacing(0)
        choice_layout.setMargin(0)

        self.choice = QComboBox()
        self.choice.addItems(list(ALGORITHMS.keys()))

        choice_layout.addWidget(QLabel('Algorithm:'))
        choice_layout.addWidget(self.choice)
        choice_layout.addStretch()
        self.layout.addLayout(choice_layout)

        self.params = AlgorithmParametersWidget(self.get_algorithm())
        self.layout.addSpacerItem(QSpacerItem(1, 10))
        self.layout.addWidget(self.params)

        self.setLayout(self.layout)

        self.choice.currentIndexChanged.connect(self._on_algorithm_changed)
        self.params.params_changed.connect(self._on_params_changed)

    def get_algorithm(self) -> str:
        """Get the chosen algorithm."""
        return self.choice.currentText()

    def get_params(self) -> dict:
        """Get the algorithm parameters."""
        return self.params.get_params()

    def _on_algorithm_changed(self) -> None:
        self.layout.removeWidget(self.params)
        self.params = AlgorithmParametersWidget(self.get_algorithm())
        self.layout.addWidget(self.params)
        self.algorithm_changed.emit()

    def _on_params_changed(self) -> None:
        self.algorithm_changed.emit()


class SeedWidget(QWidget):
    """Map seed."""

    seed_changed = Signal()
    seed_reset = Signal()

    def __init__(self, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)

        self.value = QLineEdit()
        self.value.setAttribute(Qt.WA_MacShowFocusRect, False)  # macOS only
        self.value.setText('1')
        self.reset_button = QPushButton('Reset')
        self.reset_button.setFocusPolicy(Qt.NoFocus)
        self.reset_button.setAutoDefault(False)
        self.reset_button.setDefault(False)

        layout.addWidget(QLabel('Seed:'))
        layout.addWidget(self.value)
        layout.addWidget(self.reset_button)

        self.setLayout(layout)

        self.value.editingFinished.connect(self._on_seed_changed)
        self.reset_button.clicked.connect(self._on_seed_reset)

    def get_seed(self) -> str:
        """Get the seed."""
        return self.value.text()

    def _on_seed_changed(self) -> None:
        self.seed_changed.emit()

    def _on_seed_reset(self) -> None:
        self.seed_reset.emit()


class OptionsWidget(QWidget):
    """Map Visualizer options."""

    options_changed = Signal(dict)
    scale_changed = Signal(int)
    seed_reset = Signal()

    def __init__(self, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(4)
        self.setMaximumWidth(250)

        self.map_size = MapSizeWidget()
        self.seed = SeedWidget()
        self.algorithm = AlgorithmWidget()

        layout.addWidget(self.map_size)
        layout.addWidget(self.seed)
        layout.addWidget(self.algorithm)
        layout.addStretch()

        self.setLayout(layout)

        self.map_size.size_changed.connect(self._on_options_changed)
        self.map_size.scale_changed.connect(self._on_scale_changed)
        self.algorithm.algorithm_changed.connect(self._on_options_changed)
        self.seed.seed_changed.connect(self._on_options_changed)
        self.seed.seed_reset.connect(self._on_seed_reset)

    def _on_options_changed(self) -> None:
        self.options_changed.emit(self.get_options())

    def _on_scale_changed(self) -> None:
        scale = self.map_size.get_scale()
        self.scale_changed.emit(scale)

    def _on_seed_reset(self) -> None:
        self.seed_reset.emit()

    def get_options(self) -> dict:
        """Get all options."""
        width, height = self.map_size.get_size()
        return {
            'width': width,
            'height': height,
            'scale': self.map_size.get_scale(),
            'algorithm': self.algorithm.get_algorithm(),
            'seed': self.seed.get_seed(),
            'params': self.algorithm.get_params(),
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
        layout.addSpacerItem(QSpacerItem(80, 1))
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

    state_changed = Signal(str, bool)

    def __init__(self, name: str, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout()
        layout.setSpacing(8)
        layout.setMargin(0)

        self.check = QCheckBox()
        self.check.setChecked(True)
        self.name = QLabel(name)

        layout.addWidget(self.check)
        layout.addWidget(self.name)
        layout.addStretch()

        self.setLayout(layout)

        self.check.stateChanged.connect(self._on_state_changed)

    def _on_state_changed(self, state: int) -> None:
        self.state_changed.emit(self.name.text(), bool(state))


class LayersWidget(QWidget):
    """Map Visualizer layers widget."""

    layer_state_changed = Signal(str, bool)

    def __init__(self, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)
        self.setFixedWidth(200)

        layout.addWidget(QLabel('Layers:'))
        layout.addSpacerItem(QSpacerItem(1, 10))
        self.layers = []
        for layer in reversed(list(MAP_LAYERS.keys())):
            if layer == 'base':
                continue
            item = LayersItem(layer)
            self.layers.append(item)
            layout.addWidget(item)
            item.state_changed.connect(self._on_layer_state_changed)
        layout.addStretch()

        self.setLayout(layout)

    def _on_layer_state_changed(self, name: str, checked: bool) -> None:
        self.layer_state_changed.emit(name, checked)


class ImageWidget(QWidget):
    """Widget to display the map image."""
    def __init__(self, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        self.img = None
        self.pixmap = None
        self.layers = {n: True for n in MAP_LAYERS.keys()}
        self.show()

    def draw_map(self, game_map: Map, scale_factor: int) -> None:
        """Draw the map to an image."""
        img = QImage(game_map.width, game_map.height, QImage.Format_RGB32)

        for cell in game_map:
            color = self._get_cell_color(cell)
            img.setPixel(cell.x, cell.y, color)
        self.img = img.scaled(game_map.width * scale_factor,
                              game_map.height * scale_factor,
                              Qt.KeepAspectRatio)
        self.pixmap = QPixmap.fromImage(self.img)
        self.setMinimumSize(self.pixmap.width(), self.pixmap.height())
        self.setMaximumSize(self.pixmap.width(), self.pixmap.height())

    def save(self, filename: str) -> None:
        """Save the image as a file.

        Args:
            filename: Path to the output file.

        """
        if self.img:
            self.img.save(filename)
        else:
            msg_error('No image to save!', self)

    def paintEvent(self, *args: Any, **kwargs: Any) -> None:
        """Override paint method; draw this widget."""
        if self.pixmap:
            painter = QPainter(self)
            painter.setViewport(0, 0, self.width(), self.height())
            painter.setWindow(0, 0, self.width(), self.height())
            painter.drawPixmap(0, 0, self.pixmap)
            painter.end()

    def set_layer(self, name: str, enabled: bool) -> None:
        """Set a particular layer to enabled or disabled."""
        self.layers[name] = enabled

    def _get_cell_color(self, cell: MapCell) -> qRgb:
        color = MAP_LAYERS['base']
        # color gets replaced by each layer in order until the highest wins
        for layer_name, layer_color in MAP_LAYERS.items():
            if self.layers[layer_name]:
                if hasattr(cell, layer_name) and getattr(cell, layer_name):
                    color = layer_color
        return color


class CentralWidget(QWidget):
    """Map Visualizer central widget."""

    options_changed = Signal(dict)
    scale_changed = Signal(int)
    seed_reset = Signal()

    def __init__(self, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        self.game_map = None
        self.scale_factor = 1
        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)

        self.layers = LayersWidget()
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName('image')
        self.image_widget = ImageWidget()
        self.scroll_area.setWidget(self.image_widget)
        self.options = OptionsWidget()

        layout.addWidget(self.layers)
        layout.addWidget(self.scroll_area)
        layout.addWidget(self.options)

        self.setLayout(layout)

        self.layers.layer_state_changed.connect(self._on_layer_state_changed)
        self.options.options_changed.connect(self._on_options_changed)
        self.options.scale_changed.connect(self._on_scale_changed)
        self.options.seed_reset.connect(self._on_seed_reset)

    def set_map(self, game_map: Map, scale_factor: int) -> None:
        """Set our map."""
        self.game_map = game_map
        self.scale_factor = scale_factor
        self.image_widget.draw_map(self.game_map, self.scale_factor)
        self.image_widget.repaint()

    def save_image(self, filename: str) -> None:
        """Save the current map to a file."""
        self.image_widget.save(filename)

    def get_options(self) -> dict:
        """Get options."""
        return self.options.get_options()

    def _on_layer_state_changed(self, name: str, enabled: bool) -> None:
        self.image_widget.set_layer(name, enabled)
        self.image_widget.draw_map(self.game_map, self.scale_factor)
        self.image_widget.repaint()

    def _on_options_changed(self, options: Mapping) -> None:
        self.options_changed.emit(options)

    def _on_scale_changed(self, scale: int) -> None:
        self.scale_changed.emit(scale)

    def _on_seed_reset(self) -> None:
        self.seed_reset.emit()


class MapVisualizer(QWidget):
    """Map Visualizer parent widget."""

    def __init__(self, map_config: Mapping, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        self.map_config: MutableMapping = map_config
        self.setWindowTitle('Map Visualizer')
        self.setMinimumSize(MIN_WIDTH, MIN_HEIGHT)
        self.setObjectName('MainApp')
        self.game_map = None

        RNGCache.init(self.map_config['parent_seed'])

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setMargin(10)

        self.central = CentralWidget()
        self.buttons = ButtonsWidget()

        layout.addWidget(self.central)
        layout.addWidget(self.buttons)
        self.setLayout(layout)

        self.buttons.generate_map.connect(self._on_generate_map)
        self.buttons.save_image.connect(self._on_save_image)
        self.central.options_changed.connect(self._on_options_changed)
        self.central.scale_changed.connect(self._on_scale_changed)
        self.central.seed_reset.connect(self._on_seed_reset)

        self.buttons.generate_button.setFocus()
        self._on_options_changed(self.central.get_options())

    def _on_generate_map(self) -> None:
        try:
            map_class = ALGORITHMS[self.map_config['algorithm']]['class']
        except KeyError:
            msg_error(f'No such map class: "{self.map_config.get("algorithm", "")}"', self)
            return
        self.game_map = map_class(self.map_config['max_tiles_w'],
                                  self.map_config['max_tiles_h'],
                                  seed=self.map_config['seed'],
                                  config=self.map_config.get('params'))
        self.game_map.create()
        self.central.set_map(self.game_map, self.map_config.get('gui_scale', 1))

    def _on_save_image(self) -> None:
        filename = QFileDialog().getSaveFileName(
            self, 'Save Map As', str(Path('~/Downloads').expanduser()), 'Image Files (*.png)')[0]
        self.central.save_image(filename)

    def _on_options_changed(self, opts: Mapping) -> None:
        self.map_config['max_tiles_w'] = opts['width']
        self.map_config['max_tiles_h'] = opts['height']
        self.map_config['gui_scale'] = opts['scale']
        self.map_config['algorithm'] = opts['algorithm']
        self.map_config['seed'] = opts['seed']
        self.map_config['params'] = opts['params']

    def _on_scale_changed(self, scale: int):
        if self.game_map:
            self.map_config['gui_scale'] = scale
            self.central.set_map(self.game_map, scale)

    def _on_seed_reset(self) -> None:
        RNGCache.init(self.map_config['parent_seed'])
        self._on_generate_map()


def main() -> int:
    """ Main function """
    try:
        parent_seed = sys.argv[1]
    except IndexError:
        parent_seed = 'MapVisualizer'
    app = QApplication(sys.argv)
    with STYLESHEET.open() as f:
        app.setStyleSheet(f.read())
    with CONFIG_FILE.open() as f:
        map_config = json.load(f)['map']
    map_config['parent_seed'] = parent_seed
    map_visualizer = MapVisualizer(map_config)
    map_visualizer.show()
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
