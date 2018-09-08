"""ComboBox widgets."""
from typing import Optional, Sequence

from PySide2.QtCore import Qt, Signal
from PySide2.QtWidgets import QComboBox, QWidget, QLabel, QHBoxLayout, QSpacerItem, QInputDialog

from .pushbutton import ToolPushButton


class ToolComboBox(QWidget):
    """Custom ComboBox."""

    selection_changed = Signal()

    def __init__(self, label: str, parent: Optional[QWidget]=None,
                 min_label_width: Optional[int]=None) -> None:
        super().__init__(parent)
        self._label = QLabel(label)
        self._combobox = QComboBox()

        if min_label_width is not None:
            self._label.setMinimumWidth(min_label_width)

        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)

        layout.addWidget(self._label)
        layout.addSpacerItem(QSpacerItem(4, 1))
        layout.addWidget(self._combobox, Qt.AlignLeft)

        self.setLayout(layout)

        self._combobox.currentIndexChanged.connect(self._on_current_index_changed)

    def add_items(self, items: Sequence[str]) -> None:
        """Add items to the combobox."""
        self._combobox.addItems(items)

    def set_via_text(self, text: str) -> None:
        """Set the current selection that matches the given text."""
        self._combobox.setCurrentIndex(self._combobox.findText(text))

    def reset(self) -> None:
        """Reset to default index."""
        self._combobox.setCurrentIndex(0)

    def text(self) -> str:
        """Get the current text."""
        return self._combobox.currentText()

    def _on_current_index_changed(self) -> None:
        self.selection_changed.emit()


class ToolMutableComboBox(QWidget):
    """A combobox that can have things added and removed from it."""

    selection_changed = Signal()

    def __init__(self, label: str, parent: Optional[QWidget]=None,
                 min_label_width: Optional[int]=None, sort: bool=True) -> None:
        super().__init__(parent)
        self._items = []
        self._sorted = sort
        self._label = QLabel(label)
        self._combobox = QComboBox()
        self._add_button = ToolPushButton('+')
        self._remove_button = ToolPushButton('-')

        if min_label_width is not None:
            self._label.setMinimumWidth(min_label_width)

        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)

        layout.addWidget(self._label)
        layout.addSpacerItem(QSpacerItem(4, 1))
        layout.addWidget(self._combobox, Qt.AlignLeft)
        layout.addSpacerItem(QSpacerItem(4, 1))
        layout.addWidget(self._add_button)
        layout.addWidget(self._remove_button)

        self.setLayout(layout)

        self._combobox.currentIndexChanged.connect(self._on_current_index_changed)
        self._add_button.clicked.connect(self._on_add_item)
        self._remove_button.clicked.connect(self._on_remove_item)

    def _add_sorted_items(self) -> None:
        current = self._combobox.currentText()
        self._items.sort()
        self._clear_combobox()
        self._combobox.currentIndexChanged.disconnect(self._on_current_index_changed)
        self._combobox.addItems(self._items)
        if current:
            idx = self._combobox.findText(current)
            self._combobox.setCurrentIndex(idx)
        self._combobox.currentIndexChanged.connect(self._on_current_index_changed)

    def add_items(self, items: Sequence[str]) -> None:
        """Add items to the combobox."""
        self._items.extend(items)
        if self._sorted:
            self._add_sorted_items()
        else:
            self._combobox.addItems(items)

    def add_item(self, item: str) -> None:
        """Add a single item to the combobox."""
        self._items.append(item)
        if self._sorted:
            self._add_sorted_items()
        else:
            self._combobox.addItem(item)

    def clear(self) -> None:
        """Remove all items."""
        self._clear_combobox()
        self._items = []

    def _clear_combobox(self) -> None:
        self._combobox.currentIndexChanged.disconnect(self._on_current_index_changed)
        for i in range(self._combobox.count()):
            self._combobox.removeItem(0)
        self._combobox.currentIndexChanged.connect(self._on_current_index_changed)

    def remove_item_by_text(self, text: str) -> None:
        """Remove an item with the given text."""
        self._items.remove(text)
        idx = self._combobox.findText(text)
        self._combobox.removeItem(idx)

    def remove_item_by_index(self, idx: int) -> None:
        """Remove an item with the given index."""
        self._items.pop(idx)
        self._combobox.removeItem(idx)

    def set_via_text(self, text: str) -> None:
        """Set the current selection that matches the given text."""
        self._combobox.setCurrentIndex(self._combobox.findText(text))

    def text(self) -> str:
        """Get the current text."""
        return self._combobox.currentText()

    def iter_texts(self) -> str:
        """Iterate through all of the text values in the combobox."""
        for idx in range(self._combobox.count()):
            yield self._combobox.itemText(idx)

    def _on_current_index_changed(self, arg) -> None:
        self.selection_changed.emit()

    def _on_add_item(self) -> None:
        # noinspection PyCallByClass
        item, ok = QInputDialog.getText(self, 'Add New Item', 'Item:')
        if ok:
            self.add_item(item)
            self.set_via_text(item)

    def _on_remove_item(self) -> None:
        idx = self._combobox.currentIndex()
        self.remove_item_by_index(idx)
