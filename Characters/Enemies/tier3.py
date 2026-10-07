from Characters import faces
from Characters.Enemies.enemy import Enemy

# Add tier 3 enemies here (same format as tier1.py).
class Hawk(Enemy):
    NAME = "Hawk"
    MAX_HP = 16
    FACES = [
        faces.DAMAGE_4,
        faces.DAMAGE_4,
        faces.DAMAGE_4,
        faces.DAMAGE_5,
        faces.DAMAGE_5,
        faces.MISS,
    ]

class Dice(Enemy):
    NAME = "Dice"
    MAX_HP = 12
    FACES = [
        faces.LIFE_DRAIN_1,
        faces.LIFE_DRAIN_2,
        faces.LIFE_DRAIN_3,
        faces.LIFE_DRAIN_4,
        faces.LIFE_DRAIN_5,
        faces.LIFE_DRAIN_6,
    ]

class Werewolf(Enemy):
    NAME = "Werewolf"
    MAX_HP = 10
    FACES = [
        faces.DAMAGE_6,
        faces.DAMAGE_8,
        faces.DAMAGE_10,
        faces.MISS,
        faces.MISS,
        faces.MISS,
    ]

class Bomber(Enemy):
    NAME = "Bomber"
    MAX_HP = 4
    FACES = [
        faces.DAMAGE_7,
        faces.DAMAGE_8,
        faces.DAMAGE_9,
        faces.DAMAGE_10,
        faces.MISS,
        faces.MISS,
    ]

ENEMIES = [Hawk, Dice, Werewolf, Bomber]
