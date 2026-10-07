# Each fight is {tier: number of enemies}. Each enemy is picked at random from that tier.
# e.g. {1: 2, 2: 1} summons two random tier 1 enemies and one random tier 2 enemy.
# Empty fights {} are skipped.

FIGHTS = [
    {1: 1},  # Fight 1
    {1: 2},      # Fight 2
    {1: 3},      # Fight 3
    {1: 4},      # Fight 4
    {"miniboss": 1},      # Fight 5
    {# Fight 6
        1: 1,
        2: 1
    },      
    {},      # Fight 7
    {},      # Fight 8
    {},      # Fight 9
    {},      # Fight 10
    {},      # Fight 11
    {},      # Fight 12
    {},      # Fight 13
    {},      # Fight 14
    {},      # Fight 15
    {},      # Fight 16
    {},      # Fight 17
    {},      # Fight 18
    {},      # Fight 19
    {"finalboss": 1},      # Fight 20
]
