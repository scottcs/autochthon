"""Common dialogs."""
from typing import Optional

from PySide2.QtWidgets import QWidget, QMessageBox


def msg_error(msg: str, parent: Optional[QWidget]=None) -> None:
    """Show an error message."""
    QMessageBox().critical(parent, 'Error!', msg)
