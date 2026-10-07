from Characters import faces
from Characters.Heroes.hero import Hero

# Warriors and tanks
class Knight(Hero):
    NAME = "Knight"
    MAX_HP = 14
    FACES = [
        faces.DAMAGE_2,
        faces.DAMAGE_3,
        faces.DAMAGE_3,
        faces.DAMAGE_4,
        faces.MISS,
        faces.MISS,
    ]

class Paladin(Hero):
    NAME = "Paladin"
    MAX_HP = 11
    FACES = [
        faces.DAMAGE_2,
        faces.DAMAGE_2,
        faces.DAMAGE_2,
        faces.DAMAGE_3,
        faces.DAMAGE_3,
        faces.MISS,
    ]

# Damage dealers
class Assassin(Hero):
    NAME = "Assassin"
    MAX_HP = 9
    FACES = [
        faces.DAMAGE_2,
        faces.DAMAGE_3,
        faces.DAMAGE_4,
        faces.DAMAGE_4,
        faces.HEAL_2,
        faces.MISS,
    ]

class Hunter(Hero):
    NAME = "Hunter"
    MAX_HP = 8
    FACES = [
        faces.DAMAGE_2,
        faces.DAMAGE_3,
        faces.DAMAGE_4,
        faces.LIFE_DRAIN_1,
        faces.LIFE_DRAIN_2,
        faces.MISS,
    ]

class Magician(Hero):
    NAME = "Magician"
    MAX_HP = 6
    FACES = [
        faces.DAMAGE_3,
        faces.DAMAGE_4,
        faces.DAMAGE_5,
        faces.HEAL_2,
        faces.MISS,
        faces.MISS,
    ]

class Sorcerer(Hero):
    NAME = "Sorcerer"
    MAX_HP = 6
    FACES = [
        faces.DAMAGE_4,
        faces.DAMAGE_4,
        faces.DAMAGE_5,
        faces.HEAL_1,
        faces.MISS,
        faces.MISS,
    ]

HEROES = [Knight, Paladin, Assassin, Hunter, Magician, Sorcerer]
