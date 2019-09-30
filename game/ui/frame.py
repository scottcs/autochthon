"""Draw a UI Frame."""
import typing

import game.data
import game.render
import game.types
import game.utils.geometry


class Frame:
    """Generic UI Frame."""

    def __init__(self, rect: game.utils.geometry.Rect, style: typing.Optional[str] = None) -> None:
        self.rect: game.utils.geometry.Rect = rect
        self.style: typing.Optional[str] = style
        self.visible: bool = False

    def show(self) -> None:
        """Show the frame."""
        self.visible = True

    def hide(self) -> None:
        """Hide the frame."""
        self.visible = False

    def render(self, renderer: game.render.BaseRenderer, layer: int) -> None:
        """Render the frame."""
        if not self.visible:
            return
        if self.style:
            self._render_background(renderer, layer)
            self._render_foreground(renderer, layer + 1)
        else:
            self._render_foreground(renderer, layer)

    def _get_style_tile_id(self, x: int, y: int):
        if self.style is None:
            return
        direction = "base"
        w = self.rect.w - 1
        h = self.rect.h - 1
        if x == 0:
            if y == 0:
                direction = "nw"
            elif y == h:
                direction = "sw"
            else:
                direction = "w"
        elif x == w:
            if y == 0:
                direction = "ne"
            elif y == h:
                direction = "se"
            else:
                direction = "e"
        elif y == 0:
            direction = "n"
        elif y == h:
            direction = "s"
        return game.render.TileCache.get("interface", self.style, direction=direction)

    def _render_background(self, renderer: game.render.BaseRenderer, layer: int) -> None:
        renderer.clear_layer(layer, rect=self.rect)
        for x in range(self.rect.w):
            for y in range(self.rect.h):
                tile_id = self._get_style_tile_id(x, y)
                renderer.draw_on_layer(layer, self.rect.x1 + x, self.rect.y1 + y, tile_id)

    def _render_foreground(self, renderer: game.render.BaseRenderer, layer: int) -> None:
        renderer.clear_layer(layer, rect=self.rect)
        renderer.draw_text_on_layer(layer, 4, 4, "TEST")


class Layout:
    """Base Layout."""

    def __init__(self, rect: game.utils.geometry.Rect) -> None:
        self._rect: game.utils.geometry.Rect = rect
        self.spacing: int = 2
        self.margin: int = 2
        self.frames: typing.List[Frame] = []
        self._visible: bool = False

    def show(self):
        """Show all child frames."""
        self._visible = True
        for frame in self.frames:
            frame.visible = True

    def hide(self):
        """Hide all child frames."""
        self._visible = False
        for frame in self.frames:
            frame.visible = False

    def append(self, frame: Frame) -> None:
        """Append a frame to this layout."""
        self.frames.append(frame)
        frame.visible = self._visible
        self._calculate_frame_positions()

    def append_space(self, amount: int) -> None:
        """Append some blank space to the layout."""
        self.frames.append(Frame(game.utils.geometry.Rect(0, 0, amount, amount)))

    def move_to(self, x: int, y: int) -> None:
        """Move to the given coordinates."""
        self._rect.move_to(x, y)
        self._calculate_frame_positions()

    def render(self, renderer: game.render.BaseRenderer, layer: int) -> None:
        """Render the frames in this layout, clipping to the size of the layout."""
        if not self._visible:
            return
        # TODO: clip?
        for frame in self.frames:
            frame.render(renderer, layer)

    def _calculate_frame_positions(self) -> None:
        """Calculate the positions for each child frame, left to right, top to bottom."""
        # This is the default base layout and will stack all frames on top of each other.
        for frame in self.frames:
            frame.rect.move_to(self._rect.x1 + self.spacing, self._rect.y1 + self.spacing)


class VerticalLayout(Layout):
    """Align child elements vertically."""

    def _calculate_frame_positions(self):
        x = self._rect.x1 + self.spacing
        y = self._rect.y1
        for frame in self.frames:
            y += self.spacing
            frame.rect.move_to(x, y)
            y += frame.rect.h

    def append_space(self, amount: int) -> None:
        """Append some vertical blank space to the layout."""
        self.frames.append(Frame(game.utils.geometry.Rect(0, 0, 1, amount)))


class HorizontalLayout(Layout):
    """Align child elements horizontally."""

    def _calculate_frame_positions(self):
        x = self._rect.x1
        y = self._rect.y1 + self.spacing
        for frame in self.frames:
            x += self.spacing
            frame.rect.move_to(x, y)
            x += frame.rect.w

    def append_space(self, amount: int) -> None:
        """Append some vertical blank space to the layout."""
        self.frames.append(Frame(game.utils.geometry.Rect(0, 0, amount, 1)))
