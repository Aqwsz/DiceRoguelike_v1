from Characters import faces
from Items import common
from Items.item import Item, MaxHpItem, PartyMaxHpItem, FaceSwapItem, StickerItem

# Add tier 2 items here (see tier1.py for examples).


ITEMS = [
    common.MAX_HP_ITEM_2,           # +2 max HP, one hero
    common.PARTY_MAX_HP_ITEM_1,     # +1 max HP, every hero
    common.FACE_SWAP_DAMAGE_2,      # replace a face with Damage 2
    common.FACE_SWAP_SHIELD_2,      # replace a face with Shield 2
    common.FACE_SWAP_HEAL_2,        # replace a face with Heal 2
    common.DAMAGE_BOOST_1,
    common.HEAL_BOOST_2,            # +1 to every heal / group-heal face
    common.SHIELD_BOOST_1,          # +1 to every shield face
]
