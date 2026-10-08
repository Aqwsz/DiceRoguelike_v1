import random

from menu import ask_choice
from Items import ITEM_TIERS
from Items.offer import offer_item

# Chance of an event after a won fight that is not a miniboss or final boss.
EVENT_CHANCE = 0.25
BOSS_TIERS = ("miniboss", "finalboss")


def choose_hero(party, prompt):
    print(f"\n{prompt}")
    for number, hero in enumerate(party, start=1):
        print(f"  {number}. {hero}")
    return party[ask_choice(len(party))]


def item_tier_for_fight(fight_number):
    """Same rule as main.item_tier: fights 1-2 -> tier 1, 3-4 -> tier 2, ..."""
    return min((fight_number + 1) // 2, max(ITEM_TIERS))


class Event:
    """Base class. Add a subclass below and put it in EVENTS.

    TITLE is shown to the player. choices() returns
    [(label, callback), ...] where callback(party, inventory) runs on pick.
    A decline option is added automatically. The choice labels are the description.
    """
    TITLE = "Unknown event"

    def __init__(self):
        self.fight_number = 1

    def choices(self, party, inventory):
        raise NotImplementedError

    def decline(self, party, inventory):
        print("You decline the event and move on.")


class GainAnItem(Event):
    TITLE = "Gain an Item"

    def choices(self, party, inventory):
        return [
            ("Take the item", self.gain_item),
        ]

    def gain_item(self, party, inventory):
        offer_item(party, item_tier_for_fight(self.fight_number), inventory)


class ShrineOfVigor(Event):
    TITLE = "Shrine of Vigor"

    def choices(self, party, inventory):
        return [
            ("Bless one hero (+1 max HP)", self.bless),
        ]

    def bless(self, party, inventory):
        hero = choose_hero(party, "Who receives the blessing?")
        hero.raise_base_max_hp(1)
        print(f"{hero.name} feels stronger: {hero}")


class BloodAltar(Event):
    TITLE = "Blood Altar"

    def choices(self, party, inventory):
        return [
            ("Accept the pact (+2 max HP to one hero, -2 max HP to another)", self.pact),
        ]

    def pact(self, party, inventory):
        blessed = choose_hero(party, "Who grows stronger?")
        others = [hero for hero in party if hero is not blessed]
        drained = random.choice(others) if others else blessed
        blessed.raise_base_max_hp(2)
        if drained is not blessed:
            drained.lower_base_max_hp(2)
        print(f"{blessed.name} is empowered: {blessed}")
        if drained is not blessed:
            print(f"{drained.name} is drained: {drained}")


class ForkedPath(Event):
    TITLE = "Forked Path"

    def choices(self, party, inventory):
        return [
            ("Take the hard road (+1 max HP to every hero)", self.train),
        ]

    def train(self, party, inventory):
        for hero in party:
            hero.raise_base_max_hp(1)
        print(f"The march toughens everyone: {', '.join(str(hero) for hero in party)}")


# Add new Event subclasses here.
EVENTS = [GainAnItem, ShrineOfVigor, BloodAltar, ForkedPath]


def is_boss_fight(fight_plan):
    return any(fight_plan.get(tier, 0) for tier in BOSS_TIERS)


def maybe_run_event(party, inventory, fight_plan, fight_number=1):
    """After a won non-boss fight, EVENT_CHANCE chance to run a random event from EVENTS."""
    if is_boss_fight(fight_plan) or not EVENTS:
        return
    if random.random() >= EVENT_CHANCE:
        return
    event = random.choice(EVENTS)()
    event.fight_number = fight_number
    print(f"\n***** {event.TITLE} *****")
    options = list(event.choices(party, inventory))
    options.append(("Decline", event.decline))
    for number, (label, _) in enumerate(options, start=1):
        print(f"  {number}. {label}")
    _, callback = options[ask_choice(len(options))]
    callback(party, inventory)
