from Characters import faces
from Characters.Enemies.enemy import Enemy
from Characters.Enemies.tier1 import Skeleton

# Bosses. Add them here (same format as tier1.py).

class Dragon(Enemy):
    NAME = "Dragon"
    MAX_HP = 40
    FACES = [
        faces.DAMAGE_14,
        faces.DAMAGE_14,
        faces.LIFE_DRAIN_10,
        faces.LIFE_DRAIN_11,
        faces.LIFE_DRAIN_12,
        faces.HEAL_20,
    ]

class Graveyard_King(Enemy):
    NAME = "Graveyard King"
    MAX_HP = 30
    FACES = [
        faces.DAMAGE_10,
        faces.DAMAGE_10,
        faces.DAMAGE_10,
        faces.DAMAGE_10,
        faces.HEAL_10,
        faces.HEAL_10,
    ]
    SPAWN_ON_DEATH = {Skeleton: 2}

ENEMIES = [Dragon, Graveyard_King]
