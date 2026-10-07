from Characters.dice import Die

# How much poison wears off after each poison tick. 0 = poison lasts the whole fight.
POISON_DECAY = 0


class Character:
    """Base class for heroes and enemies.

    Subclasses only need to set NAME, MAX_HP and FACES (a list of 6 Face objects).
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
        self.die = Die(self.FACES)

    def is_alive(self):
        return self.hitpoints > 0

    def roll(self):
        return self.die.roll()

    def take_damage(self, amount):
        self.hitpoints = max(0, self.hitpoints - amount)

    def heal(self, amount):
        self.hitpoints = min(self.max_hp, self.hitpoints + amount)

    def add_poison(self, amount):
        self.poison += amount

    def tick_poison(self):
        """Take damage equal to current poison, then let it wear off. Returns the damage taken."""
        damage = self.poison
        self.take_damage(damage)
        self.poison = max(0, self.poison - POISON_DECAY)
        return damage

    def raise_base_max_hp(self, amount):
        """Permanent max HP increase; also heals by the same amount."""
        self.base_max_hp += amount
        self.max_hp += amount
        self.hitpoints += amount

    def full_heal(self):
        self.max_hp = self.base_max_hp
        self.hitpoints = self.base_max_hp
        self.poison = 0

    def __str__(self):
        poison = f", {self.poison} poison" if self.poison else ""
        return f"{self.name} ({self.hitpoints}/{self.max_hp} HP{poison})"
