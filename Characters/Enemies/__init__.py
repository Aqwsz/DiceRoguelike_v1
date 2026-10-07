from Characters.Enemies import tier1, tier2, tier3, miniboss, finalboss

# Keys used in Levels/fights.py, e.g. {1: 2, "miniboss": 1}.
ENEMY_TIERS = {
    1: tier1.ENEMIES,
    2: tier2.ENEMIES,
    3: tier3.ENEMIES,
    "miniboss": miniboss.ENEMIES,
    "finalboss": finalboss.ENEMIES,
}
