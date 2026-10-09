from Characters.src.dice import Face

# Every die face in the game. Edit effects here; heroes and enemies reference these by name.
#
# Combos (face + stickers) work the same way via lazy names, Slice & Dice style:
#   faces.DAMAGE_10_EXECUTE
#   faces.DAMAGE_3_POISON
#   faces.DAMAGE_2_BURN_WEAKEN
#   faces.DAMAGE_1_LIFE_DRAIN
# These return a Side (face + stickers), which Character FACES lists accept.
#
# Status effects that scale with damage are stickers (Poison, Burn, Weaken, Life Drain),
# not separate face types. Legacy names like POISON_2 / WEAKEN_1 still resolve via
# __getattr__ to DAMAGE_N + sticker(s).

# Damage: creates DAMAGE_1 ... DAMAGE_<MAX_DAMAGE>.
MAX_DAMAGE = 100
for amount in range(1, MAX_DAMAGE + 1):
    globals()[f"DAMAGE_{amount}"] = Face(f"Damage {amount}", damage=amount)

# Damage all foes
MAX_DAMAGE_ALL = 100
for amount in range(1, MAX_DAMAGE_ALL + 1):
    globals()[f"DAMAGE_ALL_{amount}"] = Face(f"Damage All {amount}", damage_all=amount)

# Heal: restores HP on the living ally with the lowest current HP.
MAX_HEAL = 100
for amount in range(1, MAX_HEAL + 1):
    globals()[f"HEAL_{amount}"] = Face(f"Heal {amount}", heal=amount)

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

# Legacy status faces -> DAMAGE_N + sticker(s). Longer prefixes first.
_LEGACY_STATUS = (
    ("POISON_BURN_", ("POISON", "BURN")),
    ("LIFE_DRAIN_", ("LIFE_DRAIN",)),
    ("POISON_", ("POISON",)),
    ("BURN_", ("BURN",)),
    ("WEAKEN_", ("WEAKEN",)),
)


def __getattr__(name):
    """Lazy face+sticker recipes, plus legacy POISON_N / BURN_N / WEAKEN_N / LIFE_DRAIN_N."""
    from Characters.src.combo import Side, match_sticker_suffixes, parse_side_name, sticker_aliases

    for prefix, sticker_keys in _LEGACY_STATUS:
        if not name.startswith(prefix):
            continue
        rest = name[len(prefix):]
        amount_str, sep, sticker_tail = rest.partition("_")
        if not amount_str.isdigit():
            break
        amount = int(amount_str)
        if amount < 1 or amount > MAX_DAMAGE:
            break
        aliases = sticker_aliases()
        stickers = []
        for key in sticker_keys:
            sticker = aliases.get(key)
            if sticker is None:
                raise AttributeError(f"legacy recipe {name!r}: missing sticker {key}")
            stickers.append(sticker)
        if sep and sticker_tail:
            stickers.extend(match_sticker_suffixes("_" + sticker_tail, aliases))
        side = Side(globals()[f"DAMAGE_{amount}"], tuple(stickers))
        globals()[name] = side
        return side

    plain = {key: value for key, value in globals().items() if isinstance(value, Face)}
    try:
        side = parse_side_name(name, faces_map=plain)
    except ValueError as err:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from err
    if not side.stickers:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    globals()[name] = side
    return side
