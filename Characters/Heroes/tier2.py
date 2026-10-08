from Characters import faces
from Characters.Heroes.hero import Hero
from Characters.Heroes.colors import Grey, Orange, Blue, Red

########################################################
# Warriors and tanks (Grey)

class Knight(Hero, Grey):
    NAME = "Knight"
    MAX_HP = 14
    FACES = [
        faces.DAMAGE_2,
        faces.DAMAGE_3,
        faces.DAMAGE_3,
        faces.SHIELD_2,
        faces.STUN,
        faces.MISS,
    ]

class Paladin(Hero, Grey):
    NAME = "Paladin"
    MAX_HP = 11
    FACES = [
        faces.DAMAGE_2,
        faces.DAMAGE_2,
        faces.DAMAGE_3,
        faces.SHIELD_3,
        faces.SHIELD_3,
        faces.MISS,
    ]

########################################################
# Damage dealers (Orange)

class Assassin(Hero, Orange):
    NAME = "Assassin"
    MAX_HP = 9
    FACES = [
        faces.DAMAGE_2,
        faces.DAMAGE_3,
        faces.DAMAGE_4,
        faces.DAMAGE_4,
        faces.WEAKEN_1,
        faces.MISS,
    ]

class Hunter(Hero, Orange):
    NAME = "Hunter"
    MAX_HP = 8
    FACES = [
        faces.DAMAGE_ALL_1,
        faces.DAMAGE_3,
        faces.DAMAGE_4,
        faces.LIFE_DRAIN_1,
        faces.LIFE_DRAIN_2,
        faces.MISS,
    ]

########################################################
# Magic (Blue)

class Magician(Hero, Blue):
    NAME = "Magician"
    MAX_HP = 6
    FACES = [
        faces.DAMAGE_3,
        faces.DAMAGE_4,
        faces.MANA_3,
        faces.HEAL_2,
        faces.MISS,
        faces.MISS,
    ]

class Sorcerer(Hero, Blue):
    NAME = "Sorcerer"
    MAX_HP = 6
    FACES = [
        faces.DAMAGE_4,
        faces.DAMAGE_4,
        faces.MANA_2,
        faces.HEAL_1,
        faces.MISS,
        faces.MISS,
    ]

########################################################
# Supporters (Red)

class Medic(Hero, Red):
    NAME = "Medic"
    MAX_HP = 8
    FACES = [
        faces.HEAL_2,
        faces.HEAL_2,
        faces.HEAL_3,
        faces.HEAL_3,
        faces.GROUP_HEAL_2,
        faces.MISS,
    ]

class Alchemist(Hero, Red):
    NAME = "Alchemist"
    MAX_HP = 8
    FACES = [
        faces.POISON_1,
        faces.BURN_2,
        faces.GROUP_HEAL_2,
        faces.GROUP_HEAL_3,
        faces.WEAKEN_1,
        faces.MISS,
    ]

HEROES = [Knight, Paladin, Assassin, Hunter, Magician, Sorcerer, Medic, Alchemist]
