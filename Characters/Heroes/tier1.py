from Characters import faces
from Characters.src.hero import Hero
from Characters.Heroes.colors import Grey, Orange, Blue, Red

########################################################
# Bruisers and tanks (Grey)

class Warrior(Hero, Grey):
    NAME = "Warrior"
    MAX_HP = 10
    FACES = [
        faces.DAMAGE_1,         # 1 damage
        faces.DAMAGE_1,         # 1 damage
        faces.DAMAGE_1,         # 1 damage
        faces.DAMAGE_2,         # 1 damage
        faces.SHIELD_1,         # 2 damage
        faces.MISS,          # no effect
    ]

class Berserker(Hero, Grey):
    NAME = "Berserker"
    MAX_HP = 7
    FACES = [
        faces.DAMAGE_1,         # 1 damage
        faces.DAMAGE_1,         # 1 damage
        faces.DAMAGE_2,         # 2 damage
        faces.SHIELD_2,         # 2 damage
        faces.MISS,
        faces.MISS,

    ]

########################################################
#Damage dealers (Orange)

class Archer(Hero, Orange):
    NAME = "Archer"
    MAX_HP = 7
    FACES = [
        faces.DAMAGE_1,         # 1 damage
        faces.DAMAGE_1,         # 1 damage
        faces.DAMAGE_1,         # 1 damage
        faces.DAMAGE_2,
        faces.HEAL_1,
        faces.MISS,          # no effect
    ]

class Rogue(Hero, Orange):
    NAME = "Rogue"
    MAX_HP = 5
    FACES = [
        faces.DAMAGE_1,         # 1 damage
        faces.DAMAGE_1,         # 1 damage
        faces.DAMAGE_2,         # 2 damage
        faces.DAMAGE_1_LIFE_DRAIN,
        faces.DAMAGE_1_LIFE_DRAIN,
        faces.HEAL_1,
    ]

########################################################
#Magic (high damage, mana, but risky) (Blue)

class Mage(Hero, Blue):
    NAME = "Mage"
    MAX_HP = 5
    FACES = [
        faces.DAMAGE_3,   
        faces.MANA_2,     
        faces.MANA_2,     
        faces.HEAL_1,     
        faces.MISS,       
        faces.MISS,       
    ]

class Speller(Hero, Blue):
    NAME = "Speller"
    MAX_HP = 4
    FACES = [
        faces.MANA_1,
        faces.MANA_1,
        faces.MANA_2,
        faces.MANA_2,
        faces.HEAL_2,
        faces.MISS,
    ]

########################################################
#Supporters (Red)

class Healer(Hero, Red):
    NAME = "Healer"
    MAX_HP = 6
    FACES = [
        faces.HEAL_1,
        faces.HEAL_1,
        faces.HEAL_2,
        faces.HEAL_2,
        faces.MISS,
        faces.MISS,
    ]

class Potioner(Hero, Red):
    NAME = "Potioner"
    MAX_HP = 6
    FACES = [
        faces.DAMAGE_1_POISON,
        faces.DAMAGE_1_POISON,
        faces.GROUP_HEAL_1,
        faces.GROUP_HEAL_1,
        faces.MISS,
        faces.MISS,
    ]



HEROES = [Warrior, Berserker, Archer, Rogue, Mage, Speller, Healer, Potioner]
