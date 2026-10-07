from Characters.Heroes import tier1, tier2, tier3

HERO_TIERS = {
    1: tier1.HEROES,
    2: tier2.HEROES,
    3: tier3.HEROES,
}

# Hero class -> its tier, e.g. HERO_TIER[Warrior] == 1.
HERO_TIER = {hero: tier for tier, heroes in HERO_TIERS.items() for hero in heroes}
