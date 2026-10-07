from Characters import faces
from Characters.Heroes.hero import Hero

# Bruisers and tanks
class Warrior(Hero):
    NAME = "Warrior"
    MAX_HP = 10
    FACES = [
        faces.DAMAGE_1,         # 1 damage
        faces.DAMAGE_1,         # 1 damage
        faces.DAMAGE_1,         # 1 damage
        faces.DAMAGE_1,         # 1 damage
        faces.DAMAGE_2,         # 2 damage
        faces.MISS,          # no effect
    ]

class Berserker(Hero):
    NAME = "Berserker"
    MAX_HP = 7
    FACES = [
        faces.DAMAGE_1,         # 1 damage
        faces.DAMAGE_1,         # 1 damage
        faces.DAMAGE_2,         # 2 damage
        faces.DAMAGE_2,         # 2 damage
        faces.MISS,
        faces.MISS,

    ]



#Damage dealers
class Archer(Hero):
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

class Rogue(Hero):
    NAME = "Rogue"
    MAX_HP = 5
    FACES = [
        faces.DAMAGE_1,         # 1 damage
        faces.DAMAGE_1,         # 1 damage
        faces.DAMAGE_2,         # 2 damage
        faces.LIFE_DRAIN_1,
        faces.LIFE_DRAIN_1,
        faces.HEAL_1,
    ]


#Magic (high damage but risky)
class Mage(Hero):
    NAME = "Mage"
    MAX_HP = 5
    FACES = [
        faces.DAMAGE_3,      # 3 damage
        faces.DAMAGE_3,      # 3 damage
        faces.HEAL_1,        # 1 heal
        faces.HEAL_1,        # 1 heal
        faces.MISS,          # no effect
        faces.MISS,          # no effect
    ]

class Speller(Hero):
    NAME = "Speller"
    MAX_HP = 4
    FACES = [
        faces.DAMAGE_2,
        faces.DAMAGE_2,
        faces.DAMAGE_3,
        faces.HEAL_2,
        faces.MISS,
        faces.MISS,
    ]

#Supporters

class Potioner(Hero):
    NAME = "Potioner"
    MAX_HP = 6
    FACES = [
        faces.POISON_1,
        faces.POISON_1,
        faces.GROUP_HEAL_1,
        faces.GROUP_HEAL_1,
        faces.MISS,
        faces.MISS,
    ]



HEROES = [Warrior, Berserker, Archer, Rogue, Mage, Speller, Potioner]
