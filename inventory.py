class Inventory:
    """Every item obtained during one prestige."""

    def __init__(self, prestige=0):
        self.prestige = prestige
        self.items = []

    def add(self, item):
        self.items.append(item)

    def show(self):
        print(f"\nInventory (prestige {self.prestige}):")
        if not self.items:
            print("  (empty)")
        for item in self.items:
            print(f"  - {item.summary()}")
