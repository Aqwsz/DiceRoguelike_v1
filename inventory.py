from menu import ask_choice


class Inventory:
    """Every item obtained during one prestige, equipped on a hero or kept in the bag."""

    def __init__(self, prestige=0):
        self.prestige = prestige
        self.items = []

    def add(self, item):
        self.items.append(item)

    def bag(self):
        return [item for item in self.items if item.holder is None]

    def equipped(self):
        return [item for item in self.items if item.holder is not None]

    def show(self):
        print(f"\nInventory (prestige {self.prestige}):")
        if not self.items:
            print("  (empty)")
        for item in self.items:
            print(f"  - {item.summary()}")

    def show_equipment(self, party):
        print("\nYour items:")
        for hero in party:
            names = ", ".join(item.NAME for item in hero.items) or "none"
            print(f"  {hero.name} ({hero.item_slots()}): {names}")
        print(f"  Bag: {', '.join(item.NAME for item in self.bag()) or 'empty'}")

    def equip(self, item, party):
        """Ask which hero gets the item. A full hero must unequip one item first.
        Returns False if the player keeps the item in the bag instead."""
        while True:
            print(f"\nEquip {item.NAME} ({item.describe()}) on which hero?")
            for number, hero in enumerate(party, start=1):
                print(f"  {number}. {hero} - {hero.item_slots()}")
            print(f"  {len(party) + 1}. Keep it in the bag")
            choice = ask_choice(len(party) + 1)
            if choice == len(party):
                return False
            hero = party[choice]
            if hero.has_free_item_slot() or self.make_room(hero, party):
                item.equip(hero, party)
                print(f"{hero.name} equips {item.NAME}: {hero}")
                return True

    def make_room(self, hero, party):
        """Ask which of a full hero's items to unequip. Returns False if cancelled."""
        print(f"\n{hero.name} is full. Unequip which item?")
        for number, item in enumerate(hero.items, start=1):
            print(f"  {number}. {item.NAME} - {item.describe()}")
        print(f"  {len(hero.items) + 1}. Cancel")
        choice = ask_choice(len(hero.items) + 1)
        if choice == len(hero.items):
            return False
        self.unequip(hero.items[choice], party)
        return True

    def unequip(self, item, party):
        hero = item.holder
        item.unequip(party)
        print(f"{hero.name} unequips {item.NAME} (moved to the bag): {hero}")

    def pick(self, items, prompt):
        """Let the player pick one of items, or cancel (returns None)."""
        print(f"\n{prompt}")
        for number, item in enumerate(items, start=1):
            print(f"  {number}. {item.summary()}")
        print(f"  {len(items) + 1}. Cancel")
        choice = ask_choice(len(items) + 1)
        return None if choice == len(items) else items[choice]

    def manage(self, party):
        """Equip / unequip menu, repeated until the player is done."""
        while True:
            self.show_equipment(party)
            print("\n  1. Done\n  2. Equip an item from the bag\n  3. Unequip an item")
            choice = ask_choice(3)
            if choice == 0:
                return
            if choice == 1:
                if not self.bag():
                    print("The bag is empty.")
                    continue
                item = self.pick(self.bag(), "Equip which item?")
                if item:
                    self.equip(item, party)
            else:
                if not self.equipped():
                    print("No items are equipped.")
                    continue
                item = self.pick(self.equipped(), "Unequip which item?")
                if item:
                    self.unequip(item, party)
