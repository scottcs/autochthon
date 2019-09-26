"""Assemblage editor."""
import copy
import json
import pathlib
import re
import sys
import typing

import PySide2.QtCore
import PySide2.QtGui
import PySide2.QtWidgets

import game.data
import game.factory
import game.utils.render
import tools.widgets

DATA_DIR = pathlib.Path("data/assemblage")
COMPONENT_DIR = pathlib.Path("game/component")
COMPONENT_RE = re.compile(r"(?<=^class )\w+")
IGNORE_COMPONENT_PREFIXES = ("Base", "TMP")


class RenderWidget(PySide2.QtWidgets.QWidget):
    """Render widget."""

    def __init__(self, parent: typing.Optional[PySide2.QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.setMinimumSize(32, 48)
        self.setMaximumSize(32, 48)
        self.tileset = None
        self.tile_size = None
        self.tile_coords = None
        self.color = None
        self.sprite = None

    def clear_sprite(self) -> None:
        """Clear the sprite."""
        self.tileset = None
        self.tile_size = None
        self.tile_coords = None
        self.color = None
        self.sprite = None
        self.update()
        self.repaint()

    def update_tile(self, tile_id: typing.Sequence[str], color: str) -> None:
        """Update the rendered tile."""
        try:
            self.tileset = game.data.TILES_PATH / pathlib.Path(
                game.data.tileset["tilesets"][tile_id[0]]["file"]
            )
            self.tile_size = game.data.tileset["tilesets"][tile_id[0]]["size"]
            total_offset = game.utils.render.TileCache.get(*tile_id)
            offset = total_offset - int(game.data.tileset["tilesets"][tile_id[0]]["offset"], 0)
            x = offset % int(self.tile_size[0])
            y = offset // int(self.tile_size[1])
            self.tile_coords = [x * self.tile_size[0], y * self.tile_size[1]]
        except KeyError:
            tools.widgets.msg_error(f"Tileset not found for: {tile_id}", self)
            return

        try:
            self.color = game.factory.convert_datum(color)
        except AttributeError:
            tools.widgets.msg_error(f"Unknown color: {color}", self)
            return
        self.set_sprite()
        self.update()
        self.repaint()

    def set_sprite(self) -> None:
        """Draw the image."""
        # frame = None
        # for frame_name, frame_data in tileset_data["frames"].items():
        #     if frame_name == tile:
        #         frame = frame_data["frame"]
        #         break
        # if not frame:
        #     tools.widgets.msg_error(f"Could not find frame for {tile}", self)
        #     return
        x, y = self.tile_coords
        w, h = self.tile_size
        sheet = PySide2.QtGui.QImage(str(self.tileset))
        print(x, y, w, h)
        self.sprite = sheet.copy(x, y, w, h)

    def paintEvent(self, event):
        """Called when this widget should be painted."""
        if not self.sprite:
            return

        mask = PySide2.QtGui.QImage(self.sprite)
        painter = PySide2.QtGui.QPainter()

        # painter.begin(mask)
        # painter.setCompositionMode(PySide2.QtGui.QPainter.CompositionMode_SourceIn)
        # painter.fillRect(mask.rect(), PySide2.QtGui.QColor(self.color))
        # painter.end()

        painter.begin(self)
        painter.fillRect(self.rect(), PySide2.QtCore.Qt.black)
        painter.drawImage(8, 12, mask)
        painter.end()


class FileLoadSave(PySide2.QtWidgets.QWidget):
    """File load/save line."""

    file_loaded = PySide2.QtCore.Signal(dict)

    def __init__(self, parent: typing.Optional[PySide2.QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.filename = None
        self.data = {}
        self.original_json = None

        layout = PySide2.QtWidgets.QHBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)

        self.edit = tools.widgets.ToolLineEdit("File:")
        self.edit.disable()

        self.load_button = tools.widgets.ToolPushButton("Load")
        self.save_button = tools.widgets.ToolPushButton("Save")
        self.save_button.setDisabled(True)

        layout.addWidget(self.edit)
        layout.addSpacerItem(PySide2.QtWidgets.QSpacerItem(4, 0))
        layout.addWidget(self.load_button)
        layout.addWidget(self.save_button)
        self.setLayout(layout)

        self.load_button.clicked.connect(self._on_load)
        self.save_button.clicked.connect(self._on_save)

    def _on_load(self) -> None:
        if self.save_button.isEnabled():
            message_box = PySide2.QtWidgets.QMessageBox()
            message_box.setText("The document has been modified.")
            message_box.setInformativeText("Do you want to save your changes?")
            message_box.setStandardButtons(
                PySide2.QtWidgets.QMessageBox.Save
                | PySide2.QtWidgets.QMessageBox.Discard
                | PySide2.QtWidgets.QMessageBox.Cancel
            )
            message_box.setDefaultButton(PySide2.QtWidgets.QMessageBox.Save)
            ret = message_box.exec_()
            if ret == PySide2.QtWidgets.QMessageBox.Save:
                if not self._on_save():
                    return
            elif ret == PySide2.QtWidgets.QMessageBox.Cancel:
                return
            elif ret == PySide2.QtWidgets.QMessageBox.Discard:
                pass
            else:
                # should never be reached
                return

        filename = PySide2.QtWidgets.QFileDialog().getOpenFileName(
            self, "Open Assemblage", str(DATA_DIR), "Assemblage Files (*.json)"
        )[0]
        if filename:
            self.filename = pathlib.Path(filename)
            text = filename.split(f"{DATA_DIR}/")[-1]
            self.edit.set_text(text)
            self._load_file()

    def _on_save(self) -> bool:
        if not self.data:
            tools.widgets.msg_error("No data to save!", self)
            return False
        for key in self.data.keys():
            if key == "":
                tools.widgets.msg_error("You must give all assemblages a name!", self)
                return False
            if not self.data[key]:
                tools.widgets.msg_error("There is no component data to save!", self)
                return False
        filename = PySide2.QtWidgets.QFileDialog().getSaveFileName(
            self, "Save Assemblage As", str(DATA_DIR), "Assemblage Files (*.json)"
        )[0]
        if filename:
            self.filename = pathlib.Path(filename)
            text = filename.split(f"{DATA_DIR}/")[-1]
            self.edit.set_text(text)
            self._save_file()
            return True
        return False

    def _save_file(self) -> None:
        self.save_button.setDisabled(True)
        self.save_button.repaint()
        with self.filename.open("w") as f:
            json.dump(self.data, f, indent=2)

    def _load_file(self) -> None:
        self.save_button.setDisabled(True)
        self.save_button.repaint()
        with self.filename.open() as f:
            self.data = json.load(f)
            self.original_json = json.dumps(self.data, sort_keys=True)
        if self.data:
            self.file_loaded.emit(self.data)

    def _enable_save_button(self) -> None:
        self.save_button.setDisabled(False)
        self.save_button.repaint()

    def update_data(self, data: typing.MutableMapping) -> None:
        """Update the internal representation of the data."""
        new_json = json.dumps(data, sort_keys=True)
        if self.original_json != new_json:
            self._enable_save_button()
            self.data = data
        else:
            self.save_button.setDisabled(True)
        self.save_button.repaint()


class GetComponentDialog(PySide2.QtWidgets.QDialog):
    """Choose a component."""

    components = []

    def __init__(self, parent: typing.Optional[PySide2.QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.setMinimumSize(400, 600)
        self._cache_component_list()

        layout = PySide2.QtWidgets.QVBoxLayout()

        self.components_list = PySide2.QtWidgets.QListWidget()
        self.components_list.addItems(self.components)
        self.components_list.setSelectionMode(
            PySide2.QtWidgets.QAbstractItemView.ExtendedSelection
        )

        buttons = PySide2.QtWidgets.QDialogButtonBox(
            PySide2.QtWidgets.QDialogButtonBox.Ok | PySide2.QtWidgets.QDialogButtonBox.Cancel,
            PySide2.QtCore.Qt.Horizontal,
            self,
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(PySide2.QtWidgets.QLabel("Add Components: "))
        layout.addWidget(self.components_list)
        layout.addWidget(buttons)
        self.setLayout(layout)

    @classmethod
    def _cache_component_list(cls) -> None:
        if not cls.components:
            components = []
            for filename in COMPONENT_DIR.glob("*.py"):
                component_family = filename.stem
                with filename.open() as f:
                    for line in f.readlines():
                        found = COMPONENT_RE.search(line)
                        if found:
                            name = found.group(0)
                            if not any([name.startswith(p) for p in IGNORE_COMPONENT_PREFIXES]):
                                components.append(f"{component_family}.{name}")
            cls.components = sorted(components)

    def get(self) -> typing.List[str]:
        """Show the dialog and get the component name."""
        result = self.exec_()
        components = []
        if result == PySide2.QtWidgets.QDialog.Accepted:
            for selected in self.components_list.selectedItems():
                components.append(selected.text())
        return components


class ComponentList(PySide2.QtWidgets.QWidget):
    """Component list widget."""

    selection_changed = PySide2.QtCore.Signal(str)
    component_removed = PySide2.QtCore.Signal(str)
    components_added = PySide2.QtCore.Signal(list)

    def __init__(self, parent: typing.Optional[PySide2.QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        layout = PySide2.QtWidgets.QVBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)
        header_layout = PySide2.QtWidgets.QHBoxLayout()
        header_layout.setSpacing(0)
        header_layout.setMargin(0)

        self.add_button = tools.widgets.ToolPushButton("+")
        self.remove_button = tools.widgets.ToolPushButton("-")
        self.component_list = PySide2.QtWidgets.QListWidget(self)

        header_layout.addWidget(PySide2.QtWidgets.QLabel("Components"))
        header_layout.addStretch()
        header_layout.addWidget(self.add_button)
        header_layout.addWidget(self.remove_button)

        layout.addLayout(header_layout)
        layout.addWidget(self.component_list)
        self.setLayout(layout)

        self.add_button.clicked.connect(self._on_add)
        self.remove_button.clicked.connect(self._on_remove)
        self.component_list.itemSelectionChanged.connect(self._on_selection)
        self.enable_buttons(False)

    def _on_add(self) -> None:
        component_names = GetComponentDialog().get()
        if component_names:
            self.components_added.emit(component_names)

    def _on_remove(self) -> None:
        try:
            selected: PySide2.QtWidgets.QListWidgetItem = self.component_list.selectedItems()[0]
            self.component_list.takeItem(self.component_list.row(selected))
            self.component_removed.emit(selected.text())
        except IndexError:
            pass

    def _on_selection(self) -> None:
        try:
            selected: PySide2.QtWidgets.QListWidgetItem = self.component_list.selectedItems()[0]
            self.selection_changed.emit(selected.text())
        except IndexError:
            pass

    def enable_buttons(self, enable: bool = True):
        """Enable or disable the +/- buttons."""
        self.add_button.setEnabled(enable)
        self.remove_button.setEnabled(enable)

    def update_items(self, items: typing.Sequence) -> None:
        """Update the items in the list."""
        self.component_list.clear()
        self.component_list.addItems(items)
        self.sizeHint()
        self.update()
        self.repaint()


class ComponentPane(PySide2.QtWidgets.QWidget):
    """Component Pane widget."""

    data_changed = PySide2.QtCore.Signal(dict)

    def __init__(self, parent: typing.Optional[PySide2.QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.data = {}
        self.selected = None
        layout = PySide2.QtWidgets.QHBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)
        details_layout = PySide2.QtWidgets.QVBoxLayout()
        details_layout.setSpacing(0)
        details_layout.setMargin(0)

        self.component_list = ComponentList(self)
        details_label = PySide2.QtWidgets.QLabel("Component Details")
        details_label.setMinimumHeight(23)
        details_layout.addWidget(details_label)
        self.params_widget = PySide2.QtWidgets.QScrollArea()
        self.params_widget.setHorizontalScrollBarPolicy(PySide2.QtCore.Qt.ScrollBarAlwaysOff)
        details_layout.addWidget(self.params_widget)

        layout.addWidget(self.component_list)
        layout.addSpacerItem(PySide2.QtWidgets.QSpacerItem(4, 1))
        layout.addLayout(details_layout)

        self.setLayout(layout)

        self.component_list.selection_changed.connect(self._on_selection_changed)
        self.component_list.component_removed.connect(self._on_component_removed)
        self.component_list.components_added.connect(self._on_components_added)

    def _on_selection_changed(self, selected: str) -> None:
        self.selected = selected
        self.data.setdefault(selected, {})
        if self.params_widget.widget() is not None:
            self.params_widget.widget().parameters_changed.disconnect(self._on_parameters_changed)
        component_class = game.factory.get_component_class(selected)
        widget = tools.widgets.ComponentPanel(selected, component_class, data=self.data[selected])
        widget.parameters_changed.connect(self._on_parameters_changed)
        self.params_widget.setWidget(widget)
        self.params_widget.setWidgetResizable(True)

    def _on_parameters_changed(self):
        try:
            params = self.params_widget.widget().get_parameters()
        except AttributeError:
            print(f"SOMETHING WEIRD - no widget?: {self.selected}")
            params = {}
        if self.selected:
            self.data[self.selected] = params
            self.data_changed.emit({"Components": self.data})

    def _on_component_removed(self, component_name: str) -> None:
        try:
            del self.data[component_name]
            self.data_changed.emit({"Components": self.data})
        except KeyError:
            tools.widgets.msg_error(
                f"Attempt to delete a component that does not exist: {component_name}", self
            )
        if self.component_list.component_list.count() == 0:
            self.hide_data()

    def _on_components_added(self, component_names: typing.Sequence[str]) -> None:
        for component_name in component_names:
            self.data.setdefault(component_name, {})
        self.data_changed.emit({"Components": self.data})
        self.component_list.update_items(sorted(self.data.keys()))
        self.update()

    def update_data(self, data: typing.Mapping) -> None:
        """Update the data in this widget."""
        self.data = data["Components"]
        self.component_list.update_items(sorted(self.data.keys()))
        self.sizeHint()
        self.update()
        self.repaint()

    def hide_data(self) -> None:
        """Hide the data pane."""
        self.params_widget.takeWidget()


class AssemblageEditor(PySide2.QtWidgets.QWidget):
    """Assemblage editor parent widget."""

    def __init__(self, parent: typing.Optional[PySide2.QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.assemblage_data: dict = {}
        self.setWindowTitle("Assemblage Editor")
        self.setMinimumSize(800, 600)

        layout = PySide2.QtWidgets.QVBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(10)

        header_layout = PySide2.QtWidgets.QHBoxLayout()
        header_layout.setSpacing(0)
        header_layout.setMargin(0)

        header_right_layout = PySide2.QtWidgets.QVBoxLayout()
        header_right_layout.setSpacing(0)
        header_right_layout.setMargin(0)

        self.render_widget = RenderWidget()
        self.file_widget = FileLoadSave()
        self.assemblage_name = tools.widgets.ToolMutableComboBox("Assemblage Name:", sort=True)
        self.component_widget = ComponentPane()

        header_right_layout.addWidget(self.file_widget)
        header_right_layout.addWidget(self.assemblage_name)
        header_layout.addWidget(self.render_widget)
        header_layout.addSpacerItem(PySide2.QtWidgets.QSpacerItem(8, 0))
        header_layout.addLayout(header_right_layout)
        layout.addLayout(header_layout)
        layout.addWidget(self.component_widget)

        self.setLayout(layout)

        self.assemblage_name.selection_changed.connect(self._on_assemblage_name_changed)
        self.assemblage_name.duplicate_item.connect(self._on_assemblage_duplicate)
        self.file_widget.file_loaded.connect(self._on_file_loaded)
        self.component_widget.data_changed.connect(self._on_data_changed)

    def _on_file_loaded(self, data: typing.Mapping) -> None:
        self.assemblage_data = data
        self.render_widget.clear_sprite()
        self.assemblage_name.clear()
        self.assemblage_name.add_items(list(data.keys()))
        self._on_assemblage_name_changed()

    def _on_assemblage_name_changed(self) -> None:
        name = self.assemblage_name.text()
        if name:
            self.assemblage_data.setdefault(name, {"Components": {}})
            self.component_widget.update_data(self.assemblage_data[name])
            self._update_render_widget(self.assemblage_data[name])
            self.component_widget.hide_data()
            self.component_widget.component_list.enable_buttons()
        else:
            self.component_widget.component_list.enable_buttons(False)
        self.update()
        self.repaint()

    def _on_assemblage_duplicate(self, old: str) -> None:
        name = self.assemblage_name.text()
        self.assemblage_data[name] = copy.deepcopy(self.assemblage_data[old])
        self._on_assemblage_name_changed()

    def _on_data_changed(self, data: typing.Mapping) -> None:
        self.assemblage_data[self.assemblage_name.text()] = data
        self.file_widget.update_data(self.assemblage_data)
        self._update_render_widget(data)

    def _update_render_widget(self, data: typing.Mapping) -> None:
        self.render_widget.clear_sprite()
        components = data.get("Components", {})
        renderable = components.get("render.Renderable", None)
        if renderable:
            self.render_widget.update_tile(renderable["tile_id"], renderable["tint"])


def main() -> int:
    """ Main function """
    app = tools.widgets.ToolApp(sys.argv)
    assemblage_edit = AssemblageEditor()
    assemblage_edit.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
