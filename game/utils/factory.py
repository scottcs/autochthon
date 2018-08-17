"""Factory utilities."""
from game.component.movement import Position
from game.types import Entity
from game.world import World
from gamedata.entity.assemblage.player import Player
from gamedata.entity.assemblage.enemy import Enemy


def make_player(world: World, x: int, y: int, *variations) -> Entity:
    """Make a player and add it to the world."""
    player = world.assemble_entity(Player, *variations)
    world.players.add(player)
    pos = world.component_for_entity(player, Position)
    pos.x = x
    pos.y = y
    return player


def make_enemy(world: World, x: int, y: int, *variations) -> Entity:
    """Make an enemy and add it to the world."""
    enemy = world.assemble_entity(Enemy, *variations)
    pos = world.component_for_entity(enemy, Position)
    pos.x = x
    pos.y = y
    return enemy
