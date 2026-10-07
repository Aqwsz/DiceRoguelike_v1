from Characters import faces
from Characters.Enemies.enemy import Enemy


class Slime(Enemy):
    NAME = "Slime"
    MAX_HP = 4
    FACES = [
        faces.DAMAGE_1,         # 1 damage
        faces.DAMAGE_1,         # 1 damage
        faces.DAMAGE_2,         # 2 damage
        faces.DAMAGE_2,         # 2 damage
        faces.MISS,
        faces.MISS,         # no effect
    ]


class Goblin(Enemy):
    NAME = "Goblin"
    MAX_HP = 6
    FACES = [
        faces.DAMAGE_1,           # 1 damage
        faces.DAMAGE_1,           # 1 damage
        faces.DAMAGE_1,          # 2 damage
        faces.DAMAGE_2,          # 2 damage
        faces.DAMAGE_2,     # 3 damage
        faces.MISS,           # no effect
    ]


class Skeleton(Enemy):
    NAME = "Skeleton"
    MAX_HP = 8
    FACES = [
        faces.DAMAGE_2,      # 1 damage
        faces.DAMAGE_3,      # 1 damage
        faces.DAMAGE_3,      # 3 damage
        faces.MISS,         # no effect
        faces.MISS,         # no effect
        faces.MISS,           # no effect
    ]


ENEMIES = [Slime, Goblin, Skeleton]
