"""UI game session: runs a full campaign and exposes structured state for the browser."""

from __future__ import annotations

import random
import threading
import time
from copy import deepcopy

import src.combat as combat
from Characters.Heroes import HERO_TIERS, HERO_TIER
from Characters.src.hero import MAX_ITEMS
from Characters.src.combo import as_side
from Items import ITEM_TIERS
from Items.src.item import FaceSwapItem, StickerItem, MultiStickerItem
from Items.src.offer import ITEM_OPTIONS
from Levels.events import EVENTS, EVENT_CHANCE, is_boss_fight
from Levels.fights import FIGHTS
from src.hero_rankup import roll_rankup_offers
from src.inventory import Inventory
import main as main_mod
from ui.savegame import (
    RunAborted,
    build_save,
    clear_save,
    has_save,
    hero_class_by_name,
    item_class_by_name,
    read_save,
    write_save,
)

MAX_ROUNDS = 80
# Default pause between combat actions (hero roll, enemy roll, DoT tick, etc.).
TURN_SECONDS = 1.0


def item_title(item):
    """Display name with tier prefix, e.g. [T2] Iron Charm."""
    return f"[T{item.tier}] {item.NAME}"


def item_view(item):
    needs_face = isinstance(item, (FaceSwapItem, StickerItem, MultiStickerItem))
    return {
        "id": getattr(item, "uid", id(item)),
        "name": item.NAME,
        "title": item_title(item),
        "tier": item.tier,
        "detail": item.describe(),
        "holder": item.holder.name if item.holder else None,
        "needs_face": needs_face,
        "face_slot": getattr(item, "slot", None),
    }


def _tag_item(item, counter):
    if not getattr(item, "uid", None):
        item.uid = counter[0]
        counter[0] += 1
    return item


def _face_views_from_entries(entries):
    """Class FACES → [{slot, name, detail}, ...] with full effect text."""
    views = []
    for i, entry in enumerate(entries):
        side = as_side(entry)
        views.append({"slot": i + 1, "name": side.name, "detail": side.describe()})
    return views


def _face_views_from_die(die):
    """Live die (incl. stickers) → face views for the UI inspector."""
    views = []
    for i in range(die.SIDES):
        face = die.faces[i]
        stickers = die.stickers[i]
        if stickers:
            labels = ", ".join(sticker.name for sticker in stickers)
            name = f"{face.name} [{labels}]"
            extras = "; ".join(sticker.describe() for sticker in stickers)
            detail = f"{face.describe()} + {extras}"
        else:
            name = face.name
            detail = face.describe()
        views.append({"slot": i + 1, "name": name, "detail": detail})
    return views


def hero_class_view(hero_class):
    return {
        "name": hero_class.NAME,
        "hp": hero_class.MAX_HP,
        "color": getattr(hero_class, "COLOR", ""),
        "tier": HERO_TIER.get(hero_class, 1),
        "faces": _face_views_from_entries(hero_class.FACES),
    }


def char_view(character):
    equipped = list(getattr(character, "items", []) or [])
    item_slots = []
    if hasattr(character, "items"):
        for i in range(MAX_ITEMS):
            item_slots.append(item_view(equipped[i]) if i < len(equipped) else None)
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
        "items": [item.NAME for item in equipped],
        "item_slots": item_slots,
        "max_item_slots": MAX_ITEMS if hasattr(character, "items") else 0,
        "slots": character.item_slots() if hasattr(character, "item_slots") else "",
        "faces": _face_views_from_die(character.die) if getattr(character, "die", None) else [],
    }


def party_view(party):
    return [char_view(hero) for hero in party]


class GameSession:
    """One playable run. Thread-safe snapshot + blocking choices for the HTTP layer."""

    def __init__(self):
        self._lock = threading.RLock()
        self._choice_ready = threading.Event()
        self._turn_ready = threading.Event()
        self._answer = None
        self._auto_play = True
        self._turn_deadline = None
        self._party = None
        self._inventory = None
        self._item_id_counter = [1]
        self._abort = threading.Event()
        self._resume_data = None
        self._fx_id = 0
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
            "awaiting_turn": False,
            "auto_play": True,
            "turn_seconds": TURN_SECONDS,
            "inventory": {"bag": [], "prestige": 0},
            "has_save": has_save(),
            "can_save": False,
            "fx": None,
        }
        self._thread = None

    # --- public API ---------------------------------------------------------

    def start(self, from_save=False):
        with self._lock:
            # Called from the game thread after win/loss — spawn a fresh run.
            on_game_thread = (
                self._thread is not None
                and self._thread is threading.current_thread()
            )
            if self._thread and self._thread.is_alive() and not on_game_thread:
                return deepcopy(self._state)
            self._abort.clear()
            self._resume_data = read_save() if from_save else None
            if from_save and not self._resume_data:
                self._reset_state()
                self._state["error"] = "No valid save to continue"
                return deepcopy(self._state)
            self._reset_state()
            if self._resume_data:
                self._auto_play = bool(self._resume_data.get("auto_play", True))
                self._state["auto_play"] = self._auto_play
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        return self.snapshot()

    def snapshot(self):
        with self._lock:
            self._state["has_save"] = has_save()
            self._state["can_save"] = self._can_save_locked()
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
        # Wait for the next prompt (equip hero, die face, event follow-up, …)
        # so the UI does not blank until a refresh/poll catches up.
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline:
            time.sleep(0.03)
            with self._lock:
                if self._state.get("choice") is not None:
                    break
                phase = self._state.get("phase")
                if phase in ("fight", "map", "win", "lose", "error") or self._state.get(
                    "awaiting_turn"
                ):
                    break
                if not (self._thread and self._thread.is_alive()):
                    break
        return self.snapshot()

    def advance(self):
        """Skip the current turn pause (Next turn button / auto timer)."""
        self._turn_ready.set()
        return self.snapshot()

    def set_auto_play(self, enabled: bool):
        with self._lock:
            self._auto_play = bool(enabled)
            self._state["auto_play"] = self._auto_play
            # If auto was just turned on and a pause is already overdue, wake now.
            if (
                enabled
                and self._state.get("awaiting_turn")
                and self._turn_deadline is not None
                and time.monotonic() >= self._turn_deadline
            ):
                self._turn_ready.set()
        return self.snapshot()

    def equip_from_bag(self, item_id, hero_index, face_slot=None):
        """Equip a bag item onto a party hero. face_slot is 0-based when needed."""
        with self._lock:
            if self._state.get("phase") == "fight":
                return {**self.snapshot(), "error": "Can't change gear mid-fight"}
            party = self._party
            inventory = self._inventory
            if not party or not inventory:
                return self.snapshot()
            item = self._find_item(item_id)
            if not item or item.holder is not None:
                return {**self.snapshot(), "error": "Item not in bag"}
            if not (0 <= hero_index < len(party)):
                return {**self.snapshot(), "error": "Invalid hero"}
            hero = party[hero_index]
            if not hero.has_free_item_slot():
                return {**self.snapshot(), "error": f"{hero.name} has no free item slot"}
            needs_face = isinstance(item, (FaceSwapItem, StickerItem, MultiStickerItem))
            if needs_face and face_slot is None:
                return {
                    **self.snapshot(),
                    "needs_face": True,
                    "item_id": item.uid,
                    "hero_index": hero_index,
                    "faces": _face_views_from_die(hero.die),
                }
            try:
                self._apply_equip(item, hero, party, face_slot)
            except Exception as exc:
                return {**self.snapshot(), "error": str(exc)}
            self._log(f"{hero.name} equips {item.NAME}", "good")
            self._publish_fighters()
            return self.snapshot()

    def unequip_to_bag(self, item_id):
        with self._lock:
            if self._state.get("phase") == "fight":
                return {**self.snapshot(), "error": "Can't change gear mid-fight"}
            party = self._party
            inventory = self._inventory
            if not party or not inventory:
                return self.snapshot()
            item = self._find_item(item_id)
            if not item or item.holder is None:
                return {**self.snapshot(), "error": "Item not equipped"}
            hero_name = item.holder.name
            inventory.unequip(item, party)
            self._log(f"{hero_name} unequips {item.NAME}")
            self._publish_fighters()
            return self.snapshot()

    def save_game(self):
        """Write a checkpoint. Mid-fight saves restart that fight on Continue."""
        with self._lock:
            if not self._can_save_locked():
                return {**self.snapshot(), "error": "Nothing to save yet"}
            data = build_save(
                self._party,
                self._inventory,
                resume_fight=self._resume_fight_number_locked(),
                auto_play=self._auto_play,
                phase=self._state.get("phase"),
                fight=self._state.get("fight") or 0,
            )
        try:
            write_save(data)
        except OSError as exc:
            return {**self.snapshot(), "error": f"Save failed: {exc}"}
        return {**self.snapshot(), "saved": True}

    def quit_to_title(self, save=False):
        """Stop the run and return to the title screen. Optionally save first."""
        err = None
        if save:
            result = self.save_game()
            if result.get("error"):
                err = result["error"]
                # Still allow quit without save if save failed? Prefer report error.
                return result
        self._abort.set()
        self._choice_ready.set()
        self._turn_ready.set()
        thread = self._thread
        if thread and thread.is_alive() and thread is not threading.current_thread():
            thread.join(timeout=2.0)
        with self._lock:
            self._reset_state()
            self._abort.clear()
            if err:
                self._state["error"] = err
        return self.snapshot()

    # --- internals ----------------------------------------------------------

    def _can_save_locked(self):
        phase = self._state.get("phase")
        return bool(
            self._party
            and phase not in (None, "boot", "win", "lose", "error")
        )

    def _resume_fight_number_locked(self):
        fight = int(self._state.get("fight") or 0)
        phase = self._state.get("phase")
        if phase == "fight" and fight >= 1:
            return fight
        if fight < 1:
            return 1
        return next(
            (i for i, plan in enumerate(FIGHTS[fight:], start=fight + 1) if plan),
            fight + 1,
        )

    def _reset_state(self):
        self._choice_ready.clear()
        self._turn_ready.clear()
        self._answer = None
        self._auto_play = True
        self._party = None
        self._inventory = None
        self._item_id_counter = [1]
        self._turn_deadline = None
        self._fx_id = 0
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
            "awaiting_turn": False,
            "auto_play": True,
            "turn_seconds": TURN_SECONDS,
            "inventory": {"bag": [], "prestige": 0},
            "has_save": has_save(),
            "can_save": False,
            "fx": None,
        }

    def _set(self, **kwargs):
        with self._lock:
            self._state.update(kwargs)

    def _log(self, text, kind="info"):
        with self._lock:
            self._state["log"] = (self._state["log"] + [{"text": text, "kind": kind}])[-40:]

    def _fighter_ref(self, character, party, enemies):
        """Map a character to {side, index, name} for UI animations."""
        for index, hero in enumerate(party):
            if hero is character:
                return {"side": "party", "index": index, "name": character.name}
        for index, foe in enumerate(enemies):
            if foe is character:
                return {"side": "enemy", "index": index, "name": character.name}
        return {"side": "party", "index": 0, "name": character.name}

    def _emit_fx(self, kind, actor, target=None, face="", slot=None, party=None, enemies=None):
        """Publish a one-shot combat visual for the browser (dice roll, attack line)."""
        self._fx_id += 1
        payload = {
            "id": self._fx_id,
            "kind": kind,
            "actor": self._fighter_ref(actor, party or [], enemies or []),
            "target": self._fighter_ref(target, party or [], enemies or []) if target else None,
            "face": face or "",
            "slot": slot,
        }
        self._set(fx=payload)

    def _ask(self, title, options, subtitle=""):
        """Block until the UI posts a choice index. options: list of {label, detail?}."""
        if self._abort.is_set():
            raise RunAborted()
        self._choice_ready.clear()
        self._answer = None
        self._set(
            phase="choice",
            title=title,
            subtitle=subtitle,
            choice={"title": title, "subtitle": subtitle, "options": options},
        )
        while not self._choice_ready.wait(timeout=0.2):
            if self._abort.is_set():
                raise RunAborted()
        if self._abort.is_set():
            raise RunAborted()
        with self._lock:
            answer = self._answer
            self._answer = None
        return answer

    def _inventory_view(self):
        inv = self._inventory
        if not inv:
            return {"bag": [], "prestige": 0}
        return {
            "prestige": inv.prestige,
            "bag": [item_view(item) for item in inv.bag()],
        }

    def _find_item(self, item_id):
        inv = self._inventory
        if not inv:
            return None
        for item in inv.items:
            if getattr(item, "uid", None) == item_id or id(item) == item_id:
                return item
        return None

    def _apply_equip(self, item, hero, party, face_slot=None):
        """Equip without CLI prompts. face_slot is 0-based for die items."""
        if isinstance(item, FaceSwapItem):
            if face_slot is None:
                raise ValueError("Pick a die face for this item")
            item.slot = int(face_slot)
            item.swap_into(hero)
            hero.items.append(item)
            item.holder = hero
        elif isinstance(item, StickerItem):
            if face_slot is None:
                raise ValueError("Pick a die face for this item")
            item.slot = int(face_slot)
            hero.items.append(item)
            item.holder = hero
            hero.die.add_sticker(item.slot, item.STICKER)
        elif isinstance(item, MultiStickerItem):
            if face_slot is None:
                raise ValueError("Pick a die face for this item")
            item.slot = int(face_slot)
            hero.items.append(item)
            item.holder = hero
            for sticker in item.STICKERS:
                hero.die.add_sticker(item.slot, sticker)
        else:
            item.equip(hero, party)

    def _publish_fighters(self, enemies=None, mana=None):
        """Refresh party/enemies/inventory in state (lock held or via _set)."""
        party = self._party or []
        payload = {
            "party": party_view(party),
            "inventory": self._inventory_view(),
        }
        if enemies is not None:
            payload["enemies"] = party_view(enemies)
        if mana is not None:
            payload["mana"] = mana
        self._set(**payload)

    def _sync_fighters(self, party, enemies=None, mana=None):
        """Refresh fighters. Pass mana to update it; omit mid-fight to keep the pool."""
        self._party = party
        payload = {
            "party": party_view(party),
            "enemies": party_view(enemies) if enemies is not None else [],
            "inventory": self._inventory_view(),
        }
        if mana is not None:
            payload["mana"] = mana
        elif enemies is None:
            # Out of combat (map / between fights) — no active pool.
            payload["mana"] = 0
        self._set(**payload)

    def _run(self):
        try:
            if self._resume_data:
                data = self._resume_data
                self._resume_data = None
                self._play_from_save(data)
            else:
                self._play()
        except RunAborted:
            with self._lock:
                if self._state.get("phase") != "boot":
                    self._reset_state()
        except Exception as exc:
            self._set(phase="error", title="Something broke", subtitle=str(exc), error=str(exc))

    def _make_item(self, data):
        cls = item_class_by_name(data.get("name"), data.get("tier"))
        if not cls:
            raise ValueError(f"Unknown item {data.get('name')!r}")
        item = cls(data.get("tier") or 1)
        _tag_item(item, self._item_id_counter)
        return item

    def _play_from_save(self, data):
        inventory = Inventory(prestige=int(data.get("prestige") or 0))
        self._inventory = inventory
        party = []
        for hdata in data["party"]:
            cls = hero_class_by_name(hdata.get("name"))
            if not cls:
                raise ValueError(f"Unknown hero {hdata.get('name')!r}")
            party.append(cls())
        self._party = party
        for hero, hdata in zip(party, data["party"]):
            for idata in hdata.get("items") or []:
                item = self._make_item(idata)
                inventory.add(item)
                face_slot = idata.get("face_slot")
                self._apply_equip(item, hero, party, face_slot)
            hero.base_max_hp = int(hdata.get("base_max_hp", hero.base_max_hp))
            hero.max_hp = int(hdata.get("max_hp", hero.max_hp))
            hero.hitpoints = max(1, min(int(hdata.get("hp", hero.hitpoints)), hero.max_hp))
            hero.next_fight_half_hp = bool(hdata.get("next_fight_half_hp"))
        for idata in data.get("bag") or []:
            item = self._make_item(idata)
            inventory.add(item)
        resume = max(1, int(data.get("resume_fight") or 1))
        self._sync_fighters(party)
        self._set(
            phase="map",
            title="Continue run",
            subtitle=f"Resuming at fight {resume}",
            fight=resume - 1,
        )
        self._run_fights(party, inventory, start_at=resume)

    def _play(self):
        inventory = Inventory(prestige=0)
        self._inventory = inventory
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
        self._party = party
        self._sync_fighters(party)
        self._set(phase="map", title="The road ahead", subtitle="Fight 1 of 20")
        self._run_fights(party, inventory, start_at=1)

    def _wait_end_choice(self):
        self._choice_ready.clear()
        self._answer = None
        while not self._choice_ready.wait(timeout=0.2):
            if self._abort.is_set():
                raise RunAborted()
        if self._abort.is_set():
            raise RunAborted()

    def _run_fights(self, party, inventory, start_at=1):
        for number, fight_plan in enumerate(FIGHTS, start=1):
            if self._abort.is_set():
                raise RunAborted()
            if not fight_plan or number < start_at:
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
                clear_save()
                self._wait_end_choice()
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
            next_number = next(
                (i for i, plan in enumerate(FIGHTS[number:], start=number + 1) if plan),
                number + 1,
            )
            self._ready_next_fight(party, next_number)

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
        clear_save()
        self._wait_end_choice()
        return self.start()

    def _wait_turn(self):
        """Pause after a combat beat so the UI can update. Auto: 1s, or Next turn.

        Uses short timed waits so enabling Auto mid-pause is noticed, and so
        Next /api/advance can always interrupt.
        """
        self._turn_ready.clear()
        deadline = time.monotonic() + TURN_SECONDS
        with self._lock:
            self._turn_deadline = deadline
            self._state.update(awaiting_turn=True, phase="fight")
        while True:
            if self._abort.is_set():
                with self._lock:
                    self._state["awaiting_turn"] = False
                    self._turn_deadline = None
                raise RunAborted()
            if self._turn_ready.wait(timeout=0.05):
                break
            with self._lock:
                auto = self._auto_play
            if auto and time.monotonic() >= deadline:
                break
        with self._lock:
            self._state["awaiting_turn"] = False
            self._turn_deadline = None
        self._turn_ready.clear()

    def _fight(self, party, enemies):
        mana_pool = combat.ManaPool()
        for character in list(party) + list(enemies):
            character.begin_fight()
        self._sync_fighters(party, enemies, mana_pool.amount)
        self._wait_turn()
        round_number = 1
        while combat.alive(party) and combat.alive(enemies) and round_number <= MAX_ROUNDS:
            self._log(f"— Round {round_number} —", "round")
            self._set(subtitle=f"Round {round_number}")
            self._wait_turn()
            for hero in combat.alive(party):
                if not combat.alive(enemies):
                    break
                self._take_turn(hero, combat.alive(enemies)[0], party, enemies, mana_pool)
                self._wait_turn()
            if combat.alive(enemies) and combat.alive(party):
                before = mana_pool.amount
                combat.cast_mana_spells(mana_pool, enemies)
                if mana_pool.amount < before:
                    self._log(f"Autospell! Mana now {mana_pool.amount}", "mana")
                    self._sync_fighters(party, enemies, mana_pool.amount)
                    self._wait_turn()
            for enemy in combat.alive(enemies):
                if not combat.alive(party):
                    break
                target = random.choice(combat.alive(party))
                self._take_turn(enemy, target, enemies, party, None)
                self._wait_turn()
            self._poison_tick_logged(party)
            self._poison_tick_logged(enemies)
            self._burn_tick_logged(party)
            self._burn_tick_logged(enemies)
            combat.clear_shields(party)
            combat.clear_shields(enemies)
            self._sync_fighters(party, enemies, mana_pool.amount)
            self._log("End of round — shields and weaken fade", "round")
            self._wait_turn()
            round_number += 1
        return bool(combat.alive(party) and not combat.alive(enemies))

    def _poison_tick_logged(self, side):
        for character in [c for c in combat.alive(side) if c.poison]:
            damage = character.tick_poison()
            self._log(f"  {character.name} takes {damage} poison damage", "poison")
            if not character.is_alive():
                combat.defeat(character, side)

    def _burn_tick_logged(self, side):
        for character in [c for c in combat.alive(side) if c.burn]:
            damage = character.tick_burn()
            self._log(f"  {character.name} takes {damage} burn damage", "burn")
            if not character.is_alive():
                combat.defeat(character, side)

    def _take_turn(self, user, target, allies, foes, mana_pool):
        party = allies if mana_pool is not None else foes
        enemies = foes if mana_pool is not None else allies

        if user.stunned:
            user.stunned = False
            self._log(f"{user.name} is stunned and skips!", "status")
            if mana_pool is not None:
                self._sync_fighters(party, enemies, mana_pool.amount)
            else:
                self._sync_fighters(party, enemies)
            self._emit_fx("stun", user, target, party=party, enemies=enemies)
            return

        before_foes = {
            id(f): (f.hitpoints, f.shield, f.poison, f.burn, f.weaken, f.stunned)
            for f in foes
        }
        before_allies = {
            id(a): (a.hitpoints, a.shield, a.thorns) for a in allies
        }
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

        detail = roll.name if face is roll.face else f"{roll.name} -> {face.name}"
        self._log(f"{user.name} rolls {detail}", "roll")
        # Side effects summary
        for foe in foes:
            prev = before_foes.get(id(foe))
            if not prev:
                continue
            prev_hp, prev_shield, prev_poison, prev_burn, prev_weaken, prev_stun = prev
            lost = prev_hp - foe.hitpoints
            if lost > 0:
                self._log(f"  {foe.name} takes {lost} damage", "damage")
            if foe.poison > prev_poison:
                self._log(f"  {foe.name} gains {foe.poison - prev_poison} poison", "status")
            if foe.burn > prev_burn:
                self._log(f"  {foe.name} gains {foe.burn - prev_burn} burn", "status")
            if foe.weaken > prev_weaken:
                self._log(f"  {foe.name} gains {foe.weaken - prev_weaken} weaken", "status")
            if foe.stunned and not prev_stun:
                self._log(f"  {foe.name} is stunned", "status")
        for ally in allies:
            prev = before_allies.get(id(ally))
            if not prev:
                continue
            prev_hp, prev_shield, prev_thorns = prev
            if ally.hitpoints > prev_hp:
                self._log(f"  {ally.name} heals {ally.hitpoints - prev_hp}", "heal")
            if ally.shield > prev_shield:
                self._log(f"  {ally.name} gains {ally.shield - prev_shield} shield", "status")
            if ally.thorns and not prev_thorns:
                self._log(f"  {ally.name} gains thorns", "status")

        if mana_pool is not None:
            self._sync_fighters(party, enemies, mana_pool.amount)
        else:
            self._sync_fighters(party, enemies)
        self._emit_fx(
            "roll",
            user,
            target,
            face=detail,
            slot=roll.slot,
            party=party,
            enemies=enemies,
        )

    def _offer_item(self, party, tier, inventory):
        pool = ITEM_TIERS.get(tier) or []
        if not pool:
            return
        offers = [cls(tier) for cls in random.sample(pool, min(ITEM_OPTIONS, len(pool)))]
        idx = self._ask(
            f"Choose a tier {tier} item",
            [{"label": item_title(item), "detail": item.describe()} for item in offers],
            subtitle="Equip it after you pick.",
        )
        item = offers[idx]
        _tag_item(item, self._item_id_counter)
        inventory.add(item)
        self._set(inventory=self._inventory_view())
        self._equip_item(item, party, inventory)

    def _equip_item(self, item, party, inventory):
        options = []
        for hero in party:
            free = "free slot" if hero.has_free_item_slot() else "full"
            options.append(
                {
                    "label": hero.name,
                    "detail": f"{hero.item_slots()} · {free}",
                    "heroes": [char_view(hero)],
                }
            )
        options.append(
            {
                "label": "Keep in bag",
                "detail": "Equip later from Inventory",
            }
        )
        idx = self._ask(f"Equip {item_title(item)}", options, subtitle=item.describe())
        if idx == len(party):
            self._set(inventory=self._inventory_view())
            return
        hero = party[idx]
        if not hero.has_free_item_slot():
            drop = self._ask(
                f"{hero.name} is full — unequip one",
                [{"label": item_title(it), "detail": it.describe()} for it in hero.items]
                + [{"label": "Cancel", "detail": "Leave in bag"}],
            )
            if drop == len(hero.items):
                self._set(inventory=self._inventory_view())
                return
            inventory.unequip(hero.items[drop], party)

        if isinstance(item, (FaceSwapItem, StickerItem, MultiStickerItem)):
            face_slot = self._pick_slot(hero, item, replace=isinstance(item, FaceSwapItem))
            self._apply_equip(item, hero, party, face_slot)
        else:
            self._apply_equip(item, hero, party)
        self._log(f"{hero.name} equips {item.NAME}", "good")
        self._sync_fighters(party)

    def _pick_slot(self, hero, item, replace):
        if replace and isinstance(item, FaceSwapItem):
            taken = {
                it.slot
                for it in hero.items
                if isinstance(it, FaceSwapItem)
                and it is not item
                and getattr(it, "slot", None) is not None
            }
            slots = [i for i in range(6) if i not in taken] or list(range(6))
        else:
            slots = list(range(6))
        face_views = {view["slot"] - 1: view for view in _face_views_from_die(hero.die)}
        idx = self._ask(
            f"Choose a die face on {hero.name}",
            [
                {
                    "label": f"Face {slot + 1}",
                    "detail": face_views.get(slot, {}).get("detail")
                    or hero.die.describe_slot(slot),
                }
                for slot in slots
            ],
            subtitle=item_title(item),
        )
        return slots[idx]

    def _ready_next_fight(self, party, next_number):
        """Pause so the player can open Inventory and equip before the next fight."""
        self._sync_fighters(party)
        bag_n = len(self._inventory.bag()) if self._inventory else 0
        detail = (
            f"{bag_n} item(s) in bag — open Inventory to equip"
            if bag_n
            else "Open Inventory anytime before you continue"
        )
        self._ask(
            f"Ready for fight {next_number}?",
            [{"label": f"Continue to fight {next_number}", "detail": detail}],
            subtitle="Equip gear from Inventory, then continue.",
        )

    def _offer_rankup(self, party):
        offers = roll_rankup_offers(party)
        if not offers:
            return
        options = []
        for hero, new_class in offers:
            face_views = _face_views_from_entries(new_class.FACES)
            options.append(
                {
                    "label": f"{hero.name} → {new_class.NAME}",
                    "detail": (
                        f"{getattr(type(hero), 'COLOR', '')} tier {HERO_TIER[type(hero)]} → "
                        f"tier {HERO_TIER[new_class]} · {new_class.MAX_HP} HP"
                    ),
                    "faces": face_views,
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
        # Nested ask_choice / choose_hero / offer_item / grant_and_equip — patch for UI.
        import src.menu as menu
        import Items.src.offer as offer_mod
        import Levels.events as ev_mod

        saved = menu.ask_choice
        saved_offer = offer_mod.offer_item
        saved_choose_hero = ev_mod.choose_hero
        saved_grant = ev_mod.grant_and_equip

        def ui_ask(count):
            return self._ask(
                "Choose",
                [{"label": f"Option {i + 1}", "detail": ""} for i in range(count)],
            )

        def ui_choose_hero(p, prompt):
            pick = self._ask(
                prompt,
                [{"label": hero.name, "detail": str(hero)} for hero in p],
            )
            return p[pick]

        def ui_offer(p, tier, inv):
            self._offer_item(p, tier, inv)

        def ui_grant(p, inv, item):
            _tag_item(item, self._item_id_counter)
            inv.add(item)
            self._set(inventory=self._inventory_view())
            self._equip_item(item, p, inv)

        menu.ask_choice = ui_ask
        offer_mod.offer_item = ui_offer
        ev_mod.ask_choice = ui_ask
        ev_mod.offer_item = ui_offer
        ev_mod.choose_hero = ui_choose_hero
        ev_mod.grant_and_equip = ui_grant
        try:
            options[idx][1](party, inventory)
        finally:
            menu.ask_choice = saved
            offer_mod.offer_item = saved_offer
            ev_mod.ask_choice = saved
            ev_mod.offer_item = saved_offer
            ev_mod.choose_hero = saved_choose_hero
            ev_mod.grant_and_equip = saved_grant
        self._sync_fighters(party)
        self._log(f"Event: {event.TITLE}", "event")
