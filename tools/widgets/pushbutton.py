"""Custom QPushButton for tools."""
from PySide2.QtCore import Qt
from PySide2.QtWidgets import QPushButton


class ToolPushButton(QPushButton):
    """Custom QPushbutton."""

    def __init__(self, *args, allow_focus: bool=False, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if allow_focus:
            self.setAutoDefault(True)
            self.setDefault(True)
        else:
            self.setFocusPolicy(Qt.NoFocus)
            self.setAutoDefault(False)
            self.setDefault(False)
