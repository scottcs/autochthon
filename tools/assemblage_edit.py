"""Assemblage editor."""
from copy import deepcopy
import json
from pathlib import Path
import re
import sys
from typing import Optional, List, Sequence, Mapping, MutableMapping

from PySide2.QtCore import Qt, Signal
from PySide2.QtGui import QImage, QPainter, QColor
from PySide2.QtWidgets import (QAbstractItemView, QDialog, QDialogButtonBox, QScrollArea,
                               QFileDialog, QHBoxLayout, QLabel, QListWidget,
                               QListWidgetItem, QMessageBox, QSpacerItem, QVBoxLayout, QWidget)

from game.utils.factory import get_component_class, convert_datum
from tools.widgets import (msg_error, ToolApp, ToolMutableComboBox, ToolLineEdit, ToolPushButton,
                           ComponentPanel)

DATA_DIR = Path('data/assemblage')
TILE_IDS_FILE = Path('static/img/oryx_ur/tile_ids.json')
COMPONENT_DIR = Path('game/component')
COMPONENT_RE = re.compile(r'(?<=^class )\w+')
IGNORE_COMPONENT_PREFIXES = ('Base', 'GUT')

with TILE_IDS_FILE.open() as tile_ids_file_handle:
    TILE_IDS = json.load(tile_ids_file_handle)


class RenderWidget(QWidget):
    """Render widget."""

    def __init__(self, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        self.setMinimumSize(32, 48)
        self.setMaximumSize(32, 48)
        self.tile_id = None
        self.color = None
        self.sprite = None

    def clear_sprite(self) -> None:
        """Clear the sprite."""
        self.tile_id = None
        self.color = None
        self.sprite = None
        self.update()
        self.repaint()

    def update_tile(self, tile_id: str, color: str) -> None:
        """Update the rendered tile."""
        try:
            tile_id = int(tile_id)
        except ValueError:
            for id_, data in TILE_IDS.items():
                if data['name'] == tile_id:
                    tile_id = id_
                    break
        if str(tile_id) not in TILE_IDS:
            msg_error(f'Tile id not found: {tile_id}', self)
            return
        self.tile_id = str(tile_id)
        if color.startswith('Palette.'):
            try:
                self.color = convert_datum(color)
            except AttributeError:
                msg_error(f'Unknown color: {color}', self)
                return
        else:
            msg_error(f'Unknown color: {color}', self)
            return
        self.set_sprite()
        self.update()
        self.repaint()

    def set_sprite(self) -> None:
        """Draw the image."""
        data = TILE_IDS[self.tile_id]
        tileset = Path(data['tileset'])
        tile = data['tiles'][0]
        with tileset.open() as f:
            tileset_data = json.load(f)
        frame = None
        for frame_name, frame_data in tileset_data['frames'].items():
            if frame_name == tile:
                frame = frame_data['frame']
                break
        if not frame:
            msg_error(f'Could not find frame for {tile}', self)
            return
        sheet = QImage(str(tileset.parent / tileset_data['meta']['image']))
        self.sprite = sheet.copy(frame['x'], frame['y'], frame['w'], frame['h'])

    def paintEvent(self, event):
        """Called when this widget should be painted."""
        if not self.sprite:
            return

        mask = QImage(self.sprite)
        painter = QPainter()

        painter.begin(mask)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(mask.rect(), QColor(self.color))
        painter.end()

        painter.begin(self)
        painter.fillRect(self.rect(), Qt.black)
        painter.drawImage(8, 12, mask)
        painter.end()


class FileLoadSave(QWidget):
    """File load/save line."""

    file_loaded = Signal(dict)

    def __init__(self, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        self.filename = None
        self.data = {}
        self.original_json = None
        self.original_name = None

        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)

        self.edit = ToolLineEdit('File:')
        self.edit.disable()

        self.load_button = ToolPushButton('Load')
        self.save_button = ToolPushButton('Save')
        self.save_button.setDisabled(True)

        layout.addWidget(self.edit)
        layout.addSpacerItem(QSpacerItem(4, 0))
        layout.addWidget(self.load_button)
        layout.addWidget(self.save_button)
        self.setLayout(layout)

        self.load_button.clicked.connect(self._on_load)
        self.save_button.clicked.connect(self._on_save)

    def _on_load(self) -> None:
        if self.save_button.isEnabled():
            message_box = QMessageBox()
            message_box.setText('The document has been modified.')
            message_box.setInformativeText('Do you want to save your changes?')
            message_box.setStandardButtons(
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            message_box.setDefaultButton(QMessageBox.Save)
            ret = message_box.exec_()
            if ret == QMessageBox.Save:
                if not self._on_save():
                    return
            elif ret == QMessageBox.Cancel:
                return
            elif ret == QMessageBox.Discard:
                pass
            else:
                # should never be reached
                return

        filename = QFileDialog().getOpenFileName(
            self, 'Open Assemblage', str(DATA_DIR), 'Assemblage Files (*.json)')[0]
        if filename:
            self.filename = Path(filename)
            text = filename.split(f'{DATA_DIR}/')[-1]
            self.edit.set_text(text)
            self._load_file()

    def _on_save(self) -> bool:
        if not self.data:
            msg_error('No data to save!', self)
            return False
        for key in self.data.keys():
            if key == '':
                msg_error('You must give all assemblages a name!', self)
                return False
            if not self.data[key]:
                msg_error('There is no component data to save!', self)
                return False
        filename = QFileDialog().getSaveFileName(
            self, 'Save Assemblage As', str(DATA_DIR), 'Assemblage Files (*.json)')[0]
        if filename:
            self.filename = Path(filename)
            text = filename.split(f'{DATA_DIR}/')[-1]
            self.edit.set_text(text)
            self._save_file()
            return True
        return False

    def _save_file(self) -> None:
        self.save_button.setDisabled(True)
        self.save_button.repaint()
        with self.filename.open('w') as f:
            json.dump(self.data, f, indent=2)

    def _load_file(self) -> None:
        self.save_button.setDisabled(True)
        self.save_button.repaint()
        with self.filename.open() as f:
            self.data = json.load(f)
            self.original_json = json.dumps(self.data, sort_keys=True)
            for key in self.data.keys():
                self.original_name = key
                break  # only one object per file
        if self.data:
            self.file_loaded.emit(self.data)

    def _enable_save_button(self) -> None:
        self.save_button.setDisabled(False)
        self.save_button.repaint()

    def update_data(self, data: MutableMapping) -> None:
        """Update the internal representation of the data."""
        new_json = json.dumps(data, sort_keys=True)
        if self.original_json != new_json:
            self._enable_save_button()
            self.data = data
        else:
            self.save_button.setDisabled(True)
        self.save_button.repaint()

    def update_assemblage_name(self, name: str) -> None:
        """Update the assemblage name in our data."""
        if name:
            new_data = {}
            for value in self.data.values():
                new_data[name] = value
                break  # should only be one value
            self.update_data(new_data)


class GetComponentDialog(QDialog):
    """Choose a component."""
    components = []

    def __init__(self, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        self.setMinimumSize(400, 600)
        self._cache_component_list()

        layout = QVBoxLayout()

        self.components_list = QListWidget()
        self.components_list.addItems(self.components)
        self.components_list.setSelectionMode(QAbstractItemView.ExtendedSelection)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
                                   Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(QLabel('Add Components: '))
        layout.addWidget(self.components_list)
        layout.addWidget(buttons)
        self.setLayout(layout)

    @classmethod
    def _cache_component_list(cls) -> None:
        if not cls.components:
            components = []
            for filename in COMPONENT_DIR.glob('*.py'):
                component_family = filename.stem
                with filename.open() as f:
                    for line in f.readlines():
                        found = COMPONENT_RE.search(line)
                        if found:
                            name = found.group(0)
                            if not any([name.startswith(p) for p in IGNORE_COMPONENT_PREFIXES]):
                                components.append(f'{component_family}.{name}')
            cls.components = sorted(components)

    def get(self) -> List[str]:
        """Show the dialog and get the component name."""
        result = self.exec_()
        components = []
        if result == QDialog.Accepted:
            for selected in self.components_list.selectedItems():
                components.append(selected.text())
        return components


class ComponentList(QWidget):
    """Component list widget."""
    selection_changed = Signal(str)
    component_removed = Signal(str)
    components_added = Signal(list)

    def __init__(self, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(0)
        header_layout.setMargin(0)

        self.add_button = ToolPushButton('+')
        self.remove_button = ToolPushButton('-')
        self.component_list = QListWidget(self)

        header_layout.addWidget(QLabel('Components'))
        header_layout.addStretch()
        header_layout.addWidget(self.add_button)
        header_layout.addWidget(self.remove_button)

        layout.addLayout(header_layout)
        layout.addWidget(self.component_list)
        self.setLayout(layout)

        self.add_button.clicked.connect(self._on_add)
        self.remove_button.clicked.connect(self._on_remove)
        self.component_list.itemSelectionChanged.connect(self._on_selection)

    def _on_add(self) -> None:
        component_names = GetComponentDialog().get()
        if component_names:
            self.components_added.emit(component_names)

    def _on_remove(self) -> None:
        try:
            selected: QListWidgetItem = self.component_list.selectedItems()[0]
            self.component_list.takeItem(self.component_list.row(selected))
            self.component_removed.emit(selected.text())
        except IndexError:
            pass

    def _on_selection(self) -> None:
        try:
            selected: QListWidgetItem = self.component_list.selectedItems()[0]
            self.selection_changed.emit(selected.text())
        except IndexError:
            pass

    def update_items(self, items: Sequence) -> None:
        """Update the items in the list."""
        self.component_list.clear()
        self.component_list.addItems(items)
        self.sizeHint()
        self.update()
        self.repaint()


class ComponentPane(QWidget):
    """Component Pane widget."""

    data_changed = Signal(dict)

    def __init__(self, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        self.data = {}
        self.selected = None
        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)
        details_layout = QVBoxLayout()
        details_layout.setSpacing(0)
        details_layout.setMargin(0)

        self.component_list = ComponentList(self)
        details_label = QLabel('Component Details')
        details_label.setMinimumHeight(23)
        details_layout.addWidget(details_label)
        self.params_widget = QScrollArea()
        self.params_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        details_layout.addWidget(self.params_widget)

        layout.addWidget(self.component_list)
        layout.addSpacerItem(QSpacerItem(4, 1))
        layout.addLayout(details_layout)

        self.setLayout(layout)

        self.component_list.selection_changed.connect(self._on_selection_changed)
        self.component_list.component_removed.connect(self._on_component_removed)
        self.component_list.components_added.connect(self._on_components_added)

    def _on_selection_changed(self, selected: str) -> None:
        self.selected = selected
        self.data.setdefault(selected, {})
        if self.params_widget.widget() is not None:
            self.params_widget.widget().parameters_changed.disconnect(self._on_parameters_changed)
        component_class = get_component_class(selected)
        widget = ComponentPanel(selected, component_class, data=self.data[selected])
        widget.parameters_changed.connect(self._on_parameters_changed)
        self.params_widget.setWidget(widget)

    def _on_parameters_changed(self):
        params = self.params_widget.widget().get_parameters()
        if self.selected:
            self.data[self.selected] = params
            self.data_changed.emit({'Components': self.data})

    def _on_component_removed(self, component_name: str) -> None:
        try:
            del self.data[component_name]
            self.data_changed.emit({'Components': self.data})
        except KeyError:
            msg_error(f'Attempt to delete a component that does not exist: {component_name}', self)
        if self.component_list.component_list.count() == 0:
            self.hide_data()

    def _on_components_added(self, component_names: Sequence[str]) -> None:
        for component_name in component_names:
            self.data.setdefault(component_name, {})
        self.data_changed.emit({'Components': self.data})
        self.component_list.update_items(sorted(self.data.keys()))
        self.update()

    def update_data(self, data: Mapping) -> None:
        """Update the data in this widget."""
        self.data = data['Components']
        self.component_list.update_items(sorted(self.data.keys()))
        self.sizeHint()
        self.update()
        self.repaint()

    def hide_data(self) -> None:
        """Hide the data pane."""
        self.params_widget.takeWidget()


class AssemblageEditor(QWidget):
    """Assemblage editor parent widget."""

    def __init__(self, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        self.assemblage_data: dict = {}
        self.setWindowTitle('Assemblage Editor')
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(10)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(0)
        header_layout.setMargin(0)

        header_right_layout = QVBoxLayout()
        header_right_layout.setSpacing(0)
        header_right_layout.setMargin(0)

        self.render_widget = RenderWidget()
        self.file_widget = FileLoadSave()
        self.assemblage_name = ToolMutableComboBox('Assemblage Name:', sort=True)
        self.component_widget = ComponentPane()

        header_right_layout.addWidget(self.file_widget)
        header_right_layout.addWidget(self.assemblage_name)
        header_layout.addWidget(self.render_widget)
        header_layout.addSpacerItem(QSpacerItem(8, 0))
        header_layout.addLayout(header_right_layout)
        layout.addLayout(header_layout)
        layout.addWidget(self.component_widget)

        self.setLayout(layout)

        self.assemblage_name.selection_changed.connect(self._on_assemblage_name_changed)
        self.assemblage_name.duplicate_item.connect(self._on_assemblage_duplicate)
        self.file_widget.file_loaded.connect(self._on_file_loaded)
        self.component_widget.data_changed.connect(self._on_data_changed)

    def _on_file_loaded(self, data: Mapping) -> None:
        self.assemblage_data = data
        self.render_widget.clear_sprite()
        self.assemblage_name.clear()
        self.assemblage_name.add_items(list(data.keys()))
        self._on_assemblage_name_changed()

    def _on_assemblage_name_changed(self) -> None:
        name = self.assemblage_name.text()
        self.assemblage_data.setdefault(name, {'Components': {}})
        self.component_widget.update_data(self.assemblage_data[name])
        self._update_render_widget(self.assemblage_data[name])
        self.component_widget.hide_data()
        self.update()
        self.repaint()

    def _on_assemblage_duplicate(self, old: str) -> None:
        name = self.assemblage_name.text()
        self.assemblage_data[name] = deepcopy(self.assemblage_data[old])
        self._on_assemblage_name_changed()

    def _on_data_changed(self, data: Mapping) -> None:
        self.assemblage_data[self.assemblage_name.text()] = data
        self.file_widget.update_data(self.assemblage_data)
        self._update_render_widget(data)

    def _update_render_widget(self, data: Mapping) -> None:
        self.render_widget.clear_sprite()
        components = data.get('Components', {})
        renderable = components.get('render.Renderable', None)
        if renderable:
            try:
                self.render_widget.update_tile(renderable['tile_id'], renderable['tint'])
            except KeyError:
                # Probably haven't finished editing
                pass


def main() -> int:
    """ Main function """
    app = ToolApp(sys.argv)
    assemblage_edit = AssemblageEditor()
    assemblage_edit.show()
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
