"""Temporary game file."""

MOMENTS_PER_TURN = 10


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
        print(f'got keys {keys}')
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

        if 'Control' in keys:
            print('control')
            return {}

        for key in keys:
            map_deltas.append({
                'x': self.x,
                'y': self.y,
                'tileset': None,
                'tile': None,
            })

            if 'l' == key or 'u' == key or 'n' == key:
                self.x += 1
            if 'h' == key or 'y' == key or 'b' == key:
                self.x -= 1
            if 'k' == key or 'y' == key or 'u' == key:
                self.y -= 1
            if 'j' == key or 'b' == key or 'n' == key:
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

    def process_input_event(self, event) -> dict:
        """Process an input event."""
        keys = event.get('keys')
        mouse = event.get('mouse')
        results = {}
        if keys:
            results.update(self.on_keyboard_input(keys))
        if mouse:
            results.update(self.on_mouse_input(mouse))
        return results
