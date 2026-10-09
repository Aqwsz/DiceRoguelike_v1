import random
from dataclasses import dataclass


@dataclass(frozen=True)
class Face:
    """One side of a die. Add new effect fields here as the game grows."""
    name: str
    damage: int = 0
    heal: int = 0
    poison: int = 0
    group_heal: int = 0
    mana: int = 0
    shield: int = 0
    stun: bool = False
    weaken: int = 0
    burn: int = 0
    thorns: bool = False
    damage_all: int = 0

    def describe(self):
        parts = []
        if self.damage:
            parts.append(f"{self.damage} damage")
        if self.damage_all:
            parts.append(f"{self.damage_all} damage to all foes")
        if self.heal:
            if self.damage or self.damage_all:
                parts.append(f"{self.heal} heal to self")
            else:
                parts.append(f"{self.heal} heal to lowest-HP ally")
        if self.poison:
            parts.append(f"{self.poison} poison")
        if self.burn:
            parts.append(f"{self.burn} burn")
        if self.group_heal:
            parts.append(f"{self.group_heal} heal to all allies")
        if self.mana:
            parts.append(f"+{self.mana} mana")
        if self.shield:
            parts.append(f"{self.shield} shield to a random ally")
        if self.stun:
            parts.append("stun a random foe")
        if self.weaken:
            parts.append(f"{self.weaken} weaken (1 turn)")
        if self.thorns:
            parts.append("thorns to a random ally")
        return f"{self.name} ({', '.join(parts) or 'no effect'})"


@dataclass
class Roll:
    """Result of rolling a die: the face plus any stickers on that slot."""
    face: Face
    stickers: list
    slot: int

    @property
    def name(self):
        if not self.stickers:
            return self.face.name
        labels = ", ".join(sticker.name for sticker in self.stickers)
        return f"{self.face.name} [{labels}]"


class Die:
    SIDES = 6

    def __init__(self, faces, stickers=None):
        if len(faces) != self.SIDES:
            raise ValueError(f"A die needs exactly {self.SIDES} faces, got {len(faces)}")
        self.faces = list(faces)
        # Stickers live on the die slot, not on the Face — face-swap keeps them.
        if stickers is None:
            self.stickers = [[] for _ in range(self.SIDES)]
        else:
            if len(stickers) != self.SIDES:
                raise ValueError(f"stickers must have {self.SIDES} lists, got {len(stickers)}")
            self.stickers = [list(slot) for slot in stickers]

    def roll(self):
        slot = random.randrange(self.SIDES)
        return Roll(self.faces[slot], list(self.stickers[slot]), slot)

    def add_sticker(self, slot, sticker):
        self.stickers[slot].append(sticker)

    def remove_sticker(self, slot, sticker):
        """Remove one matching sticker from the slot (by identity, then by name)."""
        for index, existing in enumerate(self.stickers[slot]):
            if existing is sticker or existing.name == sticker.name:
                self.stickers[slot].pop(index)
                return True
        return False

    def describe_slot(self, slot):
        face = self.faces[slot]
        stickers = self.stickers[slot]
        if not stickers:
            return face.name
        labels = ", ".join(sticker.name for sticker in stickers)
        return f"{face.name} [{labels}]"
