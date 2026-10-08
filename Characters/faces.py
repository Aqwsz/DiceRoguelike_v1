from Characters.dice import Face

# Every die face in the game. Edit effects here; heroes and enemies reference these by name.
#
# Combos (face + stickers) work the same way via lazy names, Slice & Dice style:
#   faces.DAMAGE_10_EXECUTE
#   faces.DAMAGE_3_SINGLEUSE_FIRSTSTRIKE
# These return a Side (face + stickers), which Character FACES lists accept.

# Damage: creates DAMAGE_1 ... DAMAGE_<MAX_DAMAGE>.
MAX_DAMAGE = 100
for amount in range(1, MAX_DAMAGE + 1):
    globals()[f"DAMAGE_{amount}"] = Face(f"Damage {amount}", damage=amount)

# Damage all foes
MAX_DAMAGE_ALL = 100
for amount in range(1, MAX_DAMAGE_ALL + 1):
    globals()[f"DAMAGE_ALL_{amount}"] = Face(f"Damage All {amount}", damage_all=amount)

# Heal
MAX_HEAL = 100
for amount in range(1, MAX_HEAL + 1):
    globals()[f"HEAL_{amount}"] = Face(f"Heal {amount}", heal=amount)

# Damage + heal
MAX_LIFE_DRAIN = 100
for amount in range(1, MAX_LIFE_DRAIN + 1):
    globals()[f"LIFE_DRAIN_{amount}"] = Face(f"Drain Life {amount}", damage=amount, heal=amount)

# Poison: N damage now, plus N poison on the target (does not fade by default).
MAX_POISON = 100
for amount in range(1, MAX_POISON + 1):
    globals()[f"POISON_{amount}"] = Face(f"Poison {amount}", damage=amount, poison=amount)

# Burn: N damage now, plus N burn (fades by 1 each round after ticking).
MAX_BURN = 100
for amount in range(1, MAX_BURN + 1):
    globals()[f"BURN_{amount}"] = Face(f"Burn {amount}", damage=amount, burn=amount)

# Weaken: N damage now, and target deals N less damage.
MAX_WEAKEN = 100
for amount in range(1, MAX_WEAKEN + 1):
    globals()[f"WEAKEN_{amount}"] = Face(f"Weaken {amount}", damage=amount, weaken=amount)

# Shield: N shield on a random ally this round only.
MAX_SHIELD = 100
for amount in range(1, MAX_SHIELD + 1):
    globals()[f"SHIELD_{amount}"] = Face(f"Shield {amount}", shield=amount)

# Group heal: heals the user and every living ally by N.
MAX_GROUP_HEAL = 100
for amount in range(1, MAX_GROUP_HEAL + 1):
    globals()[f"GROUP_HEAL_{amount}"] = Face(f"Group Heal {amount}", group_heal=amount)

# Mana: adds N to the party's mana pool (autospell spends 5 for 8 damage).
MAX_MANA = 100
for amount in range(1, MAX_MANA + 1):
    globals()[f"MANA_{amount}"] = Face(f"Mana {amount}", mana=amount)

# Stun: stun a random foe (they skip their next roll).
STUN = Face("Stun", stun=True)

# Thorns: give a random ally thorns (attackers take the hit instead).
THORNS = Face("Thorns", thorns=True)

# No effect
MISS = Face("Miss")


def __getattr__(name):
    """Lazy face+sticker recipes, e.g. DAMAGE_10_EXECUTE -> Side(DAMAGE_10, (EXECUTE,))."""
    from Characters.combo import parse_side_name

    plain = {key: value for key, value in globals().items() if isinstance(value, Face)}
    try:
        side = parse_side_name(name, faces_map=plain)
    except ValueError as err:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from err
    if not side.stickers:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    globals()[name] = side
    return side
