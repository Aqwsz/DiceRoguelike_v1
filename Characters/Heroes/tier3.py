from Characters import faces
from Characters.Heroes.hero import Hero

# Add tier 3 heroes here (same format as tier1.py).
# Warriors and tanks
class Barbarian(Hero):
    NAME = "Barbarian"
    MAX_HP = 17
    FACES = [
        faces.DAMAGE_3,
        faces.DAMAGE_3,
        faces.DAMAGE_4,
        faces.DAMAGE_4,
        faces.MISS,
        faces.MISS,
    ]


class Ragebringer(Hero):
    NAME = "Ragebringer"
    MAX_HP = 15
    FACES = [
        faces.DAMAGE_2,
        faces.DAMAGE_3,
        faces.DAMAGE_3,
        faces.DAMAGE_4,
        faces.DAMAGE_4,
        faces.MISS,
    ]
    
class Sniper(Hero):
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

class Quartermaster(Hero):
    NAME = "Quartermaster"
    MAX_HP = 10
    FACES = [
        faces.DAMAGE_3,
        faces.DAMAGE_4,
        faces.DAMAGE_4,
        faces.DAMAGE_5,
        faces.LIFE_DRAIN_3,
        faces.MISS,
    ]

class Queen(Hero):
    NAME = "Queen"
    MAX_HP = 6
    FACES = [
        faces.DAMAGE_5,
        faces.DAMAGE_6,
        faces.DAMAGE_7,
        faces.DAMAGE_8,
        faces.MISS,
        faces.MISS,
    ]

class Cleric(Hero):
    NAME = "Cleric"
    MAX_HP = 8
    FACES = [
        faces.DAMAGE_2,
        faces.DAMAGE_3,
        faces.LIFE_DRAIN_3,
        faces.HEAL_4,
        faces.HEAL_5,
        faces.MISS,
    ]


HEROES = [Barbarian, Ragebringer, Sniper, Quartermaster, Queen, Cleric]
