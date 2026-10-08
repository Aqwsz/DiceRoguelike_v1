import random

from Characters.Heroes import HERO_TIERS, HERO_TIER
from menu import ask_choice, describe_hero_class

RANKUP_OPTIONS = 2


def same_color_targets(hero, next_tier_heroes, party_classes):
    """Next-tier heroes of the same color that aren't already in the party."""
    color = type(hero).COLOR
    return [
        hero_class for hero_class in next_tier_heroes
        if hero_class.COLOR == color and hero_class not in party_classes
    ]


def roll_rankup_offers(party):
    """Return up to RANKUP_OPTIONS (hero, new hero class) offers.

    Each offer picks a random hero from the party's lowest tier and a random next-tier
    class of the same color that isn't already in the party. The same hero can appear
    in more than one offer, but never with the same rank-up twice.
    """
    lowest_tier = min(HERO_TIER[type(hero)] for hero in party)
    rankable = [hero for hero in party if HERO_TIER[type(hero)] == lowest_tier]
    party_classes = {type(hero) for hero in party}
    next_tier_heroes = HERO_TIERS.get(lowest_tier + 1, [])

    possible = []
    for hero in rankable:
        for target in same_color_targets(hero, next_tier_heroes, party_classes):
            possible.append((hero, target))

    if not possible:
        return []
    offer_count = min(RANKUP_OPTIONS, len(possible))
    return random.sample(possible, offer_count)


def offer_rankup(party):
    """Let the player pick one rank-up offer (or skip) and swap that hero in the party.

    The new hero keeps any permanent max HP bonus and its equipped items; face swap items
    are re-applied to the same spot on the new die.
    """
    offers = roll_rankup_offers(party)
    if not offers:
        return

    print("\nChoose a hero rank-up:")
    for number, (hero, new_class) in enumerate(offers, start=1):
        print(f"\n  {number}. {hero.name} [{type(hero).COLOR}] "
              f"(tier {HERO_TIER[type(hero)]}) -> "
              f"{new_class.NAME} [{new_class.COLOR}] (tier {HERO_TIER[new_class]})")
        describe_hero_class(new_class, indent="     ")
    print(f"\n  {len(offers) + 1}. Skip")

    choice = ask_choice(len(offers) + 1)
    if choice == len(offers):
        print("Rank-up skipped.")
        return
    hero, new_class = offers[choice]
    new_hero = new_class()
    bonus_hp = hero.base_max_hp - hero.MAX_HP
    if bonus_hp:
        new_hero.raise_base_max_hp(bonus_hp)
    new_hero.items = hero.items
    for item in new_hero.items:
        item.holder = new_hero
        item.on_rankup(hero, new_hero)
    party[party.index(hero)] = new_hero
    print(f"{hero.name} becomes {new_hero}!")
