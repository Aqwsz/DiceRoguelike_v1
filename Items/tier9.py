from Characters import faces
from Items import common
from Items.item import Item, MaxHpItem, PartyMaxHpItem, FaceSwapItem

# Add tier 9 items here (see tier1.py for examples).

ITEMS = [
    common.MAX_HP_ITEM_7,           # +3 max HP, one hero
    common.PARTY_MAX_HP_ITEM_6,     # +1 max HP, every hero
    common.FACE_SWAP_DAMAGE_7,      # replace a face with Damage 4
    common.FACE_SWAP_SHIELD_7,      # replace a face with Shield 4
    common.FACE_SWAP_HEAL_8,        # replace a face with Heal 5
    #common.FACE_SWAP_DAMAGE_6_EXECUTE,  # Damage 5 + Single Use sticker
    #common.FACE_SWAP_DAMAGE_5_FIRSTSTRIKE, 
    common.FACE_SWAP_SHIELD_12_SINGLEUSE,
    #common.FACE_SWAP_HEAL_10_SINGLEUSE
    common.DAMAGE_BOOST_5,
    common.HEAL_BOOST_7,            # +1 to every heal / group-heal face
    common.SHIELD_BOOST_6,          # +1 to every shield face

]
