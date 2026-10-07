from Characters.dice import Face

# Every die face in the game. Edit effects here; heroes and enemies reference these by name.

# Damage
DAMAGE_1 = Face("Jab", damage=1)
DAMAGE_2 = Face("Slash", damage=2)
DAMAGE_3 = Face("Bash", damage=3)
DAMAGE_4 = Face("Crush", damage=4)
DAMAGE_5 = Face("Smash", damage=5)
DAMAGE_6 = Face("Bone Club", damage=6)

# Heal
HEAL_1 = Face("Bandage", heal=1)
HEAL_2 = Face("Second Wind", heal=2)
HEAL_3 = Face("Vigor", heal=3)
HEAL_4 = Face("Revitalize", heal=4)

# Damage + heal
LIFE_DRAIN_1 = Face("Drain Life 1", damage=1, heal=1)
LIFE_DRAIN_2 = Face("Drain Life 2", damage=2, heal=2)
LIFE_DRAIN_3 = Face("Drain Life 3", damage=3, heal=3)
LIFE_DRAIN_4 = Face("Drain Life 4", damage=4, heal=4)
LIFE_DRAIN_5 = Face("Drain Life 5", damage=5, heal=5)
LIFE_DRAIN_6 = Face("Drain Life 6", damage=6, heal=6)
LIFE_DRAIN_7 = Face("Drain Life 7", damage=7, heal=7)
LIFE_DRAIN_8 = Face("Drain Life 8", damage=8, heal=8)
LIFE_DRAIN_9 = Face("Drain Life 9", damage=9, heal=9)
LIFE_DRAIN_10 = Face("Drain Life 10", damage=10, heal=10)

# No effect
MISS = Face("Miss")
