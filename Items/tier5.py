from Characters import faces
from Items import common
from Items.item import Item, MaxHpItem, PartyMaxHpItem, FaceSwapItem

# Add tier 5 items here (see tier1.py for examples).


ITEMS = [
    common.MAX_HP_ITEM_4,           # +3 max HP, one hero
    common.PARTY_MAX_HP_ITEM_3,     # +1 max HP, every hero
    #common.FACE_SWAP_DAMAGE_4,      # replace a face with Damage 4
    #common.FACE_SWAP_SHIELD_4,      # replace a face with Shield 4
    common.FACE_SWAP_HEAL_5,        # replace a face with Heal 5
    common.FACE_SWAP_DAMAGE_7_SINGLEUSE,  # Damage 5 + Single Use sticker
    common.FACE_SWAP_SHIELD_8_SINGLEUSE, 
    #common.DAMAGE_BOOST_2,
    #common.HEAL_BOOST_4,            # +1 to every heal / group-heal face
    #common.SHIELD_BOOST_3,          # +1 to every shield face
    common.STICKER_DEJA_VU,
]
