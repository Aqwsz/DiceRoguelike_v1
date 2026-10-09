from Characters import faces
from Characters.src.enemy import Enemy


class Witch(Enemy): # Big damage
    NAME = "Witch"
    MAX_HP = 16
    FACES = [
        faces.DAMAGE_3_FIRSTSTRIKE,       
        faces.DAMAGE_5,      
        faces.DAMAGE_6,       
        faces.HEAL_3,       
        faces.DAMAGE_2_POISON,
        faces.MISS,      
    ]


class Pirate(Enemy): # Consistent
    NAME = "Pirate"
    MAX_HP = 18
    FACES = [
        faces.DAMAGE_3_FIRSTSTRIKE,   
        faces.DAMAGE_3_FIRSTSTRIKE,   
        faces.DAMAGE_3,   
        faces.DAMAGE_2_BURN,
        faces.DAMAGE_3_BURN,   
        faces.HEAL_2,     
    ]


class Bloodsucker(Enemy): # Annoying
    NAME = "Bloodsucker"
    MAX_HP = 14
    FACES = [
        faces.DAMAGE_3_FIRSTSTRIKE,    
        faces.DAMAGE_2_POISON,      
        faces.DAMAGE_2_POISON,     
        faces.DAMAGE_1_LIFE_DRAIN_FIRSTSTRIKE,    
        faces.DAMAGE_1_LIFE_DRAIN_FIRSTSTRIKE,    
        faces.DAMAGE_2_LIFE_DRAIN,          
    ]


ENEMIES = [Witch, Pirate, Bloodsucker]
