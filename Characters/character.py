from Characters.dice import Die


class Character:
    """Base class for heroes and enemies.

    Subclasses only need to set NAME, MAX_HP and FACES (a list of 6 Face objects).
    """
    NAME = "Unknown"
    MAX_HP = 1
    FACES = []

    def __init__(self):
        self.name = self.NAME
        # base_max_hp is what full_heal restores to; permanent upgrades should raise it.
        # max_hp is the current healing cap; temporary bonuses raise only this and
        # are removed by full_heal.
        self.base_max_hp = self.MAX_HP
        self.max_hp = self.MAX_HP
        self.hitpoints = self.MAX_HP
        self.die = Die(self.FACES)

    def is_alive(self):
        return self.hitpoints > 0

    def roll(self):
        return self.die.roll()

    def take_damage(self, amount):
        self.hitpoints = max(0, self.hitpoints - amount)

    def heal(self, amount):
        self.hitpoints = min(self.max_hp, self.hitpoints + amount)

    def full_heal(self):
        self.max_hp = self.base_max_hp
        self.hitpoints = self.base_max_hp

    def __str__(self):
        return f"{self.name} ({self.hitpoints}/{self.max_hp} HP)"
