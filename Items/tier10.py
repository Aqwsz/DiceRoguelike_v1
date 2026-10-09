from Characters import faces
from Items import common
from Items.src.item import Item, MaxHpItem, PartyMaxHpItem, FaceSwapItem

# Add tier 10 items here (see tier1.py for examples).


ITEMS = [
    common.MAX_HP_ITEM_8,           # +3 max HP, one hero
    common.PARTY_MAX_HP_ITEM_7,     # +1 max HP, every hero
    common.FACE_SWAP_DAMAGE_8,      # replace a face with Damage 4
    common.FACE_SWAP_SHIELD_8,      # replace a face with Shield 4
    common.FACE_SWAP_HEAL_9,        # replace a face with Heal 5
    common.FACE_SWAP_DAMAGE_10_EXECUTE,  # Damage 5 + Single Use sticker
    common.FACE_SWAP_DAMAGE_6_FIRSTSTRIKE, 
    common.FACE_SWAP_DAMAGE_14_SINGLEUSE,
    common.FACE_SWAP_SHIELD_14_SINGLEUSE,
    common.FACE_SWAP_HEAL_15_SINGLEUSE,
    common.DAMAGE_BOOST_6,
    common.HEAL_BOOST_8,            # +1 to every heal / group-heal face
    common.SHIELD_BOOST_7,          # +1 to every shield face
    common.FACE_SWAP_MANA_5,
    

]