"""Combo stickers: extra rules stuck onto a die face (usually by items).

Add a new sticker by subclassing Sticker and exporting a constant here.
Items reference them via Items/common.py (STICKER_EXECUTE, ...).

Any number of stickers can stack on one face. Damage multipliers stack
(multiply). Stickers can also rewrite the rolled face (Single Use -> Miss)
or react after damage is dealt (Poison / Burn / Weaken / Life Drain).
"""

class Sticker:
    """One combo rule on a die face. Override the hooks you need."""
    NAME = "Unknown sticker"
    DESCRIPTION = ""

    @property
    def name(self):
        return self.NAME

    def describe(self):
        return self.DESCRIPTION or self.NAME

    def prepare_face(self, user, roll, face):
        """Optionally replace the face before it is applied (e.g. spent Single Use -> Miss).

        Return the face to use. Called in sticker order; later stickers see earlier changes.
        """
        return face

    def damage_multiplier(self, user, target):
        """Return a damage multiplier for this hit (1.0 = no change).

        Called separately for each foe when the face deals damage or damage_all.
        """
        return 1.0

    def after_damage(self, user, target, amount, face):
        """Called when this face deals damage to target (amount after multipliers).

        Not called if the hit was redirected by thorns or dealt 0.
        """
        pass

    def after_applied(self, user, roll, face_used):
        """Called once after the face (possibly rewritten) has been applied."""
        pass


class Execute(Sticker):
    NAME = "Execute"
    DESCRIPTION = "Double damage if the target is at half HP or below"

    def damage_multiplier(self, user, target):
        if target.max_hp > 0 and target.hitpoints <= target.max_hp / 2:
            return 2.0
        return 1.0


class FirstStrike(Sticker):
    NAME = "First Strike"
    DESCRIPTION = "Double damage if the target is at full HP"

    def damage_multiplier(self, user, target):
        if target.hitpoints >= target.max_hp:
            return 2.0
        return 1.0


class SingleUse(Sticker):
    NAME = "Single Use"
    DESCRIPTION = "This die side can only be used once per fight, then becomes a Miss"

    def prepare_face(self, user, roll, face):
        from Characters.faces import MISS
        spent = getattr(user, "single_use_spent", None)
        if spent is not None and roll.slot in spent:
            print(f"    Single Use spent -> Miss")
            return MISS
        return face

    def after_applied(self, user, roll, face_used):
        from Characters.faces import MISS
        # Mark spent after the first real use (not when already resolving as Miss).
        if face_used is MISS and roll.slot in getattr(user, "single_use_spent", set()):
            return
        if roll.slot not in user.single_use_spent:
            user.single_use_spent.add(roll.slot)
            print(f"    Single Use: face {roll.slot + 1} is spent for this fight")


class DejaVu(Sticker):
    NAME = "Deja Vu"
    DESCRIPTION = "Double damage if this die side matches the previous roll this fight"

    def damage_multiplier(self, user, target):
        prev = getattr(user, "previous_slot", None)
        curr = getattr(user, "current_slot", None)
        if prev is not None and curr is not None and prev == curr:
            return 2.0
        return 1.0


class Poison(Sticker):
    NAME = "Poison"
    DESCRIPTION = "Apply poison equal to damage dealt"

    def after_damage(self, user, target, amount, face):
        if amount > 0:
            target.add_poison(amount)
            print(f"    {target.name} gains {amount} poison")


class Burn(Sticker):
    NAME = "Burn"
    DESCRIPTION = "Apply burn equal to damage dealt"

    def after_damage(self, user, target, amount, face):
        if amount > 0:
            target.add_burn(amount)
            print(f"    {target.name} gains {amount} burn")


class Weaken(Sticker):
    NAME = "Weaken"
    DESCRIPTION = "Apply weaken equal to damage dealt (1 turn)"

    def after_damage(self, user, target, amount, face):
        if amount > 0:
            target.add_weaken(amount)
            print(f"    {target.name} gains {amount} weaken")


class LifeDrain(Sticker):
    NAME = "Life Drain"
    DESCRIPTION = "Heal self for damage dealt"

    def after_damage(self, user, target, amount, face):
        if amount > 0 and user is not None:
            user.heal(amount)
            print(f"    {user.name} drains {amount} HP")


# Named instances — items and die definitions reference these.
EXECUTE = Execute()
FIRST_STRIKE = FirstStrike()
SINGLE_USE = SingleUse()
DEJA_VU = DejaVu()
POISON = Poison()
BURN = Burn()
WEAKEN = Weaken()
LIFE_DRAIN = LifeDrain()
LIFEDRAIN = LIFE_DRAIN  # alias for DAMAGE_1_LIFEDRAIN recipes
