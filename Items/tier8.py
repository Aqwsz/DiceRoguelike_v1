from Characters import faces
from Items import common
from Items.src.item import Item, MaxHpItem, PartyMaxHpItem, FaceSwapItem

# Add tier 8 items here (see tier1.py for examples).


ITEMS = [
    #common.MAX_HP_ITEM_6,           # +3 max HP, one hero
    #common.PARTY_MAX_HP_ITEM_5,     # +1 max HP, every hero
    #common.FACE_SWAP_DAMAGE_6,      # replace a face with Damage 4
    #common.FACE_SWAP_SHIELD_6,      # replace a face with Shield 4
    #common.FACE_SWAP_HEAL_7,        # replace a face with Heal 5
    common.FACE_SWAP_DAMAGE_6_EXECUTE,  # Damage 5 + Single Use sticker
    common.FACE_SWAP_DAMAGE_5_FIRSTSTRIKE, 
    common.FACE_SWAP_DAMAGE_3_BURN,
    common.FACE_SWAP_DAMAGE_1_EXECUTE_FIRSTSTRIKE_BURN_POISON,

    common.FACE_SWAP_SHIELD_5_DEJA_VU,

    common.FACE_SWAP_HEAL_10_SINGLEUSE,
    #common.DAMAGE_BOOST_4,
    #common.HEAL_BOOST_6,            # +1 to every heal / group-heal face
    #common.SHIELD_BOOST_5,          # +1 to every shield face
    common.STICKER_POISON,
]

