"""Widget to represent an editable component."""
import enum
import typing

import PySide2.QtCore
import PySide2.QtWidgets

import game.data
import game.types
import tools.widgets.checkbox
import tools.widgets.combobox
import tools.widgets.lineedit

MIN_LABEL_WIDTH = 150


def int_float_self(arg: typing.Any) -> typing.Any:
    """Convert an arg to int or float or itself."""
    try:
        return int(arg)
    except ValueError:
        try:
            return float(arg)
        except ValueError:
            return arg


class ComponentPanel(PySide2.QtWidgets.QWidget):
    """An editable game component."""

    parameters_changed = PySide2.QtCore.Signal()

    def __init__(
        self,
        name: str,
        component_class: typing.Any,
        data: typing.Optional[typing.Mapping] = None,
        parent: typing.Optional[PySide2.QtWidgets.QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._name = name
        self._data = data or {}
        self._parameters = game.types.parameter_types(component_class.__init__)
        self._edit_widgets = []
        self._combo_widgets = []
        self._check_widgets = []
        self._setup_layout()

    def _setup_layout(self) -> None:
        layout = PySide2.QtWidgets.QVBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)

        for name, params in self._parameters.items():
            try:
                is_enum = issubclass(params["types"][0], enum.Enum)
            except TypeError:
                is_enum = False

            try:
                is_list = params["types"][0].__origin__ == list
            except AttributeError:
                is_list = list in params["types"]

            if bool in params["types"]:
                self._add_check_widget(name, params)
            elif is_enum:
                self._add_combo_widget(name, params)
            elif name == "tile_id":
                # special case for tile ids
                self._add_tile_id_combo_widget(name)
            elif is_list:
                # special case for lists
                self._add_list_combo_widget(name)
            else:
                self._add_edit_widget(name, params)

        for widget in self._edit_widgets:
            layout.addWidget(widget)
        if len(self._edit_widgets) > 0:
            layout.addSpacerItem(PySide2.QtWidgets.QSpacerItem(1, 8))
        for widget in self._combo_widgets:
            layout.addWidget(widget)
        if len(self._edit_widgets) + len(self._combo_widgets) > 0:
            layout.addSpacerItem(PySide2.QtWidgets.QSpacerItem(1, 8))
        for widget in self._check_widgets:
            layout.addWidget(widget)

        layout.addStretch()
        self.setLayout(layout)

    def _add_edit_widget(self, name, params):
        required = False
        try:
            default = params["default"]
            if default is None:
                default = ""
            else:
                default = str(default)
        except KeyError:
            default = None
            required = True
        widget = tools.widgets.lineedit.ToolLineEdit(
            name, required=required, default_text=default, min_label_width=MIN_LABEL_WIDTH
        )
        if name in self._data:
            widget.set_text(str(self._data[name]))
        widget.editing_finished.connect(self._on_changes)
        self._edit_widgets.append(widget)

    def _add_list_combo_widget(self, name):
        widget = tools.widgets.combobox.ToolMutableComboBox(
            name, min_label_width=MIN_LABEL_WIDTH, hide_duplicate_button=True
        )
        widget.enum_type = "list"
        if name in self._data:
            widget.add_items(self._data[name])
        widget.selection_changed.connect(self._on_changes)
        self._combo_widgets.append(widget)

    def _add_tile_id_combo_widget(self, name):
        widget = tools.widgets.combobox.ToolComboBox(name, min_label_width=MIN_LABEL_WIDTH)
        widget.enum_type = "tile_id"
        items = []
        for category in game.data.tile_ids.keys():
            for tile_name in game.data.tile_ids[category].keys():
                items.append(f"{category},{tile_name}")
        widget.add_items(sorted(items))
        if name in self._data:
            text = f"{self._data[name][0]},{self._data[name][1]}"
            widget.set_via_text(text)
        widget.selection_changed.connect(self._on_changes)
        self._combo_widgets.append(widget)

    def _add_combo_widget(self, name, params):
        widget = tools.widgets.combobox.ToolComboBox(name, min_label_width=MIN_LABEL_WIDTH)
        widget.enum_type = params["types"][0]
        widget.add_items(list(widget.enum_type.__members__.keys()))
        if "default" in params:
            which = str(params["default"]).split(".")[-1]
            widget.set_via_text(which)
        if name in self._data:
            which = self._data[name].split(".")[-1]
            widget.set_via_text(which)
        widget.selection_changed.connect(self._on_changes)
        self._combo_widgets.append(widget)

    def _add_check_widget(self, name, params):
        checked = self._data.get(name, params.get("default", False))
        widget = tools.widgets.checkbox.ToolCheckBox(name, checked=checked)
        widget.state_changed.connect(self._on_changes)
        self._check_widgets.append(widget)

    def _on_changes(self) -> None:
        self.parameters_changed.emit()

    def get_parameters(self) -> dict:
        """Get all of the current values of the parameters for this component."""
        params = {}
        for widget in self._edit_widgets:
            orig = self._parameters[widget.name]
            text = widget.text()
            value = int_float_self(text)
            if text and value != orig.get("default", None):
                params[widget.name] = value
        for widget in self._combo_widgets:
            orig = self._parameters[widget.name]
            if widget.enum_type == "tile_id":
                params[widget.name] = widget.text().split(",")
            elif widget.enum_type == "list":
                items = list(widget.iter_texts())
                if items:
                    params[widget.name] = items
            else:
                value = str(widget.enum_type.__members__[widget.text()])
                if "default" not in orig or orig["default"] != value:
                    params[widget.name] = value
        for widget in self._check_widgets:
            orig = self._parameters[widget.name]
            if "default" not in orig or orig["default"] != widget.isChecked():
                params[widget.name] = widget.isChecked()
        return params
