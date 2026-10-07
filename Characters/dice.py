import random
from dataclasses import dataclass


@dataclass(frozen=True)
class Face:
    """One side of a die. Add new effect fields here (e.g. block) as the game grows."""
    name: str
    damage: int = 0
    heal: int = 0
    poison: int = 0
    group_heal: int = 0

    def describe(self):
        parts = []
        if self.damage:
            parts.append(f"{self.damage} damage")
        if self.heal:
            parts.append(f"{self.heal} heal")
        if self.poison:
            parts.append(f"{self.poison} poison")
        if self.group_heal:
            parts.append(f"{self.group_heal} heal to all allies")
        return f"{self.name} ({', '.join(parts) or 'no effect'})"


class Die:
    SIDES = 6

    def __init__(self, faces):
        if len(faces) != self.SIDES:
            raise ValueError(f"A die needs exactly {self.SIDES} faces, got {len(faces)}")
        self.faces = list(faces)

    def roll(self):
        return random.choice(self.faces)
