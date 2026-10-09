from Characters import faces
from Items import common
from Items.src.item import Item, MaxHpItem, PartyMaxHpItem, FaceSwapItem, StickerItem

# Anything not in common.py: subclass Item and write what equipping and unequipping do.
# class Example(Item):
#     NAME = "Example"
#
#     def describe(self):
#         return "What the player sees in the menu"
#
#     def on_equip(self, hero, party):
#         hero.raise_base_max_hp(5)     # any code that changes the hero or party
#
#     def on_unequip(self, hero, party):
#         hero.lower_base_max_hp(5)     # must undo on_equip


ITEMS = [
    common.MAX_HP_ITEM_1,           # +1 max HP, one hero
    common.FACE_SWAP_DAMAGE_1,      # replace a face with Damage 1
    common.FACE_SWAP_SHIELD_1,      # replace a face with Shield 1
    common.FACE_SWAP_HEAL_1,        # replace a face with Heal 1
    common.FACE_SWAP_DAMAGE_2_SINGLEUSE,  # Damage 2 + Single Use sticker
    common.HEAL_BOOST_1,
    common.FACE_SWAP_MANA_1,
    
]
