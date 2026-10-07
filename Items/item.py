from menu import ask_choice


class Item:
    """Base class for all items.

    Subclasses set NAME and override describe() and apply(party).
    For most items, subclass one of the ready-made types below instead.
    Each obtained item remembers the tier it came from and which hero got it.
    """
    NAME = "Unknown item"

    def __init__(self, tier):
        self.tier = tier
        self.holder = None

    def describe(self):
        return ""

    def apply(self, party):
        raise NotImplementedError

    def summary(self):
        holder = f", given to {self.holder}" if self.holder else ""
        return f"{self.NAME} (tier {self.tier}) - {self.describe()}{holder}"


class HeroItem(Item):
    """The player picks one hero, then apply_to_hero(hero) runs. Override apply_to_hero."""

    def apply(self, party):
        print("\nChoose a hero:")
        for number, hero in enumerate(party, start=1):
            print(f"  {number}. {hero}")
        hero = party[ask_choice(len(party))]
        self.holder = hero.name
        self.apply_to_hero(hero)

    def apply_to_hero(self, hero):
        raise NotImplementedError


class MaxHpItem(HeroItem):
    """Permanently raise one hero's max HP by AMOUNT."""
    AMOUNT = 1

    def describe(self):
        return f"+{self.AMOUNT} max HP for one hero (permanent)"

    def apply_to_hero(self, hero):
        hero.raise_base_max_hp(self.AMOUNT)
        print(f"{hero.name} now has {hero.base_max_hp} max HP.")


class PartyMaxHpItem(Item):
    """Permanently raise every hero's max HP by AMOUNT."""
    AMOUNT = 1

    def describe(self):
        return f"+{self.AMOUNT} max HP for every hero (permanent)"

    def apply(self, party):
        for hero in party:
            hero.raise_base_max_hp(self.AMOUNT)
        print(f"Party: {', '.join(str(hero) for hero in party)}")


class FaceSwapItem(HeroItem):
    """Replace one face of the chosen hero's die with NEW_FACE."""
    NEW_FACE = None

    def describe(self):
        return f"Replace one face on a hero's die with {self.NEW_FACE.describe()}"

    def apply_to_hero(self, hero):
        print(f"\nChoose a face on {hero.name}'s die to replace:")
        for number, face in enumerate(hero.die.faces, start=1):
            print(f"  {number}. {face.describe()}")
        slot = ask_choice(len(hero.die.faces))
        old_face = hero.die.faces[slot]
        hero.die.faces[slot] = self.NEW_FACE
        print(f"{hero.name}: {old_face.describe()} -> {self.NEW_FACE.describe()}")
