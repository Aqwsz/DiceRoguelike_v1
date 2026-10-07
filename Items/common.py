from Characters import faces
from Characters.dice import Face
from Items.item import MaxHpItem, PartyMaxHpItem, FaceSwapItem

# Ready-made items, so tier files can just list them, e.g.
#   ITEMS = [common.MAX_HP_ITEM_2, common.FACE_SWAP_DAMAGE_3]

# MAX_HP_ITEM_1 ... : +N max HP for one hero (permanent).
MAX_HP_ITEM_LIMIT = 100
for amount in range(1, MAX_HP_ITEM_LIMIT + 1):
    name = f"MAX_HP_ITEM_{amount}"
    globals()[name] = type(name, (MaxHpItem,), {"NAME": f"Toughness +{amount}", "AMOUNT": amount})

# PARTY_MAX_HP_ITEM_1 ... : +N max HP for every hero (permanent).
PARTY_MAX_HP_ITEM_LIMIT = 100
for amount in range(1, PARTY_MAX_HP_ITEM_LIMIT + 1):
    name = f"PARTY_MAX_HP_ITEM_{amount}"
    globals()[name] = type(name, (PartyMaxHpItem,), {"NAME": f"Rations +{amount}", "AMOUNT": amount})

# FACE_SWAP_<face> for every face in faces.py, e.g. FACE_SWAP_DAMAGE_2, FACE_SWAP_POISON_1, FACE_SWAP_MISS.
for face_name, face in list(vars(faces).items()):
    if isinstance(face, Face):
        name = f"FACE_SWAP_{face_name}"
        globals()[name] = type(name, (FaceSwapItem,), {"NAME": f"New Face: {face.name}", "NEW_FACE": face})
