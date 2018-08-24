"""Entity editor."""
import json
from pathlib import Path
import sys
from typing import Optional, Any

from PySide2.QtCore import Qt, Signal
from PySide2.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel, QLineEdit,
                               QListWidget, QListWidgetItem, QMessageBox, QPushButton, QSpacerItem,
                               QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget)

from game.utils.factory import get_component_class

DATA_DIR = Path('data/entities')


def msg_error(msg: str, parent: Optional[QWidget]=None) -> None:
    """Show an error message."""
    QMessageBox().critical(parent, 'Error!', msg)


class FileLoadSave(QWidget):
    """File load/save line."""

    file_loaded = Signal(dict)

    def __init__(self, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        self.filename = None
        self.data = None
        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)

        self.label = QLabel('File:')
        self.edit = QLineEdit()
        self.edit.setDisabled(True)
        self.load_button = QPushButton('Load')
        self.save_as_button = QPushButton('Save As...')
        self.save_button = QPushButton('Save')

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
        print('on save as')
        print(self.edit.text())

    def _on_save(self) -> None:
        print('on save')
        print(self.edit.text())

    def _load_file(self) -> None:
        with self.filename.open() as f:
            self.data = json.load(f)
        if self.data:
            self.file_loaded.emit(self.data)


class ComponentList(QWidget):
    """Component list widget."""
    selection_changed = Signal(str)

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
        self.component_list.itemClicked.connect(self._on_selection)

    def _on_add(self) -> None:
        print('on add')

    def _on_remove(self) -> None:
        print('on remove')

    def _on_selection(self, item: QListWidgetItem) -> None:
        self.selection_changed.emit(item.text())

    def update_items(self, items: list) -> None:
        """Update the items in the list."""
        self.component_list.clear()
        self.component_list.addItems(items)


class ComponentDetailsTable(QTableWidget):
    """Component details widget."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.setColumnCount(1)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().hide()

    def update_data(self, component_name: str) -> None:
        """Refresh the list."""
        self.clear()
        self.setRowCount(100)
        component_class = get_component_class(component_name)
        try:
            annotations = component_class.__init__.__annotations__
        except AttributeError:
            print(f'Could not find annotations for {component_name}')
            annotations = {}
        row = 0
        for arg, arg_type in annotations.items():
            if arg == 'return':
                continue
            self.setVerticalHeaderItem(row, QTableWidgetItem(arg))
            self.setItem(row, 0, QTableWidgetItem('blah'))
            row += 1
        self.setRowCount(row)


class ComponentPane(QWidget):
    """Component Pane widget."""

    def __init__(self, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        self.data = {}
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

    def _on_selection_changed(self, selected: str) -> None:
        self.details_widget.update_data(selected)

    def update_data(self, data: dict) -> None:
        """Update the data in this widget."""
        self.data = data['Components']
        self.component_list.update_items(sorted(self.data.keys()))
        self.update()


class EntityEditor(QWidget):
    """Entity editor parent widget."""

    def __init__(self, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        self.setWindowTitle('Entity Editor')

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(10)
        file_widget = FileLoadSave(self)

        name_layout = QHBoxLayout()
        self.entity_name = QLineEdit()
        name_layout.addWidget(QLabel('Entity name:'))
        name_layout.addWidget(self.entity_name)
        self.component_widget = ComponentPane(self)

        layout.addWidget(file_widget)
        layout.addLayout(name_layout)
        layout.addWidget(self.component_widget)

        self.setLayout(layout)

        file_widget.file_loaded.connect(self._on_file_changed)

    def _on_file_changed(self, data: dict) -> None:
        for name, entity_data in data.items():
            self.entity_name.setText(name)
            self.component_widget.update_data(entity_data)
            break  # only one entity per file


def main() -> int:
    """ Main function """
    app = QApplication(sys.argv)
    entity_edit = EntityEditor()
    entity_edit.show()
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
