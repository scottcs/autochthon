"""App widgets."""
from pathlib import Path

from PySide2.QtWidgets import QApplication

STYLESHEET = Path('static/css/dark_orange.qss')


class ToolApp(QApplication):
    """Custom QApplication."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with STYLESHEET.open() as f:
            self.setStyleSheet(f.read())
