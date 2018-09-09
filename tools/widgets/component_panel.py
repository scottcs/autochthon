"""Widget to represent an editable component."""
from enum import Enum
from typing import Optional, Any, Sequence, Mapping

from PySide2.QtCore import Signal
from PySide2.QtGui import QValidator
from PySide2.QtWidgets import QWidget, QVBoxLayout, QSpacerItem

from game.types import parameter_types
from .checkbox import ToolCheckBox
from .combobox import ToolComboBox
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

    def __init__(self, name: str, component_class: Any, data: Optional[Mapping]=None,
                 parent: Optional[QWidget]=None) -> None:
        super().__init__(parent)
        self._name = name
        self._data = data or {}
        self._parameters = parameter_types(component_class.__init__)
        self._edit_widgets = []
        self._combo_widgets = []
        self._check_widgets = []
        self._setup_layout()

    def _setup_layout(self) -> None:
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)

        for name, params in self._parameters.items():
            required = False
            try:
                default = params['default']
                if default is None:
                    default = ''
                else:
                    default = str(default)
            except KeyError:
                default = None
                required = True

            try:
                is_enum = issubclass(params['types'][0], Enum)
            except TypeError:
                is_enum = False

            if bool in params['types']:
                checked = self._data.get(name, bool(default))
                widget = ToolCheckBox(name, checked=checked)
                widget.state_changed.connect(self._on_changes)
                self._check_widgets.append(widget)
            elif is_enum:
                widget = ToolComboBox(name, min_label_width=100)
                widget.enum_type = params['types'][0]
                widget.add_items(list(widget.enum_type.__members__.keys()))
                if name in self._data:
                    which = self._data[name].split('.')[-1]
                    widget.set_via_text(which)
                widget.selection_changed.connect(self._on_changes)
                self._combo_widgets.append(widget)
            else:
                widget = ToolLineEdit(name,
                                      required=required,
                                      default_text=default,
                                      min_label_width=100)
                # types = params['types']
                # widget.set_custom_validator(MultiTypeValidator(types))
                if name in self._data:
                    widget.set_text(str(self._data[name]))
                widget.editing_finished.connect(self._on_changes)
                self._edit_widgets.append(widget)
        for widget in self._edit_widgets:
            layout.addWidget(widget)
        if len(self._edit_widgets) > 0:
            layout.addSpacerItem(QSpacerItem(1, 8))
        for widget in self._combo_widgets:
            layout.addWidget(widget)
        if len(self._edit_widgets) + len(self._combo_widgets) > 0:
            layout.addSpacerItem(QSpacerItem(1, 8))
        for widget in self._check_widgets:
            layout.addWidget(widget)

        self.setLayout(layout)

    def _on_changes(self) -> None:
        self.parameters_changed.emit()

    def get_parameters(self) -> dict:
        """Get all of the current values of the parameters for this component."""
        params = {widget.name: widget.text() for widget in self._edit_widgets}
        for widget in self._combo_widgets:
            params[widget.name] = str(widget.enum_type.__members__[widget.text()])
        params.update({widget.name: widget.isChecked() for widget in self._check_widgets})
        return params
