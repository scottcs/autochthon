"""Widget to represent an editable component."""
from typing import Optional, Any, Sequence

from PySide2.QtCore import Signal
from PySide2.QtGui import QValidator
from PySide2.QtWidgets import QWidget, QHBoxLayout

from game.types import parameter_types, is_in_union, get_union_types
from .lineedit import ToolLineEdit


class MultiTypeValidator(QValidator):
    """Validator that allows several types."""
    def __init__(self, types: Sequence, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.types = types

    def validate(self, text: str, pos: int) -> int:
        """Validate the input."""
        ok = False
        for type_ in self.types:
            try:
                type_(str)
                ok = True
                break
            except TypeError:
                pass
        if ok:
            return QValidator.Acceptable
        else:
            return QValidator.Invalid
        # return QValidator.Intermediate


class ComponentPanel(QWidget):
    """An editable game component."""

    parameters_changed = Signal()

    def __init__(self, name: str, component_class: Any, parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        self._name = name
        self._parameters = parameter_types(component_class.__init__)
        self._widgets = []
        self._setup_layout()

    def _setup_layout(self) -> None:
        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)

        for name, params in self._parameters.items():
            edit = ToolLineEdit(name, default_text=params.get('default', None), min_label_width=40)
            types = params['types']
            edit.set_custom_validator(MultiTypeValidator(types))
            edit.editing_finished.connect(self._on_changes)
            self._widgets.append(edit)

        self.setLayout(layout)

    def _on_changes(self) -> None:
        self.parameters_changed.emit()

    def get_parameters(self) -> dict:
        """Get all of the current values of the parameters for this component."""
        return {widget.name: widget.text() for widget in self._widgets}
