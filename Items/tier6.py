from Characters import faces
from Items import common
from Items.src.item import Item, MaxHpItem, PartyMaxHpItem, FaceSwapItem

# Add tier 6 items here (see tier1.py for examples).



ITEMS = [
    common.MAX_HP_ITEM_5,           # +3 max HP, one hero
    common.PARTY_MAX_HP_ITEM_4,     # +1 max HP, every hero
    common.FACE_SWAP_DAMAGE_5,      # replace a face with Damage 4
    common.FACE_SWAP_DAMAGE_2_POISON,

    common.FACE_SWAP_SHIELD_5,      # replace a face with Shield 4

    common.FACE_SWAP_HEAL_6,        # replace a face with Heal 5
    #common.FACE_SWAP_DAMAGE_7_SINGLEUSE,  # Damage 5 + Single Use sticker
    #common.FACE_SWAP_SHIELD_8_SINGLEUSE, 
    common.DAMAGE_BOOST_3,
    common.HEAL_BOOST_5,            # +1 to every heal / group-heal face
    common.SHIELD_BOOST_4,          # +1 to every shield face
    common.MANA_BOOST_2,
   
]
