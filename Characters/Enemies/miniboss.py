from Characters import faces
from Characters.Enemies.enemy import Enemy


class Witch(Enemy): # Big damage
    NAME = "Witch"
    MAX_HP = 8
    FACES = [
        faces.DAMAGE_4,       
        faces.DAMAGE_5,      
        faces.DAMAGE_6,       
        faces.HEAL_3,       
        faces.MISS,
        faces.MISS,      
    ]


class Pirate(Enemy): # Consistent
    NAME = "Pirate"
    MAX_HP = 9
    FACES = [
        faces.DAMAGE_2,           # 2 damage
        faces.DAMAGE_2,           # 2 damage
        faces.DAMAGE_2,          # 2 damage
        faces.DAMAGE_2,          # 2 damage
        faces.DAMAGE_2,     # 2 damage
        faces.HEAL_2,           # 2 heal
    ]


class Bloodsucker(Enemy): # Annoying
    NAME = "Bloodsucker"
    MAX_HP = 7
    FACES = [
        faces.DAMAGE_2,      # 1 damage
        faces.DAMAGE_2,      # 1 damage
        faces.DAMAGE_2,      # 2 damage
        faces.LIFE_DRAIN_1,         # 1 damage, 1 heal
        faces.LIFE_DRAIN_1,         # 1 damage, 1 heal
        faces.LIFE_DRAIN_2,           # 2 damage, 2 heal
    ]


ENEMIES = [Witch, Pirate, Bloodsucker]
