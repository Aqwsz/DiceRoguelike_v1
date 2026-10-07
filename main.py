import math
import random
from collections import Counter

from Characters.Heroes import HERO_TIERS
from Characters.Enemies import ENEMY_TIERS
from Levels.fights import FIGHTS
from combat import fight
from menu import ask_choice, describe_hero_class
from hero_rankup import offer_rankup
from Items import ITEM_TIERS
from Items.offer import offer_item
from inventory import Inventory

PARTY_SIZE = 3
PARTY_OPTIONS = 3
START_FIGHT = 0

def roll_party_options(heroes):
    """Return PARTY_OPTIONS parties of PARTY_SIZE different heroes each.

    Options are different parties from each other whenever the pool has enough heroes.
    """
    if len(heroes) < PARTY_SIZE:
        raise ValueError(f"Need at least {PARTY_SIZE} heroes to form a party, got {len(heroes)}")
    possible_parties = math.comb(len(heroes), PARTY_SIZE)
    options = []
    while len(options) < PARTY_OPTIONS:
        party = random.sample(heroes, PARTY_SIZE)
        is_new = set(party) not in [set(option) for option in options]
        if is_new or len(options) >= possible_parties:
            options.append(party)
    return options


def choose_party(options):
    print("Choose your party:")
    for number, party in enumerate(options, start=1):
        print(f"\n  Option {number}:")
        for hero_class in party:
            describe_hero_class(hero_class, indent="    ")

    return [hero_class() for hero_class in options[ask_choice(len(options))]]


def summon_enemies(fight_plan):
    enemies = []
    for tier, count in fight_plan.items():
        if tier not in ENEMY_TIERS:
            raise ValueError(f"Unknown enemy tier {tier!r}, expected one of {list(ENEMY_TIERS)}")
        pool = ENEMY_TIERS[tier]
        if count and not pool:
            raise ValueError(f"Fight wants {count} tier {tier} enemies, but tier {tier} has none")
        enemies += [random.choice(pool)() for _ in range(count)]

    # Number duplicates so "Slime 1" and "Slime 2" can be told apart in the log.
    totals = Counter(enemy.name for enemy in enemies)
    seen = Counter()
    for enemy in enemies:
        if totals[enemy.name] > 1:
            seen[enemy.name] += 1
            enemy.name = f"{enemy.name} {seen[enemy.name]}"
    return enemies


def item_tier(fight_number):
    """Fights 1-2 give tier 1, fights 3-4 give tier 2, ... capped at the highest tier."""
    return min((fight_number + 1) // 2, max(ITEM_TIERS))


def main():
    inventory = Inventory(prestige=0)
    party = choose_party(roll_party_options(HERO_TIERS[1]))
    for number, fight_plan in enumerate(FIGHTS, start=1):
        if not fight_plan or number < START_FIGHT:
            continue
        print(f"\n##### Fight {number} #####")
        if not fight(party, summon_enemies(fight_plan)):
            print("\nYour party has fallen. Game over.")
            inventory.show()
            return
        for hero in party:
            hero.full_heal()
        print(f"Your party rests and recovers: {', '.join(str(hero) for hero in party)}")
        if not any(FIGHTS[number:]):
            continue
        if number % 2 == 1:
            offer_item(party, item_tier(number), inventory)
        else:
            offer_rankup(party)
    print("\nYour party cleared every fight. You win!")
    inventory.show()


if __name__ == "__main__":
    main()
