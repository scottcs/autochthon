"""Render processors."""
import esper

from game.component.playercontrolled import PlayerControlled
from game.component.position import Position
from game.component.renderable import Renderable
from game.events import WebsocketWriteAllEvent


class WebRenderProcessor(esper.Processor):
    """Game render processor for web socket."""

    def __init__(self) -> None:
        super().__init__()

    def process(self, data: dict) -> None:
        """Process all renderables."""
        if not data['time_passed']:
            return

        b_cells: bytearray = bytearray()
        num_cells: int = 0
        player_x: int = 0
        player_y: int = 0

        for ent, components in self.world.get_components(PlayerControlled, Renderable, Position):
            position = components[-1]
            player_x = position.x
            player_y = position.y
            # TODO: handle more than one player controlled object?
            break

        b_cells.extend(player_x.to_bytes(2, 'big'))
        b_cells.extend(player_y.to_bytes(2, 'big'))
        b_cells.extend(num_cells.to_bytes(2, 'big'))
        for ent, components in sorted(self.world.get_components(Position, Renderable),
                                      key=lambda x: x[1][1].layer.value):
            positional, renderable = components
            b_cells.extend(ent.to_bytes(2, 'big'))
            b_cells.extend(positional.x.to_bytes(2, 'big'))
            b_cells.extend(positional.y.to_bytes(2, 'big'))
            b_cells.extend(renderable.tile_id.to_bytes(2, 'big'))
            b_cells.extend(renderable.tint.to_bytes(4, 'big'))
            num_cells += 1
        # Overwrite num_cells now that we've counted them
        b_cells[4:6] = num_cells.to_bytes(2, 'big')
        ##########################################
        # Map Data:
        #     Header:
        #        2 bytes: player x position
        #        2 bytes: player y position
        #        2 bytes: num cells
        #     Each Cell:
        #        2 bytes: entity id
        #        2 bytes: position x
        #        2 bytes: position y
        #        2 bytes: tile id
        #        3 bytes: tint
        ##########################################
        WebsocketWriteAllEvent.fire({'message': bytes(b_cells), 'binary': True})


class TCODRenderProcessor(esper.Processor):
    """Game render processor for local TCOD console."""

    def __init__(self, _title: str, width: int=80, height: int=40) -> None:
        super().__init__()
        # Someday, implement this?
        print(f'Someday maybe this will be a {width}x{height} console.')

    def process(self, data: dict) -> None:
        """Process all renderables."""
        pass
