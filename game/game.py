"""Temporary game file."""


class Game:
    """Main game object."""

    def __init__(self):
        self.game_over = False
        self.x = 0
        self.y = 0
        self.tileset = 'static/img/oryx_ur/Monsters.json'
        self.tile = 'orc2_1'

    def on_keyboard_input(self, keys) -> dict:
        """Core game loop."""
        if self.check_for_time_passed():
            # self.world.update()
            ...
        else:
            # self.keyboard_input_system.update()
            # self.display_system.update()
            ...
        if self.check_for_game_over():
            return {'game_over': True}

        map_deltas = []
        map_deltas.append({
            'x': self.x,
            'y': self.y,
            'tileset': None,
            'tile': None,
        })

        if 'l' in keys or 'u' in keys or 'n' in keys:
            self.x += 1
        if 'h' in keys or 'y' in keys or 'b' in keys:
            self.x -= 1
        if 'k' in keys or 'y' in keys or 'u' in keys:
            self.y -= 1
        if 'j' in keys or 'b' in keys or 'n' in keys:
            self.y += 1

        map_deltas.append({
            'x': self.x,
            'y': self.y,
            'tileset': self.tileset,
            'tile': self.tile,
        })
        return {'map_deltas': map_deltas}

    def on_mouse_input(self, mouse) -> dict:
        return {}

    def check_for_game_over(self):
        """Return True if the game is over."""
        return False

    def check_for_time_passed(self) -> bool:
        """Return True if time has passed."""
        return True
