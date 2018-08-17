"""Enemy Factory."""
from gamedata.entity.assemblage import schema
from game.component.action import Actor
from game.component.descriptive import Name
from game.component.movement import Position
from game.component.render import Renderable
from game.component.status import Solid
from game.types import RenderLayer
from gamedata.palette import Palette


Enemy = (
    schema(Actor),
    schema(Name, 'Unknown Enemy'),
    schema(Position),
    schema(Renderable, 0, Palette.white, RenderLayer.ENEMY),
    schema(Solid),
)
