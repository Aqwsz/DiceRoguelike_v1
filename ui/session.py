"""UI game session: runs a full campaign and exposes structured state for the browser."""

from __future__ import annotations

import random
import threading
import time
from copy import deepcopy

import combat
from Characters.Heroes import HERO_TIERS, HERO_TIER
from Characters.combo import as_side
from Items import ITEM_TIERS
from Items.item import FaceSwapItem, StickerItem, MultiStickerItem
from Items.offer import ITEM_OPTIONS
from Levels.events import EVENTS, EVENT_CHANCE, is_boss_fight
from Levels.fights import FIGHTS
from hero_rankup import roll_rankup_offers
from inventory import Inventory
import main as main_mod

MAX_ROUNDS = 80


def _face_names(entries):
    return [as_side(entry).name for entry in entries]


def hero_class_view(hero_class):
    return {
        "name": hero_class.NAME,
        "hp": hero_class.MAX_HP,
        "color": getattr(hero_class, "COLOR", ""),
        "tier": HERO_TIER.get(hero_class, 1),
        "faces": _face_names(hero_class.FACES),
    }


def char_view(character):
    return {
        "name": character.name,
        "class_name": character.NAME,
        "hp": character.hitpoints,
        "max_hp": character.max_hp,
        "shield": character.shield,
        "poison": character.poison,
        "burn": character.burn,
        "weaken": character.weaken,
        "stunned": character.stunned,
        "thorns": character.thorns,
        "alive": character.is_alive(),
        "color": getattr(type(character), "COLOR", ""),
        "tier": HERO_TIER.get(type(character), ""),
        "items": [item.NAME for item in getattr(character, "items", [])],
        "slots": character.item_slots() if hasattr(character, "item_slots") else "",
    }


def party_view(party):
    return [char_view(hero) for hero in party]


class GameSession:
    """One playable run. Thread-safe snapshot + blocking choices for the HTTP layer."""

    def __init__(self):
        self._lock = threading.Lock()
        self._choice_ready = threading.Event()
        self._answer = None
        self._state = {
            "phase": "boot",
            "title": "",
            "subtitle": "",
            "fight": 0,
            "party": [],
            "enemies": [],
            "mana": 0,
            "log": [],
            "choice": None,
            "result": None,
            "error": None,
        }
        self._thread = None

    # --- public API ---------------------------------------------------------

    def start(self):
        with self._lock:
            if self._thread and self._thread.is_alive():
                return self.snapshot()
            self._reset_state()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        return self.snapshot()

    def snapshot(self):
        with self._lock:
            return deepcopy(self._state)

    def choose(self, index: int):
        with self._lock:
            choice = self._state.get("choice")
            if not choice:
                return self.snapshot()
            if not (0 <= index < len(choice["options"])):
                return self.snapshot()
            self._answer = index
            self._state["choice"] = None
        self._choice_ready.set()
        # Brief yield so the game thread can advance before the next poll.
        time.sleep(0.05)
        return self.snapshot()

    # --- internals ----------------------------------------------------------

    def _reset_state(self):
        self._choice_ready.clear()
        self._answer = None
        self._state = {
            "phase": "boot",
            "title": "Dice Roguelike",
            "subtitle": "Rolling a new run…",
            "fight": 0,
            "party": [],
            "enemies": [],
            "mana": 0,
            "log": [],
            "choice": None,
            "result": None,
            "error": None,
        }

    def _set(self, **kwargs):
        with self._lock:
            self._state.update(kwargs)

    def _log(self, text, kind="info"):
        with self._lock:
            self._state["log"] = (self._state["log"] + [{"text": text, "kind": kind}])[-40:]

    def _ask(self, title, options, subtitle=""):
        """Block until the UI posts a choice index. options: list of {label, detail?}."""
        self._choice_ready.clear()
        self._answer = None
        self._set(
            phase="choice",
            title=title,
            subtitle=subtitle,
            choice={"title": title, "subtitle": subtitle, "options": options},
        )
        self._choice_ready.wait()
        with self._lock:
            answer = self._answer
            self._answer = None
        return answer

    def _sync_fighters(self, party, enemies=None, mana=0):
        self._set(
            party=party_view(party),
            enemies=party_view(enemies) if enemies is not None else [],
            mana=mana,
        )

    def _run(self):
        try:
            self._play()
        except Exception as exc:
            self._set(phase="error", title="Something broke", subtitle=str(exc), error=str(exc))

    def _play(self):
        inventory = Inventory(prestige=0)
        options = main_mod.roll_party_options(HERO_TIERS[1])
        choice = self._ask(
            "Choose your party",
            [
                {
                    "label": f"Party {i + 1}",
                    "detail": " · ".join(f"{c.NAME} ({c.MAX_HP} HP)" for c in party),
                    "heroes": [hero_class_view(c) for c in party],
                }
                for i, party in enumerate(options)
            ],
            subtitle="Three heroes. Twenty fights. One dice table.",
        )
        party = [hero_class() for hero_class in options[choice]]
        self._sync_fighters(party)
        self._set(phase="map", title="The road ahead", subtitle="Fight 1 of 20")

        for number, fight_plan in enumerate(FIGHTS, start=1):
            if not fight_plan:
                continue
            enemies = main_mod.summon_enemies(fight_plan)
            self._set(
                phase="fight",
                fight=number,
                title=f"Fight {number}",
                subtitle=", ".join(e.name for e in enemies),
                log=[],
            )
            self._sync_fighters(party, enemies)
            won = self._fight(party, enemies)
            if not won:
                self._sync_fighters(party, enemies)
                self._set(
                    phase="lose",
                    title="Your party has fallen",
                    subtitle=f"Cleared {number - 1} fights",
                    result="lose",
                    choice={
                        "title": "Defeat",
                        "subtitle": "The dice went cold.",
                        "options": [{"label": "New run", "detail": "Roll again"}],
                    },
                )
                self._choice_ready.clear()
                self._answer = None
                self._choice_ready.wait()
                return self.start()

            for hero in party:
                hero.full_heal()
            self._sync_fighters(party)
            self._log(f"Victory — party recovers.", "good")

            self._maybe_event(party, inventory, fight_plan, number)

            if not any(FIGHTS[number:]):
                break
            if number % 2 == 1:
                self._offer_item(party, main_mod.item_tier(number), inventory)
            else:
                self._offer_rankup(party)
            self._sync_fighters(party)

        self._set(
            phase="win",
            title="You win",
            subtitle="Every fight cleared.",
            result="win",
            party=party_view(party),
            enemies=[],
            choice={
                "title": "Victory",
                "subtitle": "The table is yours.",
                "options": [{"label": "New run", "detail": "Play again"}],
            },
        )
        self._choice_ready.clear()
        self._answer = None
        self._choice_ready.wait()
        return self.start()

    def _fight(self, party, enemies):
        mana_pool = combat.ManaPool()
        for character in list(party) + list(enemies):
            character.begin_fight()
        round_number = 1
        while combat.alive(party) and combat.alive(enemies) and round_number <= MAX_ROUNDS:
            self._log(f"— Round {round_number} —", "round")
            self._set(subtitle=f"Round {round_number}")
            for hero in combat.alive(party):
                if not combat.alive(enemies):
                    break
                self._take_turn(hero, combat.alive(enemies)[0], party, enemies, mana_pool)
            if combat.alive(enemies) and combat.alive(party):
                before = mana_pool.amount
                combat.cast_mana_spells(mana_pool, enemies)
                if mana_pool.amount < before:
                    self._log(f"Autospell! Mana now {mana_pool.amount}", "mana")
                    self._sync_fighters(party, enemies, mana_pool.amount)
                    time.sleep(0.25)
            for enemy in combat.alive(enemies):
                if not combat.alive(party):
                    break
                target = random.choice(combat.alive(party))
                self._take_turn(enemy, target, enemies, party, None)
            combat.poison_tick(party)
            combat.poison_tick(enemies)
            combat.burn_tick(party)
            combat.burn_tick(enemies)
            combat.clear_shields(party)
            combat.clear_shields(enemies)
            self._sync_fighters(party, enemies, mana_pool.amount)
            round_number += 1
            time.sleep(0.15)
        return bool(combat.alive(party) and not combat.alive(enemies))

    def _take_turn(self, user, target, allies, foes, mana_pool):
        if user.stunned:
            user.stunned = False
            self._log(f"{user.name} is stunned and skips!", "status")
            self._sync_fighters(
                allies if mana_pool is not None else foes,
                foes if mana_pool is not None else allies,
                mana_pool.amount if mana_pool else 0,
            )
            time.sleep(0.2)
            return

        before_foes = {id(f): (f.hitpoints, f.shield) for f in foes}
        before_allies = {id(a): a.hitpoints for a in allies}
        roll = user.roll()
        user.current_slot = roll.slot
        face = roll.face
        for sticker in roll.stickers:
            face = sticker.prepare_face(user, roll, face)
        combat.apply_face(user, target, allies, foes, face, mana_pool=mana_pool, stickers=roll.stickers)
        for sticker in roll.stickers:
            sticker.after_applied(user, roll, face)
        user.previous_slot = roll.slot
        if not target.is_alive():
            combat.defeat(target, foes)

        detail = roll.name if face is roll.face else f"{roll.name} → {face.name}"
        self._log(f"{user.name} rolls {detail}", "roll")
        # Side effects summary
        for foe in foes:
            prev = before_foes.get(id(foe))
            if prev and (foe.hitpoints, foe.shield) != prev:
                lost = prev[0] - foe.hitpoints
                if lost > 0:
                    self._log(f"  {foe.name} takes {lost} damage", "damage")
        for ally in allies:
            prev_hp = before_allies.get(id(ally))
            if prev_hp is not None and ally.hitpoints > prev_hp:
                self._log(f"  {ally.name} heals {ally.hitpoints - prev_hp}", "heal")

        party = allies if mana_pool is not None else foes
        enemies = foes if mana_pool is not None else allies
        self._sync_fighters(party, enemies, mana_pool.amount if mana_pool else 0)
        time.sleep(0.35)

    def _offer_item(self, party, tier, inventory):
        pool = ITEM_TIERS.get(tier) or []
        if not pool:
            return
        offers = [cls(tier) for cls in random.sample(pool, min(ITEM_OPTIONS, len(pool)))]
        idx = self._ask(
            f"Choose a tier {tier} item",
            [{"label": item.NAME, "detail": item.describe()} for item in offers],
            subtitle="Equip it after you pick.",
        )
        item = offers[idx]
        inventory.add(item)
        self._equip_item(item, party, inventory)

    def _equip_item(self, item, party, inventory):
        options = []
        for hero in party:
            options.append(
                {
                    "label": hero.name,
                    "detail": f"{hero} · {hero.item_slots()}",
                }
            )
        options.append({"label": "Keep in bag", "detail": "Equip later (bag only for now)"})
        idx = self._ask(f"Equip {item.NAME}", options, subtitle=item.describe())
        if idx == len(party):
            return
        hero = party[idx]
        if not hero.has_free_item_slot():
            drop = self._ask(
                f"{hero.name} is full — unequip one",
                [{"label": it.NAME, "detail": it.describe()} for it in hero.items]
                + [{"label": "Cancel", "detail": "Leave in bag"}],
            )
            if drop == len(hero.items):
                return
            inventory.unequip(hero.items[drop], party)

        if isinstance(item, FaceSwapItem):
            item.slot = self._pick_slot(hero, item, replace=True)
            item.swap_into(hero)
            hero.items.append(item)
            item.holder = hero
        elif isinstance(item, StickerItem):
            item.slot = self._pick_slot(hero, item, replace=False)
            hero.items.append(item)
            item.holder = hero
            hero.die.add_sticker(item.slot, item.STICKER)
        elif isinstance(item, MultiStickerItem):
            item.slot = self._pick_slot(hero, item, replace=False)
            hero.items.append(item)
            item.holder = hero
            for sticker in item.STICKERS:
                hero.die.add_sticker(item.slot, sticker)
        else:
            item.equip(hero, party)
        self._log(f"{hero.name} equips {item.NAME}", "good")
        self._sync_fighters(party)

    def _pick_slot(self, hero, item, replace):
        if replace and isinstance(item, FaceSwapItem):
            taken = {
                it.slot
                for it in hero.items
                if isinstance(it, FaceSwapItem) and hasattr(it, "slot")
            }
            slots = [i for i in range(6) if i not in taken] or list(range(6))
        else:
            slots = list(range(6))
        idx = self._ask(
            f"Choose a die face on {hero.name}",
            [
                {
                    "label": f"Face {slot + 1}",
                    "detail": hero.die.describe_slot(slot),
                }
                for slot in slots
            ],
            subtitle=item.NAME,
        )
        return slots[idx]

    def _offer_rankup(self, party):
        offers = roll_rankup_offers(party)
        if not offers:
            return
        options = []
        for hero, new_class in offers:
            options.append(
                {
                    "label": f"{hero.name} → {new_class.NAME}",
                    "detail": (
                        f"{getattr(type(hero), 'COLOR', '')} tier {HERO_TIER[type(hero)]} → "
                        f"tier {HERO_TIER[new_class]} · {new_class.MAX_HP} HP · "
                        + ", ".join(_face_names(new_class.FACES)[:3])
                        + "…"
                    ),
                    "heroes": [hero_class_view(new_class)],
                }
            )
        options.append({"label": "Skip", "detail": "Keep your current roster"})
        idx = self._ask("Hero rank-up", options, subtitle="Same-color promotion")
        if idx == len(offers):
            self._log("Rank-up skipped")
            return
        hero, new_class = offers[idx]
        new_hero = new_class()
        bonus = hero.base_max_hp - hero.MAX_HP
        if bonus:
            new_hero.raise_base_max_hp(bonus)
        new_hero.items = hero.items
        for item in new_hero.items:
            item.holder = new_hero
            item.on_rankup(hero, new_hero)
        party[party.index(hero)] = new_hero
        self._log(f"{hero.name} becomes {new_hero.name}!", "good")
        self._sync_fighters(party)

    def _maybe_event(self, party, inventory, fight_plan, number):
        if is_boss_fight(fight_plan) or not EVENTS:
            return
        if random.random() >= EVENT_CHANCE:
            return
        event = random.choice(EVENTS)()
        event.fight_number = number
        options = list(event.choices(party, inventory))
        labels = [{"label": label, "detail": event.TITLE} for label, _cb in options]
        labels.append({"label": "Decline", "detail": "Walk away"})
        idx = self._ask(event.TITLE, labels, subtitle="A roadside event")
        if idx == len(options):
            event.decline(party, inventory)
            self._log("Event declined")
            return
        # Nested ask_choice from events (choose_hero, offer_item) — patch briefly.
        import menu
        import Items.offer as offer_mod
        import Levels.events as ev_mod

        saved = menu.ask_choice
        saved_offer = offer_mod.offer_item

        def ui_ask(count):
            return self._ask(
                "Choose",
                [{"label": f"Option {i + 1}", "detail": ""} for i in range(count)],
            )

        def ui_offer(p, tier, inv):
            self._offer_item(p, tier, inv)

        menu.ask_choice = ui_ask
        offer_mod.offer_item = ui_offer
        ev_mod.ask_choice = ui_ask
        ev_mod.offer_item = ui_offer
        try:
            options[idx][1](party, inventory)
        finally:
            menu.ask_choice = saved
            offer_mod.offer_item = saved_offer
            ev_mod.ask_choice = saved
            ev_mod.offer_item = saved_offer
        self._sync_fighters(party)
        self._log(f"Event: {event.TITLE}", "event")
