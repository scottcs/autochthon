"""Entity editor."""
import json
from pathlib import Path
import sys
from typing import Optional

from PySide2.QtCore import Qt, Signal
from PySide2.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel, QLineEdit,
                               QListWidget, QMessageBox, QPushButton, QScrollArea, QSpacerItem,
                               QVBoxLayout, QWidget)

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

    def _on_add(self) -> None:
        print('on add')

    def _on_remove(self) -> None:
        print('on remove')

    def update_items(self, items: list) -> None:
        """Update the items in the list."""
        self.component_list.clear()
        self.component_list.addItems(items)


class ComponentDetailLine(QWidget):
    """Component detail line widget."""
    def __init__(self, label: str, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(2)

        self.label = QLabel(label)
        self.edit = QLineEdit()

        layout.addWidget(self.label)
        layout.addStretch()
        layout.addWidget(self.edit)

        self.setLayout(layout)


class ComponentDetails(QWidget):
    """Component Details widget."""
    def __init__(self, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        self.lines = []
        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setMargin(0)

        for i in range(15):
            self.lines.append(ComponentDetailLine(f'Item {i}', parent=self))

        self.setLayout(self.layout)
        self.refresh()

    def refresh(self):
        """Refresh the list."""
        for item in self.layout.children():
            self.layout.removeItem(item)
        for line in self.lines:
            self.layout.addWidget(line)


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
        self.details_widget = ComponentDetails()
        details_area = QScrollArea(self)
        details_area.setWidget(self.details_widget)
        details_layout.addWidget(details_area)

        layout.addWidget(self.component_list)
        layout.addSpacerItem(QSpacerItem(4, 1))
        layout.addLayout(details_layout)

        self.setLayout(layout)

    def update_data(self, data: dict) -> None:
        """Update the data in this widget."""
        self.data = data['Components']
        self.component_list.update_items(sorted(self.data.keys()))


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
