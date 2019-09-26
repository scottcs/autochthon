"""ComboBox widgets."""
import typing

import PySide2.QtCore
import PySide2.QtWidgets

import tools.widgets.pushbutton


class ToolComboBox(PySide2.QtWidgets.QWidget):
    """Custom ComboBox."""

    selection_changed = PySide2.QtCore.Signal()

    def __init__(
        self,
        label: str,
        parent: typing.Optional[PySide2.QtWidgets.QWidget] = None,
        min_label_width: typing.Optional[int] = None,
        sort: bool = False,
    ) -> None:
        super().__init__(parent)
        self.name = label
        self._items = []
        self._sorted = sort
        self._label = PySide2.QtWidgets.QLabel(label)
        self._combobox = PySide2.QtWidgets.QComboBox()
        if min_label_width is not None:
            self._label.setMinimumWidth(min_label_width)
        self._setup_layout()
        self._combobox.currentIndexChanged.connect(self._on_current_index_changed)

    def _setup_layout(self) -> None:
        layout = PySide2.QtWidgets.QHBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)

        layout.addWidget(self._label)
        layout.addSpacerItem(PySide2.QtWidgets.QSpacerItem(4, 1))
        layout.addWidget(self._combobox, PySide2.QtCore.Qt.AlignLeft)

        self.setLayout(layout)

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

    def add_items(self, items: typing.Sequence[typing.Sequence[str]]) -> None:
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
        self._on_current_index_changed()

    def text(self) -> str:
        """Get the current text."""
        return self._combobox.currentText()

    def iter_texts(self) -> str:
        """Iterate through all of the text values in the combobox."""
        for idx in range(self._combobox.count()):
            yield self._combobox.itemText(idx)

    def reset(self) -> None:
        """Reset to default index."""
        self._combobox.setCurrentIndex(0)

    def _on_current_index_changed(self) -> None:
        self.selection_changed.emit()


class ToolMutableComboBox(ToolComboBox):
    """A combobox that can have things added and removed from it."""

    selection_changed = PySide2.QtCore.Signal()
    duplicate_item = PySide2.QtCore.Signal(str)

    def __init__(
        self, *args: typing.Any, hide_duplicate_button: bool = False, **kwargs: typing.Any
    ) -> None:
        self._hide_duplicate_button = hide_duplicate_button
        self._duplicate_button = tools.widgets.pushbutton.ToolPushButton("∞")
        self._add_button = tools.widgets.pushbutton.ToolPushButton("+")
        self._remove_button = tools.widgets.pushbutton.ToolPushButton("-")
        self._duplicate_button.clicked.connect(self._on_duplicate_item)
        self._add_button.clicked.connect(self._on_add_item)
        self._remove_button.clicked.connect(self._on_remove_item)
        super().__init__(*args, **kwargs)
        self._check_buttons()

    def _setup_layout(self) -> None:
        layout = PySide2.QtWidgets.QHBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)

        layout.addWidget(self._label)
        layout.addSpacerItem(PySide2.QtWidgets.QSpacerItem(4, 1))
        layout.addWidget(self._combobox, PySide2.QtCore.Qt.AlignLeft)
        layout.addSpacerItem(PySide2.QtWidgets.QSpacerItem(4, 1))
        if not self._hide_duplicate_button:
            layout.addWidget(self._duplicate_button)
        layout.addWidget(self._add_button)
        layout.addWidget(self._remove_button)

        self.setLayout(layout)

    def _check_buttons(self) -> None:
        if self._combobox.count() == 0:
            self._duplicate_button.setDisabled(True)
            self._remove_button.setDisabled(True)
        else:
            self._duplicate_button.setEnabled(True)
            self._remove_button.setEnabled(True)

    def add_items(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        """Add items to the combobox."""
        super().add_items(*args, **kwargs)
        self._check_buttons()

    def add_item(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        """Add a single item to the combobox."""
        super().add_item(*args, **kwargs)
        self._check_buttons()

    def clear(self) -> None:
        """Remove all items."""
        super().clear()
        self._check_buttons()

    def remove_item_by_text(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        """Remove an item with the given text."""
        super().remove_item_by_text(*args, **kwargs)
        self._check_buttons()

    def remove_item_by_index(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        """Remove an item with the given index."""
        super().remove_item_by_index(*args, **kwargs)
        self._check_buttons()

    def _on_duplicate_item(self) -> None:
        current = self.text()
        # noinspection PyCallByClass,PyArgumentList
        item, ok = PySide2.QtWidgets.QInputDialog.getText(
            self, "Duplicate Item", "Name of duplicate:", text=current
        )
        if ok and item != current:
            self.add_item(item)
            self.set_via_text(item)
            self.duplicate_item.emit(current)

    def _on_add_item(self) -> None:
        # noinspection PyCallByClass,PyArgumentList
        item, ok = PySide2.QtWidgets.QInputDialog.getText(
            self, "Add New Item", "Name of new item:"
        )
        if ok:
            self.add_item(item)
            self.set_via_text(item)

    def _on_remove_item(self) -> None:
        # noinspection PyCallByClass
        yes = PySide2.QtWidgets.QMessageBox.question(
            self,
            "Remove Item?",
            f'Are you sure you want to remove "{self.text()}"?',
            PySide2.QtWidgets.QMessageBox.StandardButtons(
                PySide2.QtWidgets.QMessageBox.Yes | PySide2.QtWidgets.QMessageBox.No
            ),
            PySide2.QtWidgets.QMessageBox.Yes,
        )
        if yes == PySide2.QtWidgets.QMessageBox.Yes:
            idx = self._combobox.currentIndex()
            self.remove_item_by_index(idx)
