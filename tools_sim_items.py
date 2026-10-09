"""Headless full-run sim with heuristic item selection + in-fight combat stats.

Run: python3 tools_sim_items.py
Each run creates a new folder and canvas (previous sims are kept):
  Simulation_Results/<YYYYMMDD_HHMMSS>/sim_results.txt|.json|...
  ~/.cursor/projects/.../canvases/item-balance-<YYYYMMDD-HHMMSS>.canvas.tsx
  Simulation_Results/latest -> symlink to the newest run dir

Hero/enemy damage & healing are logged from real fights (not immortal dummies),
so poison/burn only count while foes are alive.
"""
import builtins
import json
import os
import random
import statistics
import time
import traceback
from collections import Counter, defaultdict
from datetime import datetime

builtins.input = lambda *a, **k: ""
builtins.print = lambda *a, **k: None

from Characters.Heroes import HERO_TIERS, HERO_TIER
from Characters.src.hero import Hero
from Characters.Enemies import ENEMY_TIERS
from Characters.src.character import Character
from Characters.src.combo import sides_from_faces
from Levels.fights import FIGHTS
import src.combat as combat
from src.inventory import Inventory

# Cap rounds so heal-stall fights cannot hang the sim.
MAX_ROUNDS = 80
SIM_ROOT = "Simulation_Results"
N = 250

# Set for each run by begin_run().
RUN_ID = None
OUT_DIR = None
PROGRESS = None
RESULTS_TXT = None
RESULTS_JSON = None
BASELINE_TXT = None


def canvases_dir():
    """Cursor canvases directory for this workspace."""
    projects = os.path.join(os.path.expanduser("~"), ".cursor", "projects")
    if os.path.isdir(projects):
        scored = []
        for name in os.listdir(projects):
            if "DiceRoguelike" not in name:
                continue
            canvases = os.path.join(projects, name, "canvases")
            if not os.path.isdir(canvases):
                continue
            count = sum(1 for f in os.listdir(canvases) if f.endswith(".canvas.tsx"))
            scored.append((count, canvases))
        if scored:
            scored.sort(reverse=True)
            return scored[0][1]
    slug = os.path.abspath(".").lstrip("/").replace("/", "-")
    return os.path.join(projects, slug, "canvases")


def canvas_report_path(run_id=None):
    """Unique canvas path for this sim run (does not overwrite prior reports)."""
    run_id = run_id or RUN_ID or datetime.now().strftime("%Y%m%d_%H%M%S")
    stamp = run_id.replace("_", "-")
    return os.path.join(canvases_dir(), f"item-balance-{stamp}.canvas.tsx")


def begin_run():
    """Create a fresh Simulation_Results/<timestamp>/ directory for this sim."""
    global RUN_ID, OUT_DIR, PROGRESS, RESULTS_TXT, RESULTS_JSON, BASELINE_TXT
    os.makedirs(SIM_ROOT, exist_ok=True)
    RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Avoid collisions if two runs start in the same second.
    out = os.path.join(SIM_ROOT, RUN_ID)
    suffix = 1
    while os.path.exists(out):
        out = os.path.join(SIM_ROOT, f"{RUN_ID}_{suffix}")
        suffix += 1
    if suffix > 1:
        RUN_ID = os.path.basename(out)
    OUT_DIR = out
    os.makedirs(OUT_DIR, exist_ok=True)
    PROGRESS = os.path.join(OUT_DIR, "sim_progress.txt")
    RESULTS_TXT = os.path.join(OUT_DIR, "sim_results.txt")
    RESULTS_JSON = os.path.join(OUT_DIR, "sim_results.json")
    BASELINE_TXT = os.path.join(OUT_DIR, "baseline.txt")
    latest = os.path.join(SIM_ROOT, "latest")
    try:
        if os.path.islink(latest) or os.path.exists(latest):
            os.remove(latest)
        os.symlink(RUN_ID, latest)
    except OSError:
        with open(os.path.join(SIM_ROOT, "latest.txt"), "w") as f:
            f.write(RUN_ID + "\n")
    return RUN_ID

ENEMY_TIER_OF = {
    cls: str(tier) for tier, classes in ENEMY_TIERS.items() for cls in classes
}


from Items import ITEM_TIERS
from Items.src.offer import ITEM_OPTIONS
from Items.src.item import (
    MaxHpItem,
    PartyMaxHpItem,
    FaceSwapItem,
    StickerItem,
    MultiStickerItem,
    DamageBoostItem,
    DamageAllBoostItem,
    HealBoostItem,
    HealAllBoostItem,
    ShieldBoostItem,
)
from src.hero_rankup import roll_rankup_offers
from Levels.events import is_boss_fight, EVENTS, EVENT_CHANCE
import main as main_mod
import Items.src.offer as offer_mod
import Levels.events as ev_mod


def log(msg):
    with open(PROGRESS, "a") as f:
        f.write(msg + "\n")


# ---------------------------------------------------------------------------
# In-fight combat ledger (damage/heal/shield logged during real sims)
# ---------------------------------------------------------------------------


class CombatLedger:
    """Accumulate per-class combat totals from hooked combat calls."""

    def __init__(self):
        self.stats = defaultdict(self._blank)
        self._actor = None
        self._fight_mana = defaultdict(int)
        self._installed = False
        self._orig = {}

    @staticmethod
    def _blank():
        return {
            "kind": "",
            "tier": "",
            "color": "",
            "hp": 0,
            "damage": 0,
            "direct": 0,
            "dot": 0,
            "healing": 0,
            "shield": 0,
            "mana": 0,
            "mana_spell": 0,
            "fights": 0,
            "turns": 0,
            "rounds_alive": 0,
        }

    def ensure(self, character):
        key = character.NAME
        row = self.stats[key]
        if not row["kind"]:
            cls = type(character)
            if isinstance(character, Hero):
                row["kind"] = "hero"
                row["tier"] = str(HERO_TIER.get(cls, "?"))
                row["color"] = getattr(cls, "COLOR", "")
            else:
                row["kind"] = "enemy"
                row["tier"] = ENEMY_TIER_OF.get(cls, "?")
            row["hp"] = cls.MAX_HP
        return row

    def note_roster(self, party, enemies):
        for character in party:
            self.ensure(character)["fights"] += 1
        for character in enemies:
            self.ensure(character)["fights"] += 1

    def note_round(self, party, enemies):
        for character in combat.alive(party) + combat.alive(enemies):
            self.ensure(character)["rounds_alive"] += 1

    def credit_damage(self, source, amount, *, dot=False):
        if source is None or amount <= 0:
            return
        row = self.ensure(source)
        row["damage"] += amount
        if dot:
            row["dot"] += amount
        else:
            row["direct"] += amount

    def credit_heal(self, source, amount):
        if source is None or amount <= 0:
            return
        self.ensure(source)["healing"] += amount

    def credit_shield(self, source, amount):
        if source is None or amount <= 0:
            return
        self.ensure(source)["shield"] += amount

    def credit_mana(self, source, amount):
        if source is None or amount <= 0:
            return
        key = source.NAME
        self.ensure(source)["mana"] += amount
        self._fight_mana[key] += amount

    def credit_mana_spell(self, amount):
        """Split autospell damage across heroes by mana contributed this fight."""
        if amount <= 0:
            return
        total = sum(self._fight_mana.values())
        if total <= 0:
            return
        for name, mana in self._fight_mana.items():
            share = amount * mana / total
            self.stats[name]["mana_spell"] += share
            self.stats[name]["damage"] += share
            self.stats[name]["direct"] += share

    def begin_fight(self):
        self._fight_mana = defaultdict(int)

    def install(self):
        if self._installed:
            return
        ledger = self

        self._orig["deal_damage"] = combat.deal_damage
        self._orig["take_turn"] = combat.take_turn
        self._orig["cast_mana_spells"] = combat.cast_mana_spells
        self._orig["mana_add"] = combat.ManaPool.add
        self._orig["heal"] = Character.heal
        self._orig["add_poison"] = Character.add_poison
        self._orig["add_burn"] = Character.add_burn
        self._orig["add_shield"] = Character.add_shield
        self._orig["tick_poison"] = Character.tick_poison
        self._orig["tick_burn"] = Character.tick_burn

        def deal_damage(attacker, target, amount, attacker_side):
            if attacker is not None:
                amount = attacker.outgoing_damage(amount)
            if amount <= 0:
                return
            if target.thorns and attacker is not None:
                blocked, hp_lost = attacker.take_damage(amount)
                if not attacker.is_alive():
                    combat.defeat(attacker, attacker_side)
                return
            blocked, hp_lost = target.take_damage(amount)
            # Count pressure that reached the target (HP + absorbed by shield).
            ledger.credit_damage(attacker, blocked + hp_lost, dot=False)

        def take_turn(user, target, allies, foes, mana_pool=None):
            ledger._actor = user
            ledger.ensure(user)["turns"] += 1
            try:
                return ledger._orig["take_turn"](user, target, allies, foes, mana_pool=mana_pool)
            finally:
                ledger._actor = None

        def cast_mana_spells(mana_pool, enemies):
            cast_count = 0
            while mana_pool.amount >= combat.MANA_SPELL_COST and combat.alive(enemies):
                mana_pool.amount -= combat.MANA_SPELL_COST
                cast_count += 1
                target = combat.alive(enemies)[0]
                blocked, hp_lost = target.take_damage(combat.MANA_SPELL_DAMAGE)
                ledger.credit_mana_spell(blocked + hp_lost)
                if not target.is_alive():
                    combat.defeat(target, enemies)
            return cast_count

        def mana_add(pool, amount):
            ledger.credit_mana(ledger._actor, amount)
            return ledger._orig["mana_add"](pool, amount)

        def heal(self, amount):
            before = self.hitpoints
            ledger._orig["heal"](self, amount)
            gained = self.hitpoints - before
            # Only count in-combat heals (actor set by take_turn).
            if ledger._actor is not None:
                ledger.credit_heal(ledger._actor, gained)

        def add_poison(self, amount):
            ledger._orig["add_poison"](self, amount)
            if ledger._actor is not None:
                self.poison_source = ledger._actor

        def add_burn(self, amount):
            ledger._orig["add_burn"](self, amount)
            if ledger._actor is not None:
                self.burn_source = ledger._actor

        def add_shield(self, amount):
            ledger._orig["add_shield"](self, amount)
            if ledger._actor is not None:
                ledger.credit_shield(ledger._actor, amount)

        def tick_poison(self):
            damage = self.poison
            source = getattr(self, "poison_source", None)
            result = ledger._orig["tick_poison"](self)
            # Credit pre-shield poison amount that was attempted; match take_damage result via HP.
            # tick_poison returns damage taken request; use that for DoT credit.
            ledger.credit_damage(source, result, dot=True)
            return result

        def tick_burn(self):
            source = getattr(self, "burn_source", None)
            result = ledger._orig["tick_burn"](self)
            ledger.credit_damage(source, result, dot=True)
            return result

        combat.deal_damage = deal_damage
        combat.take_turn = take_turn
        combat.cast_mana_spells = cast_mana_spells
        combat.ManaPool.add = mana_add
        Character.heal = heal
        Character.add_poison = add_poison
        Character.add_burn = add_burn
        Character.add_shield = add_shield
        Character.tick_poison = tick_poison
        Character.tick_burn = tick_burn
        self._installed = True

    def uninstall(self):
        if not self._installed:
            return
        combat.deal_damage = self._orig["deal_damage"]
        combat.take_turn = self._orig["take_turn"]
        combat.cast_mana_spells = self._orig["cast_mana_spells"]
        combat.ManaPool.add = self._orig["mana_add"]
        Character.heal = self._orig["heal"]
        Character.add_poison = self._orig["add_poison"]
        Character.add_burn = self._orig["add_burn"]
        Character.add_shield = self._orig["add_shield"]
        Character.tick_poison = self._orig["tick_poison"]
        Character.tick_burn = self._orig["tick_burn"]
        self._installed = False


LEDGER = CombatLedger()


def fight(party, enemies):
    LEDGER.begin_fight()
    LEDGER.note_roster(party, enemies)
    mana_pool = combat.ManaPool()
    for character in list(party) + list(enemies):
        character.begin_fight()
        character.poison_source = None
        character.burn_source = None
    round_number = 1
    while combat.alive(party) and combat.alive(enemies) and round_number <= MAX_ROUNDS:
        LEDGER.note_round(party, enemies)
        for hero in combat.alive(party):
            if not combat.alive(enemies):
                break
            combat.take_turn(hero, combat.alive(enemies)[0], party, enemies, mana_pool=mana_pool)
        if combat.alive(enemies) and combat.alive(party):
            combat.cast_mana_spells(mana_pool, enemies)
        for enemy in combat.alive(enemies):
            if not combat.alive(party):
                break
            combat.take_turn(
                enemy, random.choice(combat.alive(party)), enemies, party
            )
        combat.poison_tick(party)
        combat.poison_tick(enemies)
        combat.burn_tick(party)
        combat.burn_tick(enemies)
        combat.clear_shields(party)
        combat.clear_shields(enemies)
        round_number += 1
    return bool(combat.alive(party) and not combat.alive(enemies))


def score_sticker(s):
    return {"Execute": 10, "First Strike": 9, "Deja Vu": 7, "Single Use": 3}.get(s.name, 5)


def score_item(item):
    if isinstance(item, PartyMaxHpItem):
        return 12 * item.AMOUNT
    if isinstance(item, MaxHpItem):
        return 5 * item.AMOUNT
    if isinstance(item, DamageBoostItem):
        return 14 * item.AMOUNT
    if isinstance(item, DamageAllBoostItem):
        return 16 * item.AMOUNT
    if isinstance(item, ShieldBoostItem):
        return 8 * item.AMOUNT
    if isinstance(item, HealBoostItem):
        return 6 * item.AMOUNT
    if isinstance(item, HealAllBoostItem):
        return 9 * item.AMOUNT
    if isinstance(item, FaceSwapItem):
        f = item.NEW_FACE
        score = (
            f.damage * 3
            + f.damage_all * 4
            + f.heal * 1.5
            + f.group_heal * 2
            + f.shield * 2
            + f.mana * 1.5
            + f.poison * 2.5
            + f.burn * 2
        )
        for s in item.STICKERS or ():
            score += score_sticker(s)
        if any(s.name == "Single Use" for s in (item.STICKERS or ())):
            score *= 0.85
        return score
    if isinstance(item, StickerItem):
        return score_sticker(item.STICKER) + 4
    if isinstance(item, MultiStickerItem):
        return sum(score_sticker(s) for s in item.STICKERS) + 6
    return 3.0


def pick_hero(item, party):
    free = [h for h in party if h.has_free_item_slot()]
    cands = free or list(party)

    def hs(h):
        color = getattr(type(h), "COLOR", "")
        s = 20 if h.has_free_item_slot() else 0
        dmg = sum(f.damage + f.damage_all for f in h.die.faces)
        if isinstance(item, (DamageBoostItem, DamageAllBoostItem)) or (
            isinstance(item, FaceSwapItem) and item.NEW_FACE.damage + item.NEW_FACE.damage_all > 0
        ):
            s += {"Orange": 5, "Blue": 4, "Grey": 2, "Red": 1}.get(color, 0) + dmg * 0.3
        elif isinstance(item, (HealBoostItem, HealAllBoostItem)) or (
            isinstance(item, FaceSwapItem) and (item.NEW_FACE.heal or item.NEW_FACE.group_heal)
        ):
            s += {"Red": 5, "Blue": 3}.get(color, 1)
        elif isinstance(item, ShieldBoostItem) or (
            isinstance(item, FaceSwapItem) and item.NEW_FACE.shield
        ):
            s += {"Grey": 5}.get(color, 2)
        elif isinstance(item, (MaxHpItem, PartyMaxHpItem)):
            s -= h.max_hp
        else:
            s += dmg
        return s

    return max(cands, key=hs)


def pick_slot(item, hero):
    if isinstance(item, FaceSwapItem):
        taken = {
            it.slot
            for it in hero.items
            if isinstance(it, FaceSwapItem) and hasattr(it, "slot")
        }
        slots = [i for i in range(6) if i not in taken] or list(range(6))
        return max(
            slots,
            key=lambda i: 100
            if hero.die.faces[i].name == "Miss"
            else -(hero.die.faces[i].damage + hero.die.faces[i].heal + hero.die.faces[i].shield),
        )
    return max(
        range(6),
        key=lambda i: hero.die.faces[i].damage + hero.die.faces[i].damage_all,
    )


def auto_equip(item, party, inventory):
    hero = pick_hero(item, party)
    if not hero.has_free_item_slot():
        if not hero.items:
            return
        inventory.unequip(hero.items[0], party)
    if isinstance(item, FaceSwapItem):
        item.slot = pick_slot(item, hero)
        item.swap_into(hero)
        hero.items.append(item)
        item.holder = hero
    elif isinstance(item, StickerItem):
        item.slot = pick_slot(item, hero)
        hero.items.append(item)
        item.holder = hero
        hero.die.add_sticker(item.slot, item.STICKER)
    elif isinstance(item, MultiStickerItem):
        item.slot = pick_slot(item, hero)
        hero.items.append(item)
        item.holder = hero
        for s in item.STICKERS:
            hero.die.add_sticker(item.slot, s)
    else:
        item.equip(hero, party)


def take_item(party, tier, inventory):
    pool = ITEM_TIERS[tier]
    if not pool:
        return None
    offers = [c(tier) for c in random.sample(pool, min(ITEM_OPTIONS, len(pool)))]
    item = max(offers, key=score_item)
    inventory.add(item)
    auto_equip(item, party, inventory)
    return item.NAME


def rankup(party):
    offers = roll_rankup_offers(party)
    if not offers:
        return
    hero, nc = offers[0]
    nh = nc()
    b = hero.base_max_hp - hero.MAX_HP
    if b:
        nh.raise_base_max_hp(b)
    nh.items = hero.items
    for it in nh.items:
        it.holder = nh
        it.on_rankup(hero, nh)
    party[party.index(hero)] = nh


def do_event(party, inventory, plan, number):
    if is_boss_fight(plan) or not EVENTS:
        return
    if random.random() >= EVENT_CHANCE:
        return
    event = random.choice(EVENTS)()
    event.fight_number = number
    options = list(event.choices(party, inventory))
    frail = min(range(len(party)), key=lambda i: party[i].max_hp)
    saved_offer = offer_mod.offer_item
    saved_ev_offer = ev_mod.offer_item
    saved_ask = ev_mod.ask_choice
    auto = lambda p, t, inv: take_item(p, t, inv)
    offer_mod.offer_item = auto
    ev_mod.offer_item = auto
    ev_mod.ask_choice = lambda count: frail if count == len(party) else 0
    try:
        options[0][1](party, inventory)
    finally:
        offer_mod.offer_item = saved_offer
        ev_mod.offer_item = saved_ev_offer
        ev_mod.ask_choice = saved_ask


def run_one():
    inventory = Inventory()
    party = [c() for c in random.sample(HERO_TIERS[1], 3)]
    picked = []
    cleared = 0
    for number, plan in enumerate(FIGHTS, start=1):
        if not plan:
            continue
        if not fight(party, main_mod.summon_enemies(plan)):
            return cleared, False, picked
        cleared = number
        for h in party:
            h.full_heal()
        do_event(party, inventory, plan, number)
        if not any(FIGHTS[number:]):
            break
        if number % 2 == 1:
            name = take_item(party, main_mod.item_tier(number), inventory)
            if name:
                picked.append(name)
        else:
            rankup(party)
    return cleared, True, picked


def class_faces(cls):
    faces, _ = sides_from_faces(cls.FACES)
    return faces


def face_ev(faces):
    n = len(faces) or 1

    def avg(getter):
        return sum(getter(f) for f in faces) / n

    return {
        "dmg": avg(lambda f: f.damage),
        "dmg_all": avg(lambda f: f.damage_all),
        "heal": avg(lambda f: f.heal + f.group_heal),
        "poison": avg(lambda f: f.poison),
        "burn": avg(lambda f: f.burn),
        "shield": avg(lambda f: f.shield),
        "mana": avg(lambda f: f.mana),
        "instant": avg(lambda f: f.damage + f.damage_all),
    }


def collect_unit_stats(ledger):
    """Merge face EVs with combat totals logged during the item sims."""
    # Index class metadata for heroes/enemies that never appeared.
    catalog = {}
    for tier, classes in HERO_TIERS.items():
        for cls in classes:
            catalog[cls.NAME] = ("hero", str(tier), getattr(cls, "COLOR", ""), cls)
    for tier, classes in ENEMY_TIERS.items():
        for cls in classes:
            catalog[cls.NAME] = ("enemy", str(tier), "", cls)

    rows = []
    names = set(catalog) | set(ledger.stats)
    for name in names:
        kind, tier, color, cls = catalog.get(name, ("?", "?", "", None))
        logged = ledger.stats.get(name, CombatLedger._blank())
        if logged["kind"]:
            kind = logged["kind"]
            tier = logged["tier"] or tier
            color = logged["color"] or color
        hp = logged["hp"] or (cls.MAX_HP if cls else 0)
        ev = face_ev(class_faces(cls)) if cls else face_ev([])
        fights = logged["fights"]
        rounds = logged["rounds_alive"]
        damage = logged["damage"]
        healing = logged["healing"]
        rows.append(
            {
                "kind": kind,
                "tier": tier,
                "name": name,
                "hp": hp,
                "color": color,
                "ev_instant": round(ev["instant"], 3),
                "ev_heal": round(ev["heal"], 3),
                "ev_shield": round(ev["shield"], 3),
                "ev_poison": round(ev["poison"], 3),
                "ev_burn": round(ev["burn"], 3),
                "ev_mana": round(ev["mana"], 3),
                "fights": fights,
                "turns": logged["turns"],
                "rounds_alive": rounds,
                "damage": round(damage, 1),
                "direct": round(logged["direct"], 1),
                "dot": round(logged["dot"], 1),
                "healing": round(healing, 1),
                "shield": round(logged["shield"], 1),
                "mana": round(logged["mana"], 1),
                "mana_spell": round(logged["mana_spell"], 1),
                "dmg_per_fight": round(damage / fights, 2) if fights else 0.0,
                "heal_per_fight": round(healing / fights, 2) if fights else 0.0,
                "dps": round(damage / rounds, 3) if rounds else 0.0,
                "hps": round(healing / rounds, 3) if rounds else 0.0,
            }
        )
    return rows


def format_unit_section(units):
    heroes = sorted(
        [r for r in units if r["kind"] == "hero" and r["fights"] > 0],
        key=lambda r: (-r["dmg_per_fight"], r["name"]),
    )
    enemies = sorted(
        [r for r in units if r["kind"] == "enemy" and r["fights"] > 0],
        key=lambda r: (-r["dmg_per_fight"], r["name"]),
    )
    lines = [
        "",
        "HERO STATISTICS (logged from item sims — real fights)",
        "-----------------------------------------------------",
        "Totals across all fights where that class was in the party.",
        "damage = direct hits + attributed DoTs + share of mana autospells.",
        "DoTs only tick while the target lives (no immortal-dummy snowball).",
        "",
        f"{'Tier':<4} {'Name':<16} {'F':>4} {'Dmg':>8} {'Direct':>8} {'DoT':>7} "
        f"{'Heal':>8} {'Shld':>7} {'D/F':>6} {'H/F':>6} {'DPS':>6} {'HPS':>6}",
    ]
    for r in heroes:
        lines.append(
            f"{r['tier']:<4} {r['name']:<16} {r['fights']:>4} {r['damage']:>8.0f} "
            f"{r['direct']:>8.0f} {r['dot']:>7.0f} {r['healing']:>8.0f} {r['shield']:>7.0f} "
            f"{r['dmg_per_fight']:>6.1f} {r['heal_per_fight']:>6.1f} "
            f"{r['dps']:>6.2f} {r['hps']:>6.2f}"
        )
    lines += [
        "",
        "ENEMY STATISTICS (logged from same item sims)",
        "---------------------------------------------",
        f"{'Tier':<10} {'Name':<16} {'F':>4} {'Dmg':>8} {'Direct':>8} {'DoT':>7} "
        f"{'D/F':>6} {'DPS':>6}",
    ]
    for r in enemies:
        lines.append(
            f"{r['tier']:<10} {r['name']:<16} {r['fights']:>4} {r['damage']:>8.0f} "
            f"{r['direct']:>8.0f} {r['dot']:>7.0f} {r['dmg_per_fight']:>6.1f} {r['dps']:>6.2f}"
        )
    lines += ["", "HERO TIER AVERAGES (dmg/fight · heal/fight when present)", "-" * 56]
    by_tier = {}
    for r in heroes:
        by_tier.setdefault(r["tier"], []).append(r)
    for tier in sorted(by_tier, key=lambda t: (not t.isdigit(), t)):
        group = by_tier[tier]
        lines.append(
            f"  T{tier}: n={len(group)}  avg D/F={statistics.mean(x['dmg_per_fight'] for x in group):.1f}  "
            f"avg H/F={statistics.mean(x['heal_per_fight'] for x in group):.1f}  "
            f"avg DPS={statistics.mean(x['dps'] for x in group):.2f}"
        )
    return lines


def run_baseline(n=N):
    """No-items sequential runs for comparison (no combat ledger needed)."""
    reached = Counter()
    wins = 0
    for _ in range(n):
        party = [c() for c in random.sample(HERO_TIERS[1], 3)]
        cleared = 0
        for number, plan in enumerate(FIGHTS, start=1):
            if not plan:
                continue
            if not fight(party, main_mod.summon_enemies(plan)):
                break
            cleared = number
            for h in party:
                h.full_heal()
            if number % 2 == 0:
                rankup(party)
        reached[cleared] += 1
        wins += int(cleared >= 20)
    samples = sorted([k for k, v in reached.items() for _ in range(v)])
    text = (
        f"NO ITEMS n={n} wins={wins} ({100 * wins / n:.1f}%)\n"
        f"median={samples[len(samples) // 2]} mean={statistics.mean(samples):.2f}\n"
        f"P(>=10)={100 * sum(1 for x in samples if x >= 10) / n:.1f}%\n"
        f"{dict(sorted(reached.items()))}\n"
    )
    with open(BASELINE_TXT, "w") as f:
        f.write(text)
    return {
        "n": n,
        "wins": wins,
        "reached": dict(sorted(reached.items())),
        "median": samples[len(samples) // 2],
        "mean": statistics.mean(samples),
        "p10": 100 * sum(1 for x in samples if x >= 10) / n,
        "p20": 100 * wins / n,
    }


def build_report(n, wins, errors, reached, item_names, units, baseline, elapsed, err):
    samples = []
    for k, v in reached.items():
        samples.extend([k] * v)
    samples.sort()
    p = lambda th: 100 * sum(1 for x in samples if x >= th) / len(samples) if samples else 0.0

    lines = [
        "ITEM SELECTION BALANCE REPORT",
        "=============================",
        f"Source: tools_sim_items.py · n={n} · heuristic pick/equip/rankup · round cap {MAX_ROUNDS}",
        f"Outputs: {OUT_DIR}/",
        f"Elapsed: {elapsed:.1f}s ({elapsed / max(n, 1):.3f}s/game)",
        "",
        "HEADLINE",
        "--------",
        f"With items:  {wins} wins ({100 * wins / n:.1f}%)  "
        f"median depth {samples[len(samples) // 2] if samples else 0}   "
        f"mean {statistics.mean(samples) if samples else 0:.2f}",
        f"No items:     {baseline['wins']} wins ({baseline['p20']:.1f}%)  "
        f"median depth {baseline['median']}   mean {baseline['mean']:.2f}",
        f"Errors: {errors}",
        "",
        "MILESTONE SURVIVAL",
        "------------------",
        f"                 With items   No items",
        f"P(cleared ≥ 5)     {p(5):5.1f}%",
        f"P(cleared ≥10)     {p(10):5.1f}%      {baseline['p10']:5.1f}%",
        f"P(cleared ≥15)     {p(15):5.1f}%",
        f"P(cleared ≥20)     {p(20):5.1f}%      {baseline['p20']:5.1f}%",
        "",
        f"STOP DEPTH (with items): {dict(sorted(reached.items()))}",
        "",
        "TOP AUTO-PICKED ITEMS",
        "---------------------",
    ]
    for name, c in item_names.most_common(15):
        lines.append(f"  {c:4d} {name}")
    lines.extend(format_unit_section(units))
    if err:
        lines.append("")
        lines.append("ERRORS:")
        lines.extend(err)
    lines.append("")
    lines.append(f"Run id:   {RUN_ID}")
    lines.append(f"Canvas:   {canvas_report_path()}")
    lines.append(f"Raw JSON: {RESULTS_JSON} · Baseline: {BASELINE_TXT}")
    return "\n".join(lines) + "\n", {
        "run_id": RUN_ID,
        "n": n,
        "wins": wins,
        "errors": errors,
        "elapsed_s": round(elapsed, 3),
        "reached": dict(sorted(reached.items())),
        "top_items": item_names.most_common(25),
        "baseline": baseline,
        "units": units,
        "milestones": {f">={th}": round(p(th), 1) for th in (5, 10, 15, 20)},
        "median": samples[len(samples) // 2] if samples else 0,
        "mean": round(statistics.mean(samples), 2) if samples else 0.0,
    }


def _js(value):
    return json.dumps(value, ensure_ascii=False)


def write_canvas_report(payload):
    """Write a new Cursor canvas for this run (prior canvases are left alone)."""
    run_id = payload.get("run_id") or RUN_ID or "unknown"
    n = payload["n"]
    base = payload["baseline"]
    milestones = payload["milestones"]
    heroes = sorted(
        [u for u in payload["units"] if u["kind"] == "hero" and u.get("fights", 0) > 0],
        key=lambda r: (-r["dmg_per_fight"], r["name"]),
    )
    enemies = sorted(
        [u for u in payload["units"] if u["kind"] == "enemy" and u.get("fights", 0) > 0],
        key=lambda r: (-r["dmg_per_fight"], r["name"]),
    )[:12]
    top_items = payload["top_items"][:10]

    def reached_map(reached):
        m = {i: 0 for i in range(0, 21)}
        for k, v in reached.items():
            m[int(k)] = int(v)
        return m

    with_reached = reached_map(payload["reached"])
    none_reached = reached_map(base["reached"])

    # Tier averages
    by_tier = defaultdict(list)
    for h in heroes:
        by_tier[h["tier"]].append(h)
    tier_avg = []
    for tier in sorted(by_tier, key=lambda t: (not str(t).isdigit(), str(t))):
        g = by_tier[tier]
        tier_avg.append(
            {
                "tier": f"T{tier}",
                "dmgPF": round(statistics.mean(x["dmg_per_fight"] for x in g), 1),
                "healPF": round(statistics.mean(x["heal_per_fight"] for x in g), 1),
                "dps": round(statistics.mean(x["dps"] for x in g), 2),
            }
        )

    hero_js = [
        {
            "name": h["name"],
            "tier": str(h["tier"]),
            "fights": h["fights"],
            "dmgPF": round(h["dmg_per_fight"], 1),
            "healPF": round(h["heal_per_fight"], 1),
            "dps": round(h["dps"], 2),
            "hps": round(h["hps"], 2),
            "direct": round(h["direct"]),
            "dot": round(h["dot"]),
            "color": h.get("color") or "",
        }
        for h in heroes
    ]
    enemy_js = [
        {
            "name": e["name"],
            "tier": str(e["tier"]),
            "dmgPF": round(e["dmg_per_fight"], 1),
            "dps": round(e["dps"], 2),
        }
        for e in enemies
    ]

    path = canvas_report_path(run_id)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    src = f"""import {{
  BarChart,
  Callout,
  Divider,
  Grid,
  H1,
  H2,
  H3,
  LineChart,
  Pill,
  Row,
  Stack,
  Stat,
  Table,
  Text,
  useHostTheme,
}} from "cursor/canvas";

/** Auto-generated by tools_sim_items.py — run {run_id}. Do not edit by hand. */

const RUN_ID = {_js(run_id)};
const N = {n};

const WITH_ITEMS = {{
  wins: {payload["wins"]},
  median: {payload["median"]},
  mean: {payload["mean"]},
  p5: {milestones.get(">=5", 0)},
  p10: {milestones.get(">=10", 0)},
  p15: {milestones.get(">=15", 0)},
  p20: {milestones.get(">=20", 0)},
  reached: {_js(with_reached)} as Record<number, number>,
}};

const NO_ITEMS = {{
  wins: {base["wins"]},
  median: {base["median"]},
  mean: {base["mean"]},
  p10: {base["p10"]},
  p20: {base["p20"]},
  reached: {_js(none_reached)} as Record<number, number>,
}};

const TOP_ITEMS: Array<[string, number]> = {_js(top_items)};

type HeroRow = {{
  name: string;
  tier: string;
  fights: number;
  dmgPF: number;
  healPF: number;
  dps: number;
  hps: number;
  direct: number;
  dot: number;
  color: string;
}};

const HEROES: HeroRow[] = {_js(hero_js)};

const ENEMIES = {_js(enemy_js)};

const TIER_AVG = {_js(tier_avg)};

function survival(reached: Record<number, number>): number[] {{
  return Array.from({{ length: 20 }}, (_, i) => {{
    const fight = i + 1;
    let sum = 0;
    for (let f = fight; f <= 20; f++) sum += reached[f] ?? 0;
    return Math.round((1000 * sum) / N) / 10;
  }});
}}

function deathsAt(reached: Record<number, number>): number[] {{
  return Array.from({{ length: 20 }}, (_, i) => reached[i + 1] ?? 0);
}}

const fightCats = Array.from({{ length: 20 }}, (_, i) => String(i + 1));
const survWith = survival(WITH_ITEMS.reached);
const survNone = survival(NO_ITEMS.reached);
const deathsWith = deathsAt(WITH_ITEMS.reached);
const deathsNone = deathsAt(NO_ITEMS.reached);
const topDmg = HEROES.filter((h) => h.dmgPF > 0).slice(0, 12);
const topHeal = [...HEROES].sort((a, b) => b.healPF - a.healPF).slice(0, 8);

export default function ItemBalanceReport() {{
  const theme = useHostTheme();
  return (
    <Stack gap={{20}} style={{{{ padding: 20, maxWidth: 1100 }}}}>
      <Stack gap={{6}}>
        <H1>Item balance · {{RUN_ID}}</H1>
        <Text tone="secondary" size="small">
          Auto-generated by tools_sim_items.py · run {{RUN_ID}} · n={{N}} · fight-logged damage/heal
        </Text>
        <Row gap={{8}} wrap>
          <Pill active>
            With items: {{WITH_ITEMS.wins}} wins ({{WITH_ITEMS.p20}}%)
          </Pill>
          <Pill>No items: {{NO_ITEMS.wins}} wins</Pill>
        </Row>
      </Stack>

      <Grid columns={{4}} gap={{12}}>
        <Stat value={{`${{WITH_ITEMS.p20}}%`}} label={{`Clear rate · ${{WITH_ITEMS.wins}}/${{N}}`}} tone="success" />
        <Stat value={{String(WITH_ITEMS.median)}} label={{`Median depth · none ${{NO_ITEMS.median}}`}} />
        <Stat value={{WITH_ITEMS.mean.toFixed(2)}} label={{`Mean depth · none ${{NO_ITEMS.mean.toFixed(2)}}`}} />
        <Stat value={{`${{WITH_ITEMS.p10}}%`}} label={{`P(≥10) · none ${{NO_ITEMS.p10}}%`}} tone="info" />
      </Grid>

      <Callout tone="info" title="Combat logging">
        Damage and healing are summed from the item-selection campaign sims.
        Poison/burn credit the applier only while the target lives.
      </Callout>

      <Divider />

      <Stack gap={{8}}>
        <H2>Survival curve — P(cleared ≥ fight)</H2>
        <LineChart
          categories={{fightCats}}
          series={{[
            {{ name: "With items", data: survWith, tone: "success" }},
            {{ name: "No items", data: survNone, tone: "neutral" }},
          ]}}
          valueSuffix="%"
          height={{240}}
          fill
        />
      </Stack>

      <Stack gap={{8}}>
        <H2>Stop depth histogram</H2>
        <BarChart
          categories={{fightCats}}
          series={{[
            {{ name: "With items", data: deathsWith, tone: "success" }},
            {{ name: "No items", data: deathsNone, tone: "neutral" }},
          ]}}
          height={{220}}
          showValues={{false}}
        />
      </Stack>

      <Divider />

      <Stack gap={{8}}>
        <H2>Hero tier averages (per fight when present)</H2>
        <BarChart
          categories={{TIER_AVG.map((t) => t.tier)}}
          series={{[
            {{ name: "Avg damage / fight", data: TIER_AVG.map((t) => t.dmgPF), tone: "danger" }},
            {{ name: "Avg heal / fight", data: TIER_AVG.map((t) => t.healPF), tone: "success" }},
            {{ name: "Avg DPS", data: TIER_AVG.map((t) => t.dps), tone: "info" }},
          ]}}
          height={{220}}
        />
      </Stack>

      <Grid columns={{2}} gap={{16}}>
        <Stack gap={{8}}>
          <H3>Top damage / fight</H3>
          <BarChart
            categories={{topDmg.map((h) => h.name)}}
            series={{[{{ name: "Damage per fight", data: topDmg.map((h) => h.dmgPF), tone: "danger" }}]}}
            height={{280}}
            horizontal
          />
        </Stack>
        <Stack gap={{8}}>
          <H3>Top heal / fight</H3>
          <BarChart
            categories={{topHeal.map((h) => h.name)}}
            series={{[{{ name: "Heal per fight", data: topHeal.map((h) => h.healPF), tone: "success" }}]}}
            height={{280}}
            horizontal
          />
        </Stack>
      </Grid>

      <Stack gap={{8}}>
        <H2>All heroes — fight-logged stats</H2>
        <Table
          headers={{["Tier", "Hero", "Fights", "Dmg/F", "Heal/F", "DPS", "HPS", "Direct", "DoT"]}}
          columnAlign={{["left", "left", "right", "right", "right", "right", "right", "right", "right"]}}
          striped
          stickyHeader
          rows={{HEROES.map((h) => [
            `T${{h.tier}}`,
            h.name,
            h.fights,
            h.dmgPF.toFixed(1),
            h.healPF.toFixed(1),
            h.dps.toFixed(2),
            h.hps.toFixed(2),
            Math.round(h.direct),
            Math.round(h.dot),
          ])}}
        />
      </Stack>

      <Stack gap={{8}}>
        <H2>Top enemies — damage / fight</H2>
        <Table
          headers={{["Tier", "Enemy", "Dmg/F", "DPS"]}}
          columnAlign={{["left", "left", "right", "right"]}}
          striped
          rows={{ENEMIES.map((e) => [e.tier, e.name, e.dmgPF.toFixed(1), e.dps.toFixed(2)])}}
        />
      </Stack>

      <Divider />

      <Stack gap={{8}}>
        <H2>Top auto-picked items</H2>
        <Table
          headers={{["#", "Item", "Picks"]}}
          columnAlign={{["right", "left", "right"]}}
          striped
          rows={{TOP_ITEMS.map(([name, picks], i) => [String(i + 1), name, String(picks)])}}
        />
      </Stack>

      <Text tone="secondary" size="small" style={{{{ color: theme.text.tertiary }}}}>
        Regenerated from Simulation_Results/sim_results.json
      </Text>
    </Stack>
  );
}}
"""
    with open(path, "w") as f:
        f.write(src)
    return path


def write_all_reports(report_text, payload):
    """Write text, JSON, and a new Cursor canvas into this run's folder."""
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(RESULTS_TXT, "w") as f:
        f.write(report_text)
    with open(RESULTS_JSON, "w") as f:
        json.dump(payload, f, indent=2)
    canvas_path = write_canvas_report(payload)
    # Record which canvas belongs to this run.
    with open(os.path.join(OUT_DIR, "canvas_path.txt"), "w") as f:
        f.write(canvas_path + "\n")
    return canvas_path


def main():
    begin_run()
    open(PROGRESS, "w").write(f"start N={N} run_id={RUN_ID}\n")
    LEDGER.install()
    reached = Counter()
    wins = 0
    errors = 0
    err = []
    item_names = Counter()
    t0 = time.time()

    for i in range(N):
        try:
            cleared, won, picked = run_one()
            reached[cleared] += 1
            wins += int(won)
            item_names.update(picked)
        except Exception:
            errors += 1
            if len(err) < 5:
                err.append(traceback.format_exc())
        if (i + 1) % 25 == 0:
            log(f"i={i+1} wins={wins} errors={errors} elapsed={time.time()-t0:.1f}s")

    log("summarize units from fight log...")
    units = collect_unit_stats(LEDGER)
    log("baseline...")
    baseline = run_baseline(N)
    elapsed = time.time() - t0

    report, payload = build_report(
        N, wins, errors, reached, item_names, units, baseline, elapsed, err
    )
    log("writing canvas report...")
    canvas_path = write_all_reports(report, payload)
    LEDGER.uninstall()
    log(f"done run={RUN_ID} canvas={canvas_path}")
    builtins.print = __import__("builtins").print
    print(report)
    print(f"\nRun folder:    {os.path.abspath(OUT_DIR)}")
    print(f"Canvas report: {canvas_path}")


if __name__ == "__main__":
    main()

