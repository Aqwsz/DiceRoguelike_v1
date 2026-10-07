def describe_hero_class(hero_class, indent):
    faces = ", ".join(face.describe() for face in hero_class.FACES)
    print(f"{indent}{hero_class.NAME} - {hero_class.MAX_HP} HP")
    print(f"{indent}  Die: {faces}")


def ask_choice(count):
    """Ask for a number from 1 to count and return it as a 0-based index."""
    while True:
        choice = input("\n> ").strip()
        if choice.isdigit() and 1 <= int(choice) <= count:
            return int(choice) - 1
        print(f"Please enter a number from 1 to {count}.")
