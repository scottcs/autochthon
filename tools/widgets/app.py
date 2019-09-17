"""App widgets."""
import pathlib

import PySide2.QtWidgets

STYLESHEET = pathlib.Path("tools/style/dark_orange.qss")


class ToolApp(PySide2.QtWidgets.QApplication):
    """Custom QApplication."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with STYLESHEET.open() as f:
            self.setStyleSheet(f.read())
