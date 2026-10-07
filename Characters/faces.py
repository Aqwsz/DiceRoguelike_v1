from Characters.dice import Face

# Every die face in the game. Edit effects here; heroes and enemies reference these by name.

# Damage: creates DAMAGE_1 ... DAMAGE_<MAX_DAMAGE>.
MAX_DAMAGE = 100
for amount in range(1, MAX_DAMAGE + 1):
    globals()[f"DAMAGE_{amount}"] = Face(f"Damage {amount}", damage=amount)

# Heal
MAX_HEAL = 100
for amount in range(1, MAX_HEAL + 1):
    globals()[f"HEAL_{amount}"] = Face(f"Heal {amount}", heal=amount)

# Damage + heal
MAX_LIFE_DRAIN = 100
for amount in range(1, MAX_LIFE_DRAIN + 1):
    globals()[f"LIFE_DRAIN_{amount}"] = Face(f"Drain Life {amount}", damage=amount, heal=amount)

# No effect
MISS = Face("Miss")
