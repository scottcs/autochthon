"""Common dialogs."""
import typing

import PySide2.QtWidgets


def msg_error(msg: str, parent: typing.Optional[PySide2.QtWidgets.QWidget] = None) -> None:
    """Show an error message."""
    PySide2.QtWidgets.QMessageBox().critical(parent, "Error!", msg)
