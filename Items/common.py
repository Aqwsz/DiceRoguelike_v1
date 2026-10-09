from Characters import faces, stickers
from Characters.src.combo import match_sticker_suffixes, parse_side_name, face_table, sticker_aliases
from Characters.src.dice import Face
from Characters.stickers import Sticker
from Items.src.item import (
    MaxHpItem,
    PartyMaxHpItem,
    FaceSwapItem,
    StickerItem,
    MultiStickerItem,
    DamageBoostItem,
    DamageAllBoostItem,
    HealBoostItem,
    HealAllBoostItem,
    ShieldBoostItem,
    ManaBoostItem,
    PoisonBoostItem,
    BurnBoostItem,
)

# Ready-made items, so tier files can just list them, e.g.
#   ITEMS = [common.MAX_HP_ITEM_2, common.FACE_SWAP_DAMAGE_3_SINGLEUSE]
#
# Same combo naming as faces.py / Characters/combo.py:
#   FACE_SWAP_DAMAGE_3
#   FACE_SWAP_DAMAGE_3_SINGLEUSE
#   FACE_SWAP_DAMAGE_3_SINGLE_USE_EXECUTE
# Multi-sticker (no face swap): STICKER_EXECUTE_FIRST_STRIKE

# MAX_HP_ITEM_1 ... : +N max HP for one hero (permanent).
MAX_HP_ITEM_LIMIT = 100
for amount in range(1, MAX_HP_ITEM_LIMIT + 1):
    name = f"MAX_HP_ITEM_{amount}"
    globals()[name] = type(name, (MaxHpItem,), {"NAME": f"Toughness +{amount}", "AMOUNT": amount})

# PARTY_MAX_HP_ITEM_1 ... : +N max HP for every hero (permanent).
PARTY_MAX_HP_ITEM_LIMIT = 100
for amount in range(1, PARTY_MAX_HP_ITEM_LIMIT + 1):
    name = f"PARTY_MAX_HP_ITEM_{amount}"
    globals()[name] = type(name, (PartyMaxHpItem,), {"NAME": f"Rations +{amount}", "AMOUNT": amount})

# DAMAGE_BOOST_1 ... : +N to every plain damage face on the holder's die (not damage-all).
DAMAGE_BOOST_LIMIT = 100
for amount in range(1, DAMAGE_BOOST_LIMIT + 1):
    name = f"DAMAGE_BOOST_{amount}"
    globals()[name] = type(
        name,
        (DamageBoostItem,),
        {"NAME": f"Sharpen +{amount}", "AMOUNT": amount},
    )

# DAMAGE_ALL_BOOST_1 ... : +N to every damage-all face on the holder's die.
DAMAGE_ALL_BOOST_LIMIT = 100
for amount in range(1, DAMAGE_ALL_BOOST_LIMIT + 1):
    name = f"DAMAGE_ALL_BOOST_{amount}"
    globals()[name] = type(
        name,
        (DamageAllBoostItem,),
        {"NAME": f"Cleave Edge +{amount}", "AMOUNT": amount},
    )

# HEAL_BOOST_1 ... : +N to every plain heal face on the holder's die (not group heal).
HEAL_BOOST_LIMIT = 100
for amount in range(1, HEAL_BOOST_LIMIT + 1):
    name = f"HEAL_BOOST_{amount}"
    globals()[name] = type(
        name,
        (HealBoostItem,),
        {"NAME": f"Bandages +{amount}", "AMOUNT": amount},
    )

# HEAL_ALL_BOOST_1 ... : +N to every group-heal face on the holder's die.
HEAL_ALL_BOOST_LIMIT = 100
for amount in range(1, HEAL_ALL_BOOST_LIMIT + 1):
    name = f"HEAL_ALL_BOOST_{amount}"
    globals()[name] = type(
        name,
        (HealAllBoostItem,),
        {"NAME": f"Field Dressing +{amount}", "AMOUNT": amount},
    )

# SHIELD_BOOST_1 ... : +N to every shield face on the holder's die.
SHIELD_BOOST_LIMIT = 100
for amount in range(1, SHIELD_BOOST_LIMIT + 1):
    name = f"SHIELD_BOOST_{amount}"
    globals()[name] = type(
        name,
        (ShieldBoostItem,),
        {"NAME": f"Plating +{amount}", "AMOUNT": amount},
    )

# MANA_BOOST_1 ... : +N to every mana face on the holder's die.
MANA_BOOST_LIMIT = 100
for amount in range(1, MANA_BOOST_LIMIT + 1):
    name = f"MANA_BOOST_{amount}"
    globals()[name] = type(
        name,
        (ManaBoostItem,),
        {"NAME": f"Focus +{amount}", "AMOUNT": amount},
    )

# POISON_BOOST_1 ... : +N damage on faces that already have the Poison sticker.
POISON_BOOST_LIMIT = 100
for amount in range(1, POISON_BOOST_LIMIT + 1):
    name = f"POISON_BOOST_{amount}"
    globals()[name] = type(
        name,
        (PoisonBoostItem,),
        {
            "NAME": f"Venom Edge +{amount}",
            "AMOUNT": amount,
            "STICKER": stickers.POISON,
        },
    )

# BURN_BOOST_1 ... : +N damage on faces that already have the Burn sticker.
BURN_BOOST_LIMIT = 100
for amount in range(1, BURN_BOOST_LIMIT + 1):
    name = f"BURN_BOOST_{amount}"
    globals()[name] = type(
        name,
        (BurnBoostItem,),
        {
            "NAME": f"Ember Edge +{amount}",
            "AMOUNT": amount,
            "STICKER": stickers.BURN,
        },
    )

_FACES = face_table()
_STICKER_ALIASES = sticker_aliases()

# Face-swap recipes for specialty bases (and sticker combos) are available as:
#   FACE_SWAP_MANA_1, FACE_SWAP_DAMAGE_ALL_2, FACE_SWAP_GROUP_HEAL_1,
#   FACE_SWAP_DAMAGE_1_LIFE_DRAIN, FACE_SWAP_DAMAGE_2_POISON, FACE_SWAP_DAMAGE_1_BURN, ...
# Plain FACE_SWAP_<face> for every Face in faces.py is built below; sticker combos
# are created lazily via __getattr__.


def _face_swap_item(name):
    """Build FACE_SWAP_<FACE> or FACE_SWAP_<FACE>_<STICKER>_... item class."""
    body = name[len("FACE_SWAP_"):]
    try:
        side = parse_side_name(body, faces_map=_FACES, aliases=_STICKER_ALIASES)
    except ValueError:
        return None
    return type(
        name,
        (FaceSwapItem,),
        {
            "NAME": f"New Face: {side.name}",
            "NEW_FACE": side.face,
            "STICKERS": side.stickers,
        },
    )


def _sticker_stack_item(name):
    """Build STICKER_<A>_<B>_... that applies several stickers to one face."""
    body = name[len("STICKER_"):]
    try:
        sticker_list = match_sticker_suffixes("_" + body, _STICKER_ALIASES)
    except ValueError:
        return None
    if len(sticker_list) < 2:
        return None  # singles are defined below
    return type(
        name,
        (MultiStickerItem,),
        {
            "NAME": "Stickers: " + ", ".join(s.name for s in sticker_list),
            "STICKERS": tuple(sticker_list),
        },
    )


# FACE_SWAP_<face> for every plain face. Combos are created lazily via __getattr__.
for face_name, face in _FACES.items():
    name = f"FACE_SWAP_{face_name}"
    globals()[name] = type(
        name,
        (FaceSwapItem,),
        {"NAME": f"New Face: {face.name}", "NEW_FACE": face, "STICKERS": ()},
    )

# STICKER_<name> for every sticker.
for sticker_name, sticker in vars(stickers).items():
    if isinstance(sticker, Sticker):
        name = f"STICKER_{sticker_name}"
        globals()[name] = type(
            name,
            (StickerItem,),
            {"NAME": f"Sticker: {sticker.name}", "STICKER": sticker},
        )


def __getattr__(name):
    """Lazy FACE_SWAP_<face>_<stickers> and STICKER_<a>_<b>_... item classes."""
    if name.startswith("FACE_SWAP_"):
        item = _face_swap_item(name)
        if item is not None:
            globals()[name] = item
            return item
    if name.startswith("STICKER_"):
        item = _sticker_stack_item(name)
        if item is not None:
            globals()[name] = item
            return item
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
