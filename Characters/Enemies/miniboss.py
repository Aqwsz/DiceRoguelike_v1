from Characters import faces
from Characters.Enemies.enemy import Enemy


class Witch(Enemy): # Big damage
    NAME = "Witch"
    MAX_HP = 16
    FACES = [
        faces.DAMAGE_3_FIRSTSTRIKE,       
        faces.DAMAGE_5,      
        faces.DAMAGE_6,       
        faces.HEAL_3,       
        faces.MISS,
        faces.MISS,      
    ]


class Pirate(Enemy): # Consistent
    NAME = "Pirate"
    MAX_HP = 18
    FACES = [
        faces.DAMAGE_3_FIRSTSTRIKE,   
        faces.DAMAGE_3_FIRSTSTRIKE,   
        faces.DAMAGE_3,   
        faces.DAMAGE_3,   
        faces.DAMAGE_3,   
        faces.HEAL_2,     
    ]


class Bloodsucker(Enemy): # Annoying
    NAME = "Bloodsucker"
    MAX_HP = 14
    FACES = [
        faces.DAMAGE_3_FIRSTSTRIKE,      # 1 damage
        faces.DAMAGE_3,      # 1 damage
        faces.DAMAGE_3,      # 2 damage
        faces.LIFE_DRAIN_1_FIRSTSTRIKE,         # 1 damage, 1 heal
        faces.LIFE_DRAIN_1_FIRSTSTRIKE,         # 1 damage, 1 heal
        faces.LIFE_DRAIN_2,           # 2 damage, 2 heal
    ]


ENEMIES = [Witch, Pirate, Bloodsucker]
