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

# Poison: N damage now, plus N poison on the target.
MAX_POISON = 100
for amount in range(1, MAX_POISON + 1):
    globals()[f"POISON_{amount}"] = Face(f"Poison {amount}", damage=amount, poison=amount)

# Group heal: heals the user and every living ally by N.
MAX_GROUP_HEAL = 100
for amount in range(1, MAX_GROUP_HEAL + 1):
    globals()[f"GROUP_HEAL_{amount}"] = Face(f"Group Heal {amount}", group_heal=amount)

# No effect
MISS = Face("Miss")
