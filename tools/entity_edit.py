"""Entity editor."""
import sys
from typing import Optional

from PySide2.QtWidgets import (QApplication, QHBoxLayout, QLabel, QLineEdit, QListWidget,
                               QPushButton, QScrollArea, QSpacerItem, QVBoxLayout, QWidget)


class FileLoadSave(QWidget):
    """File load/save line."""

    def __init__(self, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)

        self.label = QLabel('File:')
        self.edit = QLineEdit()
        self.load_button = QPushButton('Load')
        self.save_as_button = QPushButton('Save As...')
        self.save_button = QPushButton('Save')

        layout.addWidget(self.label)
        layout.addWidget(self.edit)
        layout.addWidget(self.load_button)
        layout.addWidget(self.save_as_button)
        layout.addWidget(self.save_button)
        self.setLayout(layout)

        self.load_button.clicked.connect(self._on_load)
        self.save_as_button.clicked.connect(self._on_save_as)
        self.save_button.clicked.connect(self._on_save)

    def _on_load(self) -> None:
        print('on load')
        print(self.edit.text())

    def _on_save_as(self) -> None:
        print('on save as')
        print(self.edit.text())

    def _on_save(self) -> None:
        print('on save')
        print(self.edit.text())


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

        self.component_list.addItems(['blah' for _ in range(40)])
        layout.addLayout(header_layout)
        layout.addWidget(self.component_list)
        self.setLayout(layout)

        self.add_button.clicked.connect(self._on_add)
        self.remove_button.clicked.connect(self._on_remove)

    def _on_add(self) -> None:
        print('on add')

    def _on_remove(self) -> None:
        print('on remove')


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


class EntityEditor(QWidget):
    """Entity editor parent widget."""

    def __init__(self, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        self.setWindowTitle('Entity Editor')

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(10)
        file_widget = FileLoadSave(self)
        component_widget = ComponentPane(self)

        layout.addWidget(file_widget)
        layout.addWidget(component_widget)

        self.setLayout(layout)


def main() -> int:
    """ Main function """
    app = QApplication(sys.argv)
    entity_edit = EntityEditor()
    entity_edit.show()
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
