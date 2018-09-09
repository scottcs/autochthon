"""Custom checkbox for tools."""
from PySide2.QtCore import Signal
from PySide2.QtWidgets import QCheckBox


class ToolCheckBox(QCheckBox):
    """Custom checkbox widget."""

    state_changed = Signal(str, bool)

    def __init__(self, *args, checked=False, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setChecked(checked)
        self.stateChanged.connect(self._on_state_changed)

    def _on_state_changed(self, state: int) -> None:
        self.state_changed.emit(self.text(), bool(state))

    @property
    def name(self):
        """name property"""
        return self.text()
