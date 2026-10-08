import random

# Party mana: after hero turns, while mana >= COST, spend COST to deal SPELL_DAMAGE.
MANA_SPELL_COST = 5
MANA_SPELL_DAMAGE = 8


class ManaPool:
    """Party mana for one fight. Heroes' mana faces fill it; unused mana carries between rounds."""

    def __init__(self):
        self.amount = 0

    def add(self, amount):
        self.amount += amount
        print(f"    Mana +{amount} (now {self.amount})")


def alive(characters):
    return [character for character in characters if character.is_alive()]


def deal_damage(attacker, target, amount, attacker_side):
    """Deal damage after weaken. If the target has thorns, the attacker takes it instead."""
    if attacker is not None:
        amount = attacker.outgoing_damage(amount)
    if amount <= 0:
        print(f"    {target.name} takes no damage")
        return

    if target.thorns and attacker is not None:
        print(f"    Thorns! {attacker.name} takes {amount} instead of {target.name}")
        blocked, hp_lost = attacker.take_damage(amount)
        if blocked:
            print(f"    {attacker.name}'s shield blocked {blocked}")
        print(f"    {attacker}")
        if not attacker.is_alive():
            defeat(attacker, attacker_side)
        return

    blocked, hp_lost = target.take_damage(amount)
    if blocked:
        print(f"    {target.name}'s shield blocked {blocked}")
    if hp_lost or not blocked:
        pass  # status printed by caller via character str


def sticker_damage(amount, stickers, user, target):
    """Apply stacked sticker multipliers to damage against one target. Returns final amount."""
    if amount <= 0 or not stickers:
        return amount
    total = float(amount)
    for sticker in stickers:
        mult = sticker.damage_multiplier(user, target)
        if mult != 1.0:
            total *= mult
            print(f"    {sticker.name}! (x{mult:g})")
    return int(total)


def apply_face(user, target, allies, foes, face, mana_pool=None, stickers=None):
    """Apply a rolled face. allies = user's side; foes = the other side."""
    stickers = stickers or []
    if face.damage:
        amount = sticker_damage(face.damage, stickers, user, target)
        deal_damage(user, target, amount, allies)
    if face.damage_all:
        for foe in list(alive(foes)):
            amount = sticker_damage(face.damage_all, stickers, user, foe)
            deal_damage(user, foe, amount, allies)
            if not foe.is_alive():
                defeat(foe, foes)
    if face.heal:
        user.heal(face.heal)
    if face.poison:
        target.add_poison(face.poison)
    if face.burn:
        target.add_burn(face.burn)
    if face.weaken:
        target.add_weaken(face.weaken)
    if face.group_heal:
        for ally in alive(allies):
            ally.heal(face.group_heal)
    if face.mana and mana_pool is not None:
        mana_pool.add(face.mana)
    if face.shield and alive(allies):
        ally = random.choice(alive(allies))
        ally.add_shield(face.shield)
        print(f"    {ally.name} gains {face.shield} shield")
    if face.stun and alive(foes):
        foe = random.choice(alive(foes))
        foe.stunned = True
        print(f"    {foe.name} is stunned!")
    if face.thorns and alive(allies):
        ally = random.choice(alive(allies))
        ally.thorns = True
        print(f"    {ally.name} gains thorns")


def take_turn(user, target, allies, foes, mana_pool=None):
    if user.stunned:
        print(f"  {user.name} is stunned and skips their roll!")
        user.stunned = False
        return

    roll = user.roll()
    user.current_slot = roll.slot
    face = roll.face
    for sticker in roll.stickers:
        face = sticker.prepare_face(user, roll, face)

    print(f"  {user.name} rolls {roll.name}"
          + (f" -> {face.name}" if face is not roll.face else ""))
    apply_face(user, target, allies, foes, face, mana_pool=mana_pool, stickers=roll.stickers)
    for sticker in roll.stickers:
        sticker.after_applied(user, roll, face)
    user.previous_slot = roll.slot

    print(f"    {user}  |  {target}")
    if face.group_heal:
        print(f"    Allies: {', '.join(str(ally) for ally in alive(allies))}")
    if face.damage_all and alive(foes):
        print(f"    Foes: {', '.join(str(foe) for foe in alive(foes))}")
    if not target.is_alive():
        defeat(target, foes)


def next_free_name(base_name, side):
    """'Slime' if no Slime is on this side yet, otherwise the next unused 'Slime N'."""
    same_kind = [character for character in side if character.NAME == base_name]
    if not same_kind:
        return base_name
    taken = {character.name for character in side}
    number = len(same_kind) + 1
    while f"{base_name} {number}" in taken:
        number += 1
    return f"{base_name} {number}"


def defeat(character, side):
    """Announce a death and add any SPAWN_ON_DEATH characters to the dead character's side."""
    if getattr(character, "_defeated", False):
        return
    character._defeated = True
    print(f"  {character.name} is defeated!")
    for spawn_class, count in character.SPAWN_ON_DEATH.items():
        for _ in range(count):
            spawn = spawn_class()
            spawn.name = next_free_name(spawn.NAME, side)
            side.append(spawn)
            print(f"  {spawn} appears!")


def cast_mana_spells(mana_pool, enemies):
    """Spend MANA_SPELL_COST mana for MANA_SPELL_DAMAGE as many times as mana allows."""
    cast_count = 0
    while mana_pool.amount >= MANA_SPELL_COST and alive(enemies):
        mana_pool.amount -= MANA_SPELL_COST
        cast_count += 1
        target = alive(enemies)[0]
        blocked, hp_lost = target.take_damage(MANA_SPELL_DAMAGE)
        print(f"  Autospell! -{MANA_SPELL_COST} mana "
              f"({mana_pool.amount} left) -> {MANA_SPELL_DAMAGE} damage to {target.name}")
        if blocked:
            print(f"    {target.name}'s shield blocked {blocked}")
        print(f"    {target}")
        if not target.is_alive():
            defeat(target, enemies)
    return cast_count


def poison_tick(side):
    poisoned = [character for character in alive(side) if character.poison]
    if poisoned:
        print("  -- Poison --")
    for character in poisoned:
        damage = character.tick_poison()
        print(f"  {character.name} takes {damage} poison damage: {character}")
        if not character.is_alive():
            defeat(character, side)


def burn_tick(side):
    burning = [character for character in alive(side) if character.burn]
    if burning:
        print("  -- Burn --")
    for character in burning:
        damage = character.tick_burn()
        print(f"  {character.name} takes {damage} burn damage: {character}")
        if not character.is_alive():
            defeat(character, side)


def clear_shields(side):
    for character in side:
        character.clear_round_shield()


def fight(party, enemies):
    """The party fights a group of enemies until one side is dead. Returns True if the party wins.

    Each round every living hero attacks the first living enemy,
    then mana spells cast if the party has enough mana,
    then every living enemy attacks a random living hero,
    then poison and burn tick, then shields expire.
    """
    mana_pool = ManaPool()
    for character in list(party) + list(enemies):
        character.begin_fight()
    print(f"\n=== {', '.join(str(hero) for hero in party)}")
    print(f"    vs {', '.join(str(enemy) for enemy in enemies)} ===")
    round_number = 1
    while alive(party) and alive(enemies):
        input(f"\nRound {round_number} - press Enter to roll...")
        for hero in alive(party):
            if not alive(enemies):
                break
            take_turn(hero, alive(enemies)[0], party, enemies, mana_pool=mana_pool)
        if alive(enemies) and alive(party):
            cast_mana_spells(mana_pool, enemies)
        if alive(enemies) and alive(party):
            print()
        for enemy in alive(enemies):
            if not alive(party):
                break
            take_turn(enemy, random.choice(alive(party)), enemies, party)
        poison_tick(party)
        poison_tick(enemies)
        burn_tick(party)
        burn_tick(enemies)
        clear_shields(party)
        clear_shields(enemies)
        print(f"  Mana: {mana_pool.amount}")
        round_number += 1

    if alive(party):
        print("\nVictory!")
        return True
    return False
