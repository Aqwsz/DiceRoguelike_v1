import random


def apply_face(user, target, face):
    """Apply a rolled face. Extend this when you add new effect types to Face."""
    if face.damage:
        target.take_damage(face.damage)
    if face.heal:
        user.heal(face.heal)


def take_turn(user, target):
    face = user.roll()
    print(f"  {user.name} rolls {face.describe()}")
    apply_face(user, target, face)
    print(f"    {user}  |  {target}")
    if not target.is_alive():
        print(f"  {target.name} is defeated!")


def alive(characters):
    return [character for character in characters if character.is_alive()]


def fight(party, enemies):
    """The party fights a group of enemies until one side is dead. Returns True if the party wins.

    Each round every living hero attacks the first living enemy,
    then every living enemy attacks a random living hero.
    """
    print(f"\n=== {', '.join(str(hero) for hero in party)}")
    print(f"    vs {', '.join(str(enemy) for enemy in enemies)} ===")
    round_number = 1
    while alive(party) and alive(enemies):
        input(f"\nRound {round_number} - press Enter to roll...")
        for hero in alive(party):
            if not alive(enemies):
                break
            take_turn(hero, alive(enemies)[0])
        for enemy in alive(enemies):
            if not alive(party):
                break
            take_turn(enemy, random.choice(alive(party)))
        round_number += 1

    if alive(party):
        print("\nVictory!")
        return True
    return False
