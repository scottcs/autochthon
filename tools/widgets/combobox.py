"""ComboBox widgets."""
from typing import Optional, Sequence

from PySide2.QtCore import Qt, Signal
from PySide2.QtWidgets import QComboBox, QWidget, QLabel, QHBoxLayout, QSpacerItem


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

    def add_items(self, items: Sequence) -> None:
        """Add items to the combobox."""
        self._combobox.addItems(items)

    def set_via_text(self, text: str) -> None:
        """Set the current selection that matches the given text."""
        self._combobox.setCurrentIndex(self._combobox.findText(text))

    def text(self) -> str:
        """Get the current text."""
        return self._combobox.currentText()

    def _on_current_index_changed(self) -> None:
        self.selection_changed.emit()
