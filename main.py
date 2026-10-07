import random
from collections import Counter

from Characters.Heroes import HERO_TIERS
from Characters.Enemies import ENEMY_TIERS
from Levels.fights import FIGHTS
from combat import fight


def choose_hero(heroes):
    print("Choose your hero:")
    for number, hero_class in enumerate(heroes, start=1):
        faces = ", ".join(face.describe() for face in hero_class.FACES)
        print(f"  {number}. {hero_class.NAME} - {hero_class.MAX_HP} HP")
        print(f"     Die: {faces}")

    while True:
        choice = input("> ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(heroes):
            return heroes[int(choice) - 1]()
        print(f"Please enter a number from 1 to {len(heroes)}.")


def summon_enemies(fight_plan):
    enemies = []
    for tier, count in fight_plan.items():
        if tier not in ENEMY_TIERS:
            raise ValueError(f"Unknown enemy tier {tier!r}, expected one of {list(ENEMY_TIERS)}")
        pool = ENEMY_TIERS[tier]
        if count and not pool:
            raise ValueError(f"Fight wants {count} tier {tier} enemies, but tier {tier} has none")
        enemies += [random.choice(pool)() for _ in range(count)]

    # Number duplicates so "Slime 1" and "Slime 2" can be told apart in the log.
    totals = Counter(enemy.name for enemy in enemies)
    seen = Counter()
    for enemy in enemies:
        if totals[enemy.name] > 1:
            seen[enemy.name] += 1
            enemy.name = f"{enemy.name} {seen[enemy.name]}"
    return enemies


def main():
    hero = choose_hero(HERO_TIERS[1])
    for number, fight_plan in enumerate(FIGHTS, start=1):
        if not fight_plan:
            continue
        print(f"\n##### Fight {number} #####")
        if not fight(hero, summon_enemies(fight_plan)):
            print("Game over.")
            return
        hero.full_heal()
        print(f"{hero.name} rests and recovers: {hero}")
    print(f"\n{hero.name} cleared every fight. You win!")


if __name__ == "__main__":
    main()
