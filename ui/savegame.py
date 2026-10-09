"""Persist a mid-run checkpoint for the browser UI."""

from __future__ import annotations

import json
import os

from Characters.Heroes import HERO_TIERS
from Items import ITEM_TIERS

SAVE_VERSION = 1
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAVE_PATH = os.path.join(ROOT, "savegame.json")


class RunAborted(Exception):
    """Raised when the player quits back to the title screen."""


def has_save(path=SAVE_PATH):
    return os.path.isfile(path)


def clear_save(path=SAVE_PATH):
    try:
        os.remove(path)
    except FileNotFoundError:
        pass


def hero_class_by_name(name):
    for heroes in HERO_TIERS.values():
        for cls in heroes:
            if cls.NAME == name:
                return cls
    return None


def item_class_by_name(name, tier=None):
    if tier is not None:
        for cls in ITEM_TIERS.get(tier, []):
            if getattr(cls, "NAME", None) == name:
                return cls
    for pool in ITEM_TIERS.values():
        for cls in pool:
            if getattr(cls, "NAME", None) == name:
                return cls
    return None


def serialize_item(item):
    return {
        "name": item.NAME,
        "tier": item.tier,
        "face_slot": getattr(item, "slot", None),
    }


def serialize_hero(hero):
    return {
        "name": hero.NAME,
        "hp": hero.hitpoints,
        "max_hp": hero.max_hp,
        "base_max_hp": hero.base_max_hp,
        "next_fight_half_hp": bool(getattr(hero, "next_fight_half_hp", False)),
        "items": [serialize_item(item) for item in getattr(hero, "items", [])],
    }


def build_save(party, inventory, resume_fight, auto_play, phase, fight):
    return {
        "version": SAVE_VERSION,
        "resume_fight": resume_fight,
        "auto_play": bool(auto_play),
        "phase": phase,
        "fight": fight,
        "party": [serialize_hero(hero) for hero in party or []],
        "bag": [serialize_item(item) for item in (inventory.bag() if inventory else [])],
        "prestige": getattr(inventory, "prestige", 0) if inventory else 0,
    }


def write_save(data, path=SAVE_PATH):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
    os.replace(tmp, path)


def read_save(path=SAVE_PATH):
    if not has_save(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict) or data.get("version") != SAVE_VERSION:
        return None
    if not data.get("party"):
        return None
    return data
