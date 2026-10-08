from dataclasses import replace

from menu import ask_choice


# Display names used when a boosted face still matches the simple "Label N" pattern.
_FACE_FIELD_LABELS = {
    "damage": "Damage",
    "damage_all": "Damage All",
    "heal": "Heal",
    "group_heal": "Group Heal",
    "shield": "Shield",
}


def adjust_face_field(face, field, delta):
    """Return a copy of face with field changed by delta, or None if that field is unused."""
    current = getattr(face, field, 0)
    if current <= 0:
        return None
    new_value = max(0, current + delta)
    name = face.name
    label = _FACE_FIELD_LABELS.get(field)
    if label and name == f"{label} {current}":
        name = f"{label} {new_value}"
    return replace(face, **{field: new_value}, name=name)


class Item:
    """Base class for all items. Every item is equipped on one hero (up to MAX_ITEMS per hero).

    Subclasses set NAME and override describe(), on_equip(hero, party) and
    on_unequip(hero, party). on_unequip must undo whatever on_equip did.
    For most items, subclass one of the ready-made types below instead.
    """
    NAME = "Unknown item"

    def __init__(self, tier):
        self.tier = tier
        self.holder = None

    def describe(self):
        return ""

    def on_equip(self, hero, party):
        pass

    def on_unequip(self, hero, party):
        pass

    def on_rankup(self, old_hero, new_hero):
        """The holder ranked up into new_hero. HP bonuses carry over on their own;
        override this for effects tied to the old hero (like its die)."""

    def equip(self, hero, party):
        hero.items.append(self)
        self.holder = hero
        self.on_equip(hero, party)

    def unequip(self, party):
        hero = self.holder
        self.on_unequip(hero, party)
        hero.items.remove(self)
        self.holder = None

    def summary(self):
        where = f"equipped by {self.holder.name}" if self.holder else "in bag"
        return f"{self.NAME} (tier {self.tier}) - {self.describe()} [{where}]"


class MaxHpItem(Item):
    """+AMOUNT max HP for the hero who equips it."""
    AMOUNT = 1

    def describe(self):
        return f"+{self.AMOUNT} max HP for the hero who equips it"

    def on_equip(self, hero, party):
        hero.raise_base_max_hp(self.AMOUNT)

    def on_unequip(self, hero, party):
        hero.lower_base_max_hp(self.AMOUNT)


class PartyMaxHpItem(Item):
    """+AMOUNT max HP for every hero while one hero has it equipped."""
    AMOUNT = 1

    def describe(self):
        return f"+{self.AMOUNT} max HP for every hero while equipped"

    def on_equip(self, hero, party):
        for ally in party:
            ally.raise_base_max_hp(self.AMOUNT)

    def on_unequip(self, hero, party):
        for ally in party:
            ally.lower_base_max_hp(self.AMOUNT)


class FaceSwapItem(Item):
    """Replace one face of the holder's die with NEW_FACE; unequipping puts the old face back.

    Optional STICKERS (tuple) are stuck onto that same slot. Unequip removes them.
    common.py builds these as FACE_SWAP_<FACE>_<STICKER>_..., e.g. FACE_SWAP_DAMAGE_3_SINGLEUSE.
    """
    NEW_FACE = None
    STICKERS = ()

    def describe(self):
        text = f"Replace one face on the holder's die with {self.NEW_FACE.name}"
        if self.STICKERS:
            labels = ", ".join(sticker.name for sticker in self.STICKERS)
            text += f" [{labels}]"
        return text

    def on_equip(self, hero, party):
        swapped = {item.slot for item in hero.items if isinstance(item, FaceSwapItem) and item is not self}
        slots = [slot for slot in range(len(hero.die.faces)) if slot not in swapped]
        print(f"\nChoose a face on {hero.name}'s die to replace:")
        for number, slot in enumerate(slots, start=1):
            print(f"  {number}. {hero.die.describe_slot(slot)}")
        self.slot = slots[ask_choice(len(slots))]
        self.swap_into(hero)

    def on_unequip(self, hero, party):
        for sticker in self.STICKERS:
            hero.die.remove_sticker(self.slot, sticker)
        hero.die.faces[self.slot] = self.old_face
        print(f"{hero.name}: {self.NEW_FACE.name} -> {self.old_face.name}")

    def on_rankup(self, old_hero, new_hero):
        self.swap_into(new_hero)

    def swap_into(self, hero):
        self.old_face = hero.die.faces[self.slot]
        hero.die.faces[self.slot] = self.NEW_FACE
        for sticker in self.STICKERS:
            hero.die.add_sticker(self.slot, sticker)
        print(f"{hero.name}: {self.old_face.name} -> {hero.die.describe_slot(self.slot)}")


class StickerItem(Item):
    """Add STICKER to one face of the holder's die; unequipping removes that sticker.

    Stickers stack: any number can sit on the same face (from different items).
    """
    STICKER = None

    def describe(self):
        return f"Add '{self.STICKER.name}' to one face ({self.STICKER.describe()})"

    def on_equip(self, hero, party):
        print(f"\nStick {self.STICKER.name} onto which face of {hero.name}'s die?")
        for number, slot in enumerate(range(len(hero.die.faces)), start=1):
            print(f"  {number}. {hero.die.describe_slot(slot)}")
        self.slot = ask_choice(len(hero.die.faces))
        hero.die.add_sticker(self.slot, self.STICKER)
        print(f"{hero.name}: {hero.die.describe_slot(self.slot)}")

    def on_unequip(self, hero, party):
        hero.die.remove_sticker(self.slot, self.STICKER)
        print(f"{hero.name}: removed {self.STICKER.name} -> {hero.die.describe_slot(self.slot)}")

    def on_rankup(self, old_hero, new_hero):
        # New die is blank; re-stick onto the same slot index.
        new_hero.die.add_sticker(self.slot, self.STICKER)


class MultiStickerItem(Item):
    """Add several stickers to one chosen face. Used by common.STICKER_A_B_... names."""
    STICKERS = ()

    def describe(self):
        labels = ", ".join(sticker.name for sticker in self.STICKERS)
        return f"Add [{labels}] to one face"

    def on_equip(self, hero, party):
        labels = ", ".join(sticker.name for sticker in self.STICKERS)
        print(f"\nStick {labels} onto which face of {hero.name}'s die?")
        for number, slot in enumerate(range(len(hero.die.faces)), start=1):
            print(f"  {number}. {hero.die.describe_slot(slot)}")
        self.slot = ask_choice(len(hero.die.faces))
        for sticker in self.STICKERS:
            hero.die.add_sticker(self.slot, sticker)
        print(f"{hero.name}: {hero.die.describe_slot(self.slot)}")

    def on_unequip(self, hero, party):
        for sticker in self.STICKERS:
            hero.die.remove_sticker(self.slot, sticker)
        print(f"{hero.name}: removed stickers -> {hero.die.describe_slot(self.slot)}")

    def on_rankup(self, old_hero, new_hero):
        for sticker in self.STICKERS:
            new_hero.die.add_sticker(self.slot, sticker)


class FaceBoostItem(Item):
    """+AMOUNT to FIELD on every face of the holder's die that already has that field.

    Subclasses set FIELD (and optionally EXTRA_FIELDS). Unequip subtracts the same
    amounts from the slots that were boosted. Rank-up re-applies onto the new die.
    """
    FIELD = "damage"
    EXTRA_FIELDS = ()
    AMOUNT = 1

    def fields(self):
        return (self.FIELD,) + tuple(self.EXTRA_FIELDS)

    def describe(self):
        labels = [_FACE_FIELD_LABELS.get(f, f) for f in self.fields()]
        what = " / ".join(labels)
        return f"+{self.AMOUNT} to every {what} face on the holder's die"

    def on_equip(self, hero, party):
        self._apply(hero)

    def on_unequip(self, hero, party):
        self._unapply(hero)

    def on_rankup(self, old_hero, new_hero):
        self._apply(new_hero)

    def _apply(self, hero):
        """Boost matching faces; remember (slot, field, amount) for a clean unequip."""
        self.changes = []
        for slot, face in enumerate(hero.die.faces):
            for field in self.fields():
                boosted = adjust_face_field(face, field, self.AMOUNT)
                if boosted is None:
                    continue
                hero.die.faces[slot] = boosted
                face = boosted
                self.changes.append((slot, field, self.AMOUNT))
        if self.changes:
            print(f"{hero.name}: {self.describe()}")
            print(f"  Die: {', '.join(hero.die.describe_slot(s) for s in range(len(hero.die.faces)))}")
        else:
            print(f"{hero.name} has no matching faces for {self.NAME}.")

    def _unapply(self, hero):
        for slot, field, amount in reversed(getattr(self, "changes", [])):
            face = hero.die.faces[slot]
            reduced = adjust_face_field(face, field, -amount)
            if reduced is not None:
                hero.die.faces[slot] = reduced
        if getattr(self, "changes", None):
            print(f"{hero.name}: removed {self.NAME}")
            print(f"  Die: {', '.join(hero.die.describe_slot(s) for s in range(len(hero.die.faces)))}")
        self.changes = []


class DamageBoostItem(FaceBoostItem):
    """+AMOUNT to damage and damage-all faces on the holder's die."""
    FIELD = "damage"
    EXTRA_FIELDS = ("damage_all",)


class HealBoostItem(FaceBoostItem):
    """+AMOUNT to heal and group-heal faces on the holder's die."""
    FIELD = "heal"
    EXTRA_FIELDS = ("group_heal",)


class ShieldBoostItem(FaceBoostItem):
    """+AMOUNT to shield faces on the holder's die."""
    FIELD = "shield"
    EXTRA_FIELDS = ()
