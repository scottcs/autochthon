"""Custom QLineEdit widget."""
from typing import Optional

from PySide2.QtCore import Qt, Signal
from PySide2.QtGui import QIntValidator
from PySide2.QtWidgets import QWidget, QLineEdit, QLabel, QHBoxLayout, QSpacerItem


class ToolLineEdit(QWidget):
    """Custom Line Edit."""

    editing_finished = Signal()

    def __init__(self, label: str, parent: Optional[QWidget]=None,
                 default_text: Optional[str]=None,
                 edit_width: Optional[int]=None,
                 min_label_width: Optional[int]=None) -> None:
        super().__init__(parent)
        self._label = QLabel(label)
        if min_label_width is not None:
            self._label.setMinimumWidth(min_label_width)

        self._edit = QLineEdit()
        self._edit.setAttribute(Qt.WA_MacShowFocusRect, False)  # macOS only
        if default_text:
            self._edit.setText(default_text)
        if edit_width:
            self._edit.setFixedWidth(edit_width)

        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)

        layout.addWidget(self._label)
        layout.addSpacerItem(QSpacerItem(4, 1))
        layout.addWidget(self._edit, Qt.AlignLeft)

        self.setLayout(layout)

        self._edit.editingFinished.connect(self._on_editing_finished)

    def text(self) -> str:
        """Get the current text of the edit widget."""
        return self._edit.text()

    def set_text(self, text: str) -> None:
        """Set the text on the edit widget."""
        self._edit.setText(text)

    def clear_focus(self) -> None:
        """Clear the focus of the line edit widget."""
        self._edit.clearFocus()

    def set_int_validator(self, min_val: Optional[int]=None, max_val: Optional[int]=None) -> None:
        """Set an int validator on this edit widget."""
        self._edit.setValidator(QIntValidator(min_val, max_val, self))

    def disable(self) -> None:
        """Disable the line edit."""
        self._edit.setDisabled(True)

    def enable(self) -> None:
        """Enable the line edit."""
        self._edit.setEnabled(True)

    def _on_editing_finished(self) -> None:
        self.editing_finished.emit()
