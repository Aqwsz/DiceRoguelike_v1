from Characters import faces
from Items import common
from Items.item import Item, MaxHpItem, PartyMaxHpItem, FaceSwapItem

# Add tier 3 items here (see tier1.py for examples).

ITEMS = [
    common.MAX_HP_ITEM_3,           # +3 max HP, one hero
    common.PARTY_MAX_HP_ITEM_2,     # +1 max HP, every hero
    common.FACE_SWAP_DAMAGE_3,      # replace a face with Damage 2
    common.FACE_SWAP_SHIELD_3,      # replace a face with Shield 2
    common.FACE_SWAP_HEAL_3,        # replace a face with Heal 2
    common.HEAL_BOOST_3,            # +1 to every heal / group-heal face
    common.SHIELD_BOOST_2,          # +1 to every shield face
    common.FACE_SWAP_DAMAGE_4_SINGLEUSE,  # Damage 3 + Single Use sticker
]

