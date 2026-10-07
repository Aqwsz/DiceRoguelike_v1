from Characters import faces
from Characters.Enemies.enemy import Enemy

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
        faces.LIFE_DRAIN_2,
        faces.MISS,
        faces.MISS,
        faces.MISS,
    ]

ENEMIES = [Ogre, Troll]
