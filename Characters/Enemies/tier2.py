from Characters import faces
from Characters.src.enemy import Enemy
from Characters.Enemies.tier1 import Slime

# Add tier 2 enemies here (same format as tier1.py).
class Ogre(Enemy):
    NAME = "Ogre"
    MAX_HP = 12
    FACES = [
        faces.DAMAGE_2,
        faces.DAMAGE_2,
        faces.DAMAGE_2,
        faces.DAMAGE_3,
        faces.DAMAGE_3,
        faces.HEAL_2,
    ]

class Troll(Enemy):
    NAME = "Troll"
    MAX_HP = 14
    FACES = [
        faces.DAMAGE_5,
        faces.DAMAGE_5,
        faces.DAMAGE_2_LIFE_DRAIN,
        faces.MISS,
        faces.MISS,
        faces.MISS,
    ]

class Vampire(Enemy):
    NAME = "Vampire"
    MAX_HP = 6
    FACES = [
        faces.DAMAGE_4,
        faces.DAMAGE_4,
        faces.DAMAGE_3_LIFE_DRAIN,
        faces.DAMAGE_3_LIFE_DRAIN,
        faces.DAMAGE_3_LIFE_DRAIN,
        faces.MISS,
    ]

class Slime_Mother(Enemy):
    NAME = "Slime Mother"
    MAX_HP = 10
    FACES = [
        faces.DAMAGE_2,
        faces.DAMAGE_2,
        faces.DAMAGE_3,
        faces.DAMAGE_3,
        faces.MISS,
        faces.MISS,
    ]
    SPAWN_ON_DEATH = {Slime: 2}

ENEMIES = [Ogre, Troll, Vampire, Slime_Mother]
