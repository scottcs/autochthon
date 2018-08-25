"""Entity editor."""
import json
from inspect import signature
from pathlib import Path
import re
import sys
from typing import Optional, Any, List

from PySide2.QtCore import Qt, Signal
from PySide2.QtWidgets import (QApplication, QAbstractItemView, QDialog, QDialogButtonBox,
                               QFileDialog, QHBoxLayout, QLabel, QLineEdit, QListWidget,
                               QListWidgetItem, QMessageBox, QPushButton, QSpacerItem,
                               QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

from game.utils.factory import get_component_class

DATA_DIR = Path('data/entities')
COMPONENT_DIR = Path('game/component')
COMPONENT_RE = re.compile(r'(?<=^class )\w+')
IGNORE_COMPONENT_PREFIXES = ('Base', 'GUT')


def msg_error(msg: str, parent: Optional[QWidget]=None) -> None:
    """Show an error message."""
    QMessageBox().critical(parent, 'Error!', msg)


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

        self.label = QLabel('File:')
        self.edit = QLineEdit()
        self.edit.setDisabled(True)
        self.load_button = QPushButton('Load')
        self.save_as_button = QPushButton('Save As...')
        self.save_button = QPushButton('Save')
        self.save_button.setDisabled(True)

        self.load_button.setFocusPolicy(Qt.NoFocus)
        self.save_as_button.setFocusPolicy(Qt.NoFocus)
        self.save_button.setFocusPolicy(Qt.NoFocus)

        layout.addWidget(self.label)
        layout.addWidget(self.edit)
        layout.addSpacerItem(QSpacerItem(4, 0))
        layout.addWidget(self.load_button)
        layout.addWidget(self.save_as_button)
        layout.addWidget(self.save_button)
        self.setLayout(layout)

        self.load_button.clicked.connect(self._on_load)
        self.save_as_button.clicked.connect(self._on_save_as)
        self.save_button.clicked.connect(self._on_save)

    def _on_load(self) -> None:
        filename = QFileDialog().getOpenFileName(
            self, 'Open Entity', str(DATA_DIR), 'Entity Files (*.json)')[0]
        if filename:
            self.filename = Path(filename)
            text = filename.split(f'{DATA_DIR}/')[-1]
            self.edit.setText(text)
            self._load_file()

    def _on_save_as(self) -> None:
        if not self.data:
            msg_error('No data to save!', self)
            return
        for key in self.data.keys():
            if key == '':
                msg_error('You must give the entity a name!', self)
                return
            if key == self.original_name:
                msg_error(f'You must change the entity name! ({self.original_name})', self)
                return
            if not self.data[key]:
                msg_error('There is no component data to save!', self)
                return
        filename = QFileDialog().getSaveFileName(
            self, 'Save Entity As', str(DATA_DIR), 'Entity Files (*.json)')[0]
        if filename:
            self.filename = Path(filename)
            text = filename.split(f'{DATA_DIR}/')[-1]
            self.edit.setText(text)
            self._save_file()

    def _on_save(self) -> None:
        self._save_file()

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
        if self.edit.text():
            self.save_button.setDisabled(False)
            self.save_button.repaint()

    def update_data(self, data: dict) -> None:
        """Update the internal representation of the data."""
        new_json = json.dumps(data, sort_keys=True)
        if self.original_json != new_json:
            self._enable_save_button()
            self.data = data
        else:
            self.save_button.setDisabled(True)
        self.save_button.repaint()

    def update_entity_name(self, name: str) -> None:
        """Update the entity name in our data."""
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

        layout.addWidget(QLabel('Add Components:'))
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

        self.add_button = QPushButton('+')
        self.remove_button = QPushButton('-')
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

    def update_items(self, items: list) -> None:
        """Update the items in the list."""
        self.component_list.clear()
        self.component_list.addItems(items)
        self.sizeHint()
        self.update()
        self.repaint()


class ComponentDetailsTable(QTableWidget):
    """Component details widget."""
    data_changed = Signal(dict)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.data = {}
        self.signature = None
        self.setColumnCount(1)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().hide()
        self.itemChanged.connect(self._on_item_changed)

    def _on_item_changed(self, item: QTableWidgetItem) -> None:
        param_name = self.verticalHeaderItem(item.row()).text()
        old_data = str(self.data.get(param_name, ''))
        new_data = item.text()
        if old_data != new_data:
            param = self.signature.parameters[param_name]
            if param_name in self.data and new_data in ('', 'None'):
                if param.default is param.empty:
                    msg_error(f'Parameter "{param_name}" is required!', self)
                    self.refresh()
                del self.data[param_name]
            else:
                if new_data.lower() == 'true':
                    self.data[param_name] = True
                elif new_data.lower() == 'false':
                    self.data[param_name] = False
                else:
                    try:
                        self.data[param_name] = int(new_data)
                    except ValueError:
                        try:
                            self.data[param_name] = float(new_data)
                        except ValueError:
                            self.data[param_name] = new_data
            self.data_changed.emit(self.data)

    def update_data(self, component_name: str, component_data: dict) -> None:
        """Refresh the list."""
        self.data = component_data
        component_class = get_component_class(component_name)
        self.signature = signature(component_class)
        self.refresh()

    def clear(self) -> None:
        """Clear the table."""
        super().clear()
        self.setRowCount(0)

    def refresh(self) -> None:
        """Refresh data."""
        self.clear()
        self.setRowCount(100)
        row = 0
        for param_name, param in self.signature.parameters.items():
            header_item = QTableWidgetItem(param_name)
            header_item.setToolTip(str(param.annotation))
            self.setVerticalHeaderItem(row, header_item)
            item = QTableWidgetItem(str(self.data.get(param_name, '')))
            if param.default is not param.empty:
                item.setBackgroundColor('#f8f8f0')
            self.setItem(row, 0, item)
            row += 1
        self.setRowCount(row)


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
        details_label = QLabel('Component Details:')
        details_label.setMinimumHeight(32)
        details_layout.addWidget(details_label)
        self.details_widget = ComponentDetailsTable()
        details_layout.addWidget(self.details_widget)

        layout.addWidget(self.component_list)
        layout.addSpacerItem(QSpacerItem(4, 1))
        layout.addLayout(details_layout)

        self.setLayout(layout)

        self.component_list.selection_changed.connect(self._on_selection_changed)
        self.component_list.component_removed.connect(self._on_component_removed)
        self.component_list.components_added.connect(self._on_components_added)
        self.details_widget.data_changed.connect(self._on_data_changed)

    def _on_selection_changed(self, selected: str) -> None:
        self.selected = selected
        self.details_widget.update_data(selected, self.data[selected])

    def _on_component_removed(self, component_name: str) -> None:
        try:
            del self.data[component_name]
            self.data_changed.emit({'Components': self.data})
        except KeyError:
            msg_error(f'Attempt to delete a component that does not exist: {component_name}', self)
        if self.component_list.component_list.count() == 0:
            self.details_widget.clear()

    def _on_components_added(self, component_names: List[str]) -> None:
        for component_name in component_names:
            self.data.setdefault(component_name, {})
        self.data_changed.emit({'Components': self.data})
        self.component_list.update_items(sorted(self.data.keys()))

    def _on_data_changed(self, data: dict) -> None:
        if self.selected:
            self.data[self.selected] = data
            self.data_changed.emit({'Components': self.data})

    def update_data(self, data: dict) -> None:
        """Update the data in this widget."""
        self.data = data['Components']
        self.component_list.update_items(sorted(self.data.keys()))
        self.sizeHint()
        self.update()
        self.repaint()


class EntityEditor(QWidget):
    """Entity editor parent widget."""

    def __init__(self, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        self.setWindowTitle('Entity Editor')
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(10)
        self.file_widget = FileLoadSave(self)

        name_layout = QHBoxLayout()
        self.entity_name = QLineEdit()
        self.entity_name.setAttribute(Qt.WA_MacShowFocusRect, False)  # macOS only
        name_layout.addWidget(QLabel('Entity name:'))
        name_layout.addWidget(self.entity_name)
        self.component_widget = ComponentPane(self)

        layout.addWidget(self.file_widget)
        layout.addLayout(name_layout)
        layout.addWidget(self.component_widget)

        self.setLayout(layout)

        self.entity_name.editingFinished.connect(self._new_entity_name)
        self.file_widget.file_loaded.connect(self._on_file_loaded)
        self.component_widget.data_changed.connect(self._on_data_changed)

    def _on_file_loaded(self, data: dict) -> None:
        for name, entity_data in data.items():
            self.entity_name.setText(name)
            self.component_widget.update_data(entity_data)
            break  # only one entity per file
        self.component_widget.details_widget.clear()

    def _on_data_changed(self, data: dict) -> None:
        self.file_widget.update_data({self.entity_name.text(): data})

    def _new_entity_name(self) -> None:
        self.file_widget.update_entity_name(self.entity_name.text())
        self.entity_name.clearFocus()
        self.update()
        self.repaint()


def main() -> int:
    """ Main function """
    app = QApplication(sys.argv)
    entity_edit = EntityEditor()
    entity_edit.show()
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
