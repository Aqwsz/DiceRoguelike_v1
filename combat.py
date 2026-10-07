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


def fight(hero, enemies):
    """Hero fights a group of enemies until one side is dead. Returns True if the hero wins.

    Each round the hero attacks the first living enemy, then every living enemy attacks the hero.
    """
    print(f"\n=== {hero} vs {', '.join(str(enemy) for enemy in enemies)} ===")
    round_number = 1
    while hero.is_alive() and any(enemy.is_alive() for enemy in enemies):
        input(f"\nRound {round_number} - press Enter to roll...")
        target = next(enemy for enemy in enemies if enemy.is_alive())
        take_turn(hero, target)
        for enemy in enemies:
            if enemy.is_alive() and hero.is_alive():
                take_turn(enemy, hero)
        round_number += 1

    if hero.is_alive():
        print("\nVictory!")
    return hero.is_alive()
