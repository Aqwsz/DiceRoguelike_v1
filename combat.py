import random


def apply_face(user, target, allies, face):
    """Apply a rolled face. Extend this when you add new effect types to Face.

    allies is the user's whole side (including the user).
    """
    if face.damage:
        target.take_damage(face.damage)
    if face.heal:
        user.heal(face.heal)
    if face.poison:
        target.add_poison(face.poison)
    if face.group_heal:
        for ally in alive(allies):
            ally.heal(face.group_heal)


def take_turn(user, target, allies, foes):
    face = user.roll()
    print(f"  {user.name} rolls {face.describe()}")
    apply_face(user, target, allies, face)
    print(f"    {user}  |  {target}")
    if face.group_heal:
        print(f"    Allies: {', '.join(str(ally) for ally in alive(allies))}")
    if not target.is_alive():
        defeat(target, foes)


def alive(characters):
    return [character for character in characters if character.is_alive()]


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
    print(f"  {character.name} is defeated!")
    for spawn_class, count in character.SPAWN_ON_DEATH.items():
        for _ in range(count):
            spawn = spawn_class()
            spawn.name = next_free_name(spawn.NAME, side)
            side.append(spawn)
            print(f"  {spawn} appears!")


def poison_tick(side):
    poisoned = [character for character in alive(side) if character.poison]
    if poisoned:
        print("  -- Poison --")
    for character in poisoned:
        damage = character.tick_poison()
        print(f"  {character.name} takes {damage} poison damage: {character}")
        if not character.is_alive():
            defeat(character, side)


def fight(party, enemies):
    """The party fights a group of enemies until one side is dead. Returns True if the party wins.

    Each round every living hero attacks the first living enemy,
    then every living enemy attacks a random living hero,
    then everyone with poison takes poison damage.
    Characters spawned on death join their side immediately.
    """
    print(f"\n=== {', '.join(str(hero) for hero in party)}")
    print(f"    vs {', '.join(str(enemy) for enemy in enemies)} ===")
    round_number = 1
    while alive(party) and alive(enemies):
        input(f"\nRound {round_number} - press Enter to roll...")
        for hero in alive(party):
            if not alive(enemies):
                break
            take_turn(hero, alive(enemies)[0], party, enemies)
        for enemy in alive(enemies):
            if not alive(party):
                break
            take_turn(enemy, random.choice(alive(party)), enemies, party)
        poison_tick(party)
        poison_tick(enemies)
        round_number += 1

    if alive(party):
        print("\nVictory!")
        return True
    return False
