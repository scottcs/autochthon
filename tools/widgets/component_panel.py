"""Widget to represent an editable component."""
from enum import Enum
from typing import Optional, Any, Mapping

from PySide2.QtCore import Signal
from PySide2.QtWidgets import QWidget, QVBoxLayout, QSpacerItem

from game.types import parameter_types
from gamedata.tile_ids import TILE_IDS
from .checkbox import ToolCheckBox
from .combobox import ToolComboBox, ToolMutableComboBox
from .lineedit import ToolLineEdit

MIN_LABEL_WIDTH = 150


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

            try:
                is_list = params['types'][0].__origin__ == list
            except AttributeError:
                is_list = list in params['types']

            if bool in params['types']:
                checked = self._data.get(name, bool(default))
                widget = ToolCheckBox(name, checked=checked)
                widget.state_changed.connect(self._on_changes)
                self._check_widgets.append(widget)
            elif is_enum:
                widget = ToolComboBox(name, min_label_width=MIN_LABEL_WIDTH)
                widget.enum_type = params['types'][0]
                widget.add_items(list(widget.enum_type.__members__.keys()))
                if name in self._data:
                    which = self._data[name].split('.')[-1]
                    widget.set_via_text(which)
                widget.selection_changed.connect(self._on_changes)
                self._combo_widgets.append(widget)
            elif name == 'tile_id':
                # special case for tile ids
                widget = ToolComboBox(name, min_label_width=MIN_LABEL_WIDTH)
                widget.enum_type = 'tile_id'
                widget.add_items(sorted([t['name'] for t in TILE_IDS.values()]))
                if name in self._data:
                    widget.set_via_text(self._data[name])
                widget.selection_changed.connect(self._on_changes)
                self._combo_widgets.append(widget)
            elif is_list:
                # special case for lists
                widget = ToolMutableComboBox(name, min_label_width=MIN_LABEL_WIDTH,
                                             hide_duplicate_button=True)
                widget.enum_type = 'list'
                if name in self._data:
                    widget.add_items(self._data[name])
                widget.selection_changed.connect(self._on_changes)
                self._combo_widgets.append(widget)
            else:
                widget = ToolLineEdit(name,
                                      required=required,
                                      default_text=default,
                                      min_label_width=MIN_LABEL_WIDTH)
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

        layout.addStretch()
        self.setLayout(layout)

    def _on_changes(self) -> None:
        self.parameters_changed.emit()

    def get_parameters(self) -> dict:
        """Get all of the current values of the parameters for this component."""
        params = {widget.name: widget.text() for widget in self._edit_widgets}
        for widget in self._combo_widgets:
            if widget.enum_type == 'tile_id':
                params[widget.name] = widget.text()
            elif widget.enum_type == 'list':
                params[widget.name] = list(widget.iter_texts())
            else:
                params[widget.name] = str(widget.enum_type.__members__[widget.text()])
        params.update({widget.name: widget.isChecked() for widget in self._check_widgets})
        return params
