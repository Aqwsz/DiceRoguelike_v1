from Characters import faces
from Items import common
from Items.src.item import Item, MaxHpItem, PartyMaxHpItem, FaceSwapItem

# Add tier 4 items here (see tier1.py for examples).


ITEMS = [
    #common.MAX_HP_ITEM_3,           # +3 max HP, one hero
    #common.PARTY_MAX_HP_ITEM_2,     # +1 max HP, every hero
    common.FACE_SWAP_DAMAGE_4,      # replace a face with Damage 4
    common.FACE_SWAP_SHIELD_4,      # replace a face with Shield 4
    common.FACE_SWAP_HEAL_4,        # replace a face with Heal 4
    common.DAMAGE_BOOST_2,
    common.HEAL_BOOST_4,            # +1 to every plain heal face
    common.SHIELD_BOOST_3,          # +1 to every shield face
    common.STICKER_EXECUTE,
    common.FACE_SWAP_DAMAGE_ALL_1,
]
