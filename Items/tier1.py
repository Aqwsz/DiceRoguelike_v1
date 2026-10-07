from Characters import faces
from Items import common
from Items.item import Item, HeroItem, MaxHpItem, PartyMaxHpItem, FaceSwapItem

# Anything not in common.py: subclass HeroItem (pick a hero) or Item (whole party).
# class Example(HeroItem):
#     NAME = "Example"
#
#     def describe(self):
#         return "What the player sees in the menu"
#
#     def apply_to_hero(self, hero):
#         hero.die.faces = [faces.DAMAGE_1] * 6   # any code that changes the hero


ITEMS = [
    common.MAX_HP_ITEM_1,           # +1 max HP, one hero
    common.FACE_SWAP_DAMAGE_1,      # replace a face with Damage 1
    common.FACE_SWAP_HEAL_1,        # replace a face with Heal 1
]
