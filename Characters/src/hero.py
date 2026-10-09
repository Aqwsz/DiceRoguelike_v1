from Characters.src.character import Character

MAX_ITEMS = 3


class Hero(Character):

    def __init__(self):
        super().__init__()
        self.items = []

    def has_free_item_slot(self):
        return len(self.items) < MAX_ITEMS

    def item_slots(self):
        return f"items {len(self.items)}/{MAX_ITEMS}"
