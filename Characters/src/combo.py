"""Slice & Dice-style side recipes: a base face plus any number of stickers.

Shared by faces.py (faces.DAMAGE_10_EXECUTE), Items/common.py
(FACE_SWAP_DAMAGE_10_EXECUTE), and Character starting dice.

Naming: BASE[_STICKER[_STICKER...]]
  DAMAGE_10
  DAMAGE_10_EXECUTE
  DAMAGE_10_SINGLEUSE_FIRSTSTRIKE
  HEAL_2_SINGLE_USE   (underscores in sticker names optional)
"""

from dataclasses import dataclass

from Characters.src.dice import Face


@dataclass(frozen=True)
class Side:
    """One die side: a face effect plus zero or more stickers."""
    face: Face
    stickers: tuple = ()

    @property
    def name(self):
        if not self.stickers:
            return self.face.name
        labels = ", ".join(sticker.name for sticker in self.stickers)
        return f"{self.face.name} [{labels}]"

    def describe(self):
        if not self.stickers:
            return self.face.describe()
        extras = "; ".join(sticker.describe() for sticker in self.stickers)
        return f"{self.face.describe()} + {extras}"


def face_table():
    """Name -> Face for every plain face currently defined in faces.py."""
    from Characters import faces
    return {name: value for name, value in vars(faces).items() if isinstance(value, Face)}


def sticker_aliases():
    """Sticker lookup including underscore-stripped aliases (SINGLEUSE == SINGLE_USE)."""
    from Characters import stickers
    from Characters.stickers import Sticker
    aliases = {}
    for name, value in vars(stickers).items():
        if isinstance(value, Sticker):
            aliases[name] = value
            aliases[name.replace("_", "")] = value
    return aliases


def match_sticker_suffixes(suffix, aliases=None):
    """Parse '_SINGLEUSE_EXECUTE' into a list of stickers. Empty -> []."""
    if not suffix:
        return []
    if not suffix.startswith("_"):
        raise ValueError(f"sticker suffix must start with '_', got {suffix!r}")
    aliases = aliases if aliases is not None else sticker_aliases()
    remaining = suffix[1:]
    matched = []
    keys = sorted(aliases, key=len, reverse=True)
    while remaining:
        found = None
        for key in keys:
            if remaining == key or remaining.startswith(key + "_"):
                found = key
                break
        if found is None:
            raise ValueError(f"unknown sticker in suffix {suffix!r} (at {remaining!r})")
        matched.append(aliases[found])
        remaining = remaining[len(found):]
        if remaining.startswith("_"):
            remaining = remaining[1:]
    return matched


def parse_side_name(name, faces_map=None, aliases=None):
    """Parse 'DAMAGE_10_EXECUTE' into a Side. Raises ValueError if unknown."""
    faces_map = faces_map if faces_map is not None else face_table()
    aliases = aliases if aliases is not None else sticker_aliases()
    face_key = None
    for key in sorted(faces_map, key=len, reverse=True):
        if name == key or name.startswith(key + "_"):
            face_key = key
            break
    if face_key is None:
        raise ValueError(f"unknown face recipe {name!r}")
    stickers = tuple(match_sticker_suffixes(name[len(face_key):], aliases))
    return Side(faces_map[face_key], stickers)


def as_side(entry):
    """Normalize a FACES entry (Face, Side, or recipe string) to a Side."""
    if isinstance(entry, Side):
        return entry
    if isinstance(entry, Face):
        return Side(entry, ())
    if isinstance(entry, str):
        return parse_side_name(entry)
    raise TypeError(f"die side must be Face, Side, or str, got {type(entry)!r}")


def sides_from_faces(entries):
    """Turn a FACES list into parallel (faces, stickers) lists for Die."""
    sides = [as_side(entry) for entry in entries]
    return [side.face for side in sides], [list(side.stickers) for side in sides]
