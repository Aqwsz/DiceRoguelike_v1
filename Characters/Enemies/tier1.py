from Characters import faces
from Characters.Enemies.enemy import Enemy


class Slime(Enemy):
    NAME = "Slime"
    MAX_HP = 4
    FACES = [
        faces.DAMAGE_2,        
        faces.DAMAGE_2,         
        faces.DAMAGE_2,    
        faces.DAMAGE_2,      
        faces.MISS,
        faces.MISS,         # no effect
    ]


class Goblin(Enemy):
    NAME = "Goblin"
    MAX_HP = 6
    FACES = [
        faces.DAMAGE_1,           
        faces.DAMAGE_1,          
        faces.DAMAGE_1,       
        faces.DAMAGE_2,        
        faces.DAMAGE_2,    
        faces.MISS,           # no effect
    ]


class Skeleton(Enemy):
    NAME = "Skeleton"
    MAX_HP = 8
    FACES = [
        faces.DAMAGE_1,      # 1 damage
        faces.DAMAGE_1,      # 1 damage
        faces.DAMAGE_3,      # 3 damage
        faces.MISS,         # no effect
        faces.MISS,         # no effect
        faces.MISS,           # no effect
    ]

class Crawler(Enemy):
    NAME = "Crawler"
    MAX_HP = 7
    FACES = [
        faces.DAMAGE_4,
        faces.DAMAGE_5,
        faces.MISS,
        faces.MISS,
        faces.MISS,
        faces.MISS,
    ]

ENEMIES = [Slime, Goblin, Skeleton, Crawler]
