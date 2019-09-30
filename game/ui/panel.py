"""Draw a UI Panel."""
import typing


class Panel:
    """UI Panel."""

    def __init__(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        text: typing.Sequence[str],
        style: typing.Optional[str] = None,
    ) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.style = style or "panel_window"
        self.visible = False

    def show(self) -> None:
        """Show the panel."""
        self.visible = True

    def hide(self) -> None:
        """Hide the panel."""
        self.visible = False

    def render(self) -> None:
        """Render the panel."""
        if not self.visible:
            return
