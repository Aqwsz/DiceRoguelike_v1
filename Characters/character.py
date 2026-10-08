from Characters.combo import sides_from_faces
from Characters.dice import Die

# How much poison wears off after each poison tick. 0 = poison lasts the whole fight.
POISON_DECAY = 0
# Burn always fades by 1 after each burn tick.
BURN_DECAY = 1


class Character:
    """Base class for heroes and enemies.

    Subclasses only need to set NAME, MAX_HP and FACES (6 Face or Side entries).
    FACES can mix plain faces and combos, e.g. faces.DAMAGE_10_EXECUTE.
    Optionally set SPAWN_ON_DEATH = {CharacterClass: count} to summon allies when this dies.
    """
    NAME = "Unknown"
    MAX_HP = 1
    FACES = []
    SPAWN_ON_DEATH = {}

    def __init__(self):
        self.name = self.NAME
        # base_max_hp is what full_heal restores to; permanent items should raise it.
        # max_hp is the current healing cap; temporary bonuses raise only this and
        # are removed by full_heal.
        self.base_max_hp = self.MAX_HP
        self.max_hp = self.MAX_HP
        self.hitpoints = self.MAX_HP
        self.poison = 0
        self.burn = 0
        self.shield = 0
        self.weaken = 0
        self.stunned = False
        self.thorns = False
        face_list, sticker_lists = sides_from_faces(self.FACES)
        self.die = Die(face_list, sticker_lists)
        # Fight-local roll state for stickers (Single Use, Deja Vu, ...).
        self.single_use_spent = set()
        self.previous_slot = None
        self.current_slot = None

    def begin_fight(self):
        """Reset per-fight sticker / roll tracking."""
        self.single_use_spent = set()
        self.previous_slot = None
        self.current_slot = None

    def is_alive(self):
        return self.hitpoints > 0

    def roll(self):
        """Roll the die. Returns a Roll (face + stickers on that slot)."""
        return self.die.roll()

    def take_damage(self, amount):
        """Apply damage after shield. Returns (blocked, hp_lost)."""
        blocked = 0
        if self.shield > 0 and amount > 0:
            blocked = min(self.shield, amount)
            self.shield -= blocked
            amount -= blocked
        self.hitpoints = max(0, self.hitpoints - amount)
        return blocked, amount

    def outgoing_damage(self, amount):
        """Damage this character deals after weaken."""
        return max(0, amount - self.weaken)

    def heal(self, amount):
        self.hitpoints = min(self.max_hp, self.hitpoints + amount)

    def add_poison(self, amount):
        self.poison += amount

    def add_burn(self, amount):
        self.burn += amount

    def add_weaken(self, amount):
        self.weaken += amount

    def add_shield(self, amount):
        self.shield += amount

    def tick_poison(self):
        """Take damage equal to current poison, then let it wear off. Returns the damage taken."""
        damage = self.poison
        self.take_damage(damage)
        self.poison = max(0, self.poison - POISON_DECAY)
        return damage

    def tick_burn(self):
        """Take damage equal to current burn, then fade by BURN_DECAY. Returns the damage taken."""
        damage = self.burn
        self.take_damage(damage)
        self.burn = max(0, self.burn - BURN_DECAY)
        return damage

    def clear_round_shield(self):
        self.shield = 0

    def raise_base_max_hp(self, amount):
        """Permanent max HP increase; also heals by the same amount."""
        self.base_max_hp += amount
        self.max_hp += amount
        self.hitpoints += amount

    def lower_base_max_hp(self, amount):
        """Undo raise_base_max_hp; current HP is capped at the new max (never below 1)."""
        self.base_max_hp -= amount
        self.max_hp -= amount
        self.hitpoints = max(1, min(self.hitpoints, self.max_hp))

    def full_heal(self):
        self.max_hp = self.base_max_hp
        self.hitpoints = self.base_max_hp
        self.poison = 0
        self.burn = 0
        self.shield = 0
        self.weaken = 0
        self.stunned = False
        self.thorns = False
        self.begin_fight()

    def __str__(self):
        parts = [f"{self.hitpoints}/{self.max_hp} HP"]
        if self.shield:
            parts.append(f"{self.shield} shield")
        if self.poison:
            parts.append(f"{self.poison} poison")
        if self.burn:
            parts.append(f"{self.burn} burn")
        if self.weaken:
            parts.append(f"{self.weaken} weaken")
        if self.thorns:
            parts.append("thorns")
        if self.stunned:
            parts.append("stunned")
        return f"{self.name} ({', '.join(parts)})"
