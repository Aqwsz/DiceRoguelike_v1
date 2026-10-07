import random

from Characters.Heroes import HERO_TIERS, HERO_TIER
from menu import ask_choice, describe_hero_class

UPGRADE_OPTIONS = 2


def roll_upgrade_offers(party):
    """Return up to UPGRADE_OPTIONS (hero, new hero class) offers.

    Each offer picks a random hero from the party's lowest tier and a random next-tier
    class that isn't already in the party. The same hero can appear in more than one
    offer, but never with the same upgrade twice.
    """
    lowest_tier = min(HERO_TIER[type(hero)] for hero in party)
    upgradable = [hero for hero in party if HERO_TIER[type(hero)] == lowest_tier]
    party_classes = {type(hero) for hero in party}
    targets = [hero_class for hero_class in HERO_TIERS.get(lowest_tier + 1, [])
               if hero_class not in party_classes]

    offer_count = min(UPGRADE_OPTIONS, len(upgradable) * len(targets))
    offers = []
    while len(offers) < offer_count:
        offer = (random.choice(upgradable), random.choice(targets))
        if offer not in offers:
            offers.append(offer)
    return offers


def offer_upgrade(party):
    """Let the player pick one upgrade offer (or skip) and swap that hero in the party."""
    offers = roll_upgrade_offers(party)
    if not offers:
        return

    print("\nChoose an upgrade:")
    for number, (hero, new_class) in enumerate(offers, start=1):
        print(f"\n  {number}. {hero.name} (tier {HERO_TIER[type(hero)]}) -> "
              f"{new_class.NAME} (tier {HERO_TIER[new_class]})")
        describe_hero_class(new_class, indent="     ")
    print(f"\n  {len(offers) + 1}. Skip")

    choice = ask_choice(len(offers) + 1)
    if choice == len(offers):
        print("Upgrade skipped.")
        return
    hero, new_class = offers[choice]
    party[party.index(hero)] = new_class()
    print(f"{hero.name} becomes {new_class.NAME}!")
