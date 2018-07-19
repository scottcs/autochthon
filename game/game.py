"""Main game class."""
import esper

from game.component.renderable import Renderable

MOMENTS_PER_TURN = 10


class Game:
    """Main game object."""

    def __init__(self, render_processor):
        self.game_over = False
        self.world = esper.World()
        self.player = self.world.create_entity(Renderable(
            1,
            40, 10,
            0xff3333,
            0
        ))
        self.crab = self.world.create_entity(Renderable(
            39,
            10, 10,
            0xffff33,
            1
        ))

        self.world.add_processor(render_processor)

    def update(self):
        """Update the game world."""
        self.world.process()

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

        if 'Control' in keys:
            return {}

        # TODO: Separate position from renderable?
        player_renderable = self.world.component_for_entity(self.player, Renderable)
        crab_renderable = self.world.component_for_entity(self.crab, Renderable)

        for key in keys:
            move_up = key in 'kyu'
            move_down = key in 'jbn'
            move_left = key in 'hyb'
            move_right = key in 'lun'
            if move_up:
                player_renderable.y -= 1
            if move_down:
                player_renderable.y += 1
            if move_left:
                player_renderable.x -= 1
            if move_right:
                player_renderable.x += 1

        crab_renderable.x = player_renderable.x
        crab_renderable.y = player_renderable.y

    def on_mouse_input(self, mouse) -> dict:
        return {}

    def check_for_game_over(self):
        """Return True if the game is over."""
        return False

    def check_for_time_passed(self) -> bool:
        """Return True if time has passed."""
        return True

    def process_input_event(self, event):
        """Process an input event."""
        keys = event.get('keys')
        mouse = event.get('mouse')
        if keys:
            self.on_keyboard_input(keys)
        if mouse:
            self.on_mouse_input(mouse)
