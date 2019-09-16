"""Custom QPushButton for tools."""
import PySide2.QtCore
import PySide2.QtWidgets


class ToolPushButton(PySide2.QtWidgets.QPushButton):
    """Custom QPushbutton."""

    def __init__(self, *args, allow_focus: bool = False, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if allow_focus:
            self.setAutoDefault(True)
            self.setDefault(True)
        else:
            self.setFocusPolicy(PySide2.QtCore.Qt.NoFocus)
            self.setAutoDefault(False)
            self.setDefault(False)
