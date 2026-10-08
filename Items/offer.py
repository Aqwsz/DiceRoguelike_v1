import random

from Items import ITEM_TIERS
from menu import ask_choice

ITEM_OPTIONS = 2


def offer_item(party, tier, inventory):
    """Offer ITEM_OPTIONS different random items from this tier. The chosen one goes into the
    inventory and can be equipped right away; then the player can rearrange items."""
    pool = ITEM_TIERS[tier]
    if not pool:
        print(f"\n(No tier {tier} items yet.)")
        return

    offers = [item_class(tier) for item_class in random.sample(pool, min(ITEM_OPTIONS, len(pool)))]
    print(f"\nChoose a tier {tier} item:")
    for number, item in enumerate(offers, start=1):
        print(f"  {number}. {item.NAME} - {item.describe()}")
    item = offers[ask_choice(len(offers))]
    inventory.add(item)
    inventory.equip(item, party)
    inventory.manage(party)
