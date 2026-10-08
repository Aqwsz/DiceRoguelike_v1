from Characters import faces
from Characters.Heroes.hero import Hero
from Characters.Heroes.colors import Grey, Orange, Blue, Red

########################################################
# Warriors and tanks (Grey)

class Barbarian(Hero, Grey):
    NAME = "Barbarian"
    MAX_HP = 17
    FACES = [
        faces.DAMAGE_3,
        faces.DAMAGE_3,
        faces.SHIELD_4,
        faces.SHIELD_5,
        faces.SHIELD_6,
        faces.MISS,
    ]


class Ragebringer(Hero, Grey):
    NAME = "Ragebringer"
    MAX_HP = 15
    FACES = [
        faces.DAMAGE_4,
        faces.DAMAGE_4,
        faces.SHIELD_4,
        faces.STUN,
        faces.THORNS,
        faces.MISS,
    ]
    
########################################################
# Damage dealers (Orange)

class Sniper(Hero, Orange):
    NAME = "Sniper"
    MAX_HP = 8
    FACES = [
        faces.DAMAGE_4,
        faces.DAMAGE_4,
        faces.DAMAGE_5,
        faces.DAMAGE_6,
        faces.LIFE_DRAIN_4,
        faces.MISS,
    ]

class Quartermaster(Hero, Orange):
    NAME = "Quartermaster"
    MAX_HP = 10
    FACES = [
        faces.DAMAGE_3,
        faces.DAMAGE_4,
        faces.DAMAGE_4,
        faces.DAMAGE_ALL_1,
        faces.LIFE_DRAIN_3,
        faces.MISS,
    ]

########################################################
# Magic (Blue)

class Queen(Hero, Blue):
    NAME = "Queen"
    MAX_HP = 6
    FACES = [
        faces.DAMAGE_5,
        faces.DAMAGE_6,
        faces.DAMAGE_7,
        faces.DAMAGE_8,
        faces.MANA_4,
        faces.MISS,
    ]

class Cleric(Hero, Blue):
    NAME = "Cleric"
    MAX_HP = 8
    FACES = [
        faces.POISON_2,
        faces.BURN_3,
        faces.LIFE_DRAIN_3,
        faces.MANA_3,
        faces.HEAL_4,
        faces.MISS,
    ]

########################################################
# Supporters (Red)

class Doctor(Hero, Red):
    NAME = "Doctor"
    MAX_HP = 8
    FACES = [
        faces.HEAL_3,
        faces.HEAL_3,
        faces.HEAL_3,
        faces.HEAL_3,
        faces.GROUP_HEAL_5,
        faces.GROUP_HEAL_5,
    ]

class Chemist(Hero, Red):
    NAME = "Chemist"
    MAX_HP = 10
    FACES = [
        faces.POISON_3,
        faces.WEAKEN_2,
        faces.GROUP_HEAL_4,
        faces.GROUP_HEAL_4,
        faces.MISS,
        faces.MISS,
    ]


HEROES = [Barbarian, Ragebringer, Sniper, Quartermaster, Queen, Cleric, Doctor, Chemist]
