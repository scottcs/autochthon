"""Widget: basic building block of UI."""
from __future__ import annotations

import logging
import typing

import game.render
import game.utils.geometry

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Widget:
    """A basic UI element."""

    def __init__(self, rect: game.utils.geometry.Rect) -> None:
        self.rect: game.utils.geometry.Rect = rect
        self.children: typing.List[Widget] = []
        self._visible: bool = False
        self._layout: typing.Optional[Layout] = None
        # TODO: input events

    def __str__(self) -> str:
        return f"{self.__class__.__name__}<{self.rect} ({id(self)})>"

    @property
    def visible(self) -> bool:
        """True if this widget is visible."""
        return self._visible

    def add_widget(self, widget: Widget) -> None:
        """Add a widget to this widget's children."""
        self.children.append(widget)
        if self._layout:
            self._layout.reposition(self, self.children)

    def set_layout(self, layout: Layout) -> None:
        """Set this widget's layout of child widgets."""
        self._layout = layout
        self._layout.reposition(self, self.children)

    def show(self) -> None:
        """Show the frame."""
        self._visible = True
        for child in self.children:
            child.show()

    def hide(self) -> None:
        """Hide the frame."""
        self._visible = False
        for child in self.children:
            child.hide()

    def move_to(self, x: int, y: int) -> None:
        """Move to the given coordinates, bringing child widgets along."""
        dx, dy = self.rect.x1 - x, self.rect.y1 - y
        self.rect.move_to(x, y)
        for child in self.children:
            child.move_to(child.rect.x1 + dx, child.rect.y1 + dy)

    def render(self, renderer: game.render.BaseRenderer, layer: int) -> None:
        """Render this widget."""
        if not self._visible:
            return
        self._paint(renderer, layer)
        for child in self.children:
            child.render(renderer, layer)

    def _paint(self, renderer: game.render.BaseRenderer, layer: int) -> None:
        """Paint only this widget, not children."""
        pass


class Spacer(Widget):
    """Blank space."""

    def __init__(self, w: int, h: int) -> None:
        super().__init__(game.utils.geometry.Rect(0, 0, w, h))


class Layout:
    """Base Layout."""

    def __init__(
        self, margin: typing.Optional[int] = None, spacing: typing.Optional[int] = None
    ) -> None:
        if margin is None:
            margin = 2
        if spacing is None:
            spacing = 2
        self.margin: int = margin
        self.spacing: int = spacing

    def reposition(self, parent: Widget, children: typing.Sequence[Widget]) -> None:
        """Calculate the positions for each child widget relative to the parent."""
        # This is basic positioning that only really works for one widget.
        # (All widgets on top of each other, if more than one.)
        # Use child Layouts for multiple widgets.
        x = parent.rect.x1 + self.margin + self.spacing
        y = parent.rect.y1 + self.margin + self.spacing
        for child in children:
            child.move_to(x, y)


class VerticalLayout(Layout):
    """Align child elements vertically."""

    def reposition(self, parent: Widget, children: typing.Sequence[Widget]) -> None:
        """Calculate the positions for each child widget relative to the parent."""
        x = parent.rect.x1 + self.spacing
        y = parent.rect.y1
        for child in children:
            y += self.spacing
            child.move_to(x, y)
            y += child.rect.h


class HorizontalLayout(Layout):
    """Align child elements horizontally."""

    def reposition(self, parent: Widget, children: typing.Sequence[Widget]) -> None:
        """Calculate the positions for each child widget relative to the parent."""
        x = parent.rect.x1
        y = parent.rect.y1 + self.spacing
        for child in children:
            x += self.spacing
            child.rect.move_to(x, y)
            x += child.rect.w
