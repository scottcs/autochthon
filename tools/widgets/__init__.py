"""Widgets for tools."""
from pathlib import Path
from typing import Optional

from PySide2.QtWidgets import QWidget, QMessageBox, QApplication

STYLESHEET = Path('static/css/dark_orange.qss')


def msg_error(msg: str, parent: Optional[QWidget]=None) -> None:
    """Show an error message."""
    QMessageBox().critical(parent, 'Error!', msg)


class ToolApp(QApplication):
    """Custom QApplication."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with STYLESHEET.open() as f:
            self.setStyleSheet(f.read())
