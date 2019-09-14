"""Custom QLineEdit widget."""
import typing

import PySide2.QtCore
import PySide2.QtGui
import PySide2.QtWidgets


class ToolLineEdit(PySide2.QtWidgets.QWidget):
    """Custom Line Edit."""

    editing_finished = PySide2.QtCore.Signal()

    def __init__(
        self,
        label: str,
        parent: typing.Optional[PySide2.QtWidgets.QWidget] = None,
        default_text: typing.Optional[str] = None,
        edit_width: typing.Optional[int] = None,
        min_label_width: typing.Optional[int] = None,
        required: bool = False,
    ) -> None:
        super().__init__(parent)
        self.name = label
        self._label = PySide2.QtWidgets.QLabel(self.name)
        if min_label_width is not None:
            self._label.setMinimumWidth(min_label_width)

        self._edit = PySide2.QtWidgets.QLineEdit()
        self._edit.setAttribute(PySide2.QtCore.Qt.WA_MacShowFocusRect, False)  # macOS only
        if default_text:
            self._edit.setText(default_text)
        if edit_width:
            self._edit.setFixedWidth(edit_width)
        if required:
            self._label.setProperty("status", "required")
            self._edit.setProperty("status", "required")

        layout = PySide2.QtWidgets.QHBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)

        layout.addWidget(self._label)
        layout.addSpacerItem(PySide2.QtWidgets.QSpacerItem(4, 1))
        layout.addWidget(self._edit, PySide2.QtCore.Qt.AlignLeft)

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

    def set_int_validator(
        self, min_val: typing.Optional[int] = None, max_val: typing.Optional[int] = None
    ) -> None:
        """Set an int validator on this edit widget."""
        self._edit.setValidator(PySide2.QtGui.QIntValidator(min_val, max_val, self))

    def set_custom_validator(self, validator: typing.Any) -> None:
        """Set a custom validator."""
        self._edit.setValidator(validator)

    def disable(self) -> None:
        """Disable the line edit."""
        self._edit.setDisabled(True)

    def enable(self) -> None:
        """Enable the line edit."""
        self._edit.setEnabled(True)

    def _on_editing_finished(self) -> None:
        self.editing_finished.emit()
