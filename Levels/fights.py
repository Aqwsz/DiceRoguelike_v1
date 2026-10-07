# Each fight is {tier: number of enemies}. Each enemy is picked at random from that tier.
# e.g. {1: 2, 2: 1} summons two random tier 1 enemies and one random tier 2 enemy.
# Empty fights {} are skipped.

FIGHTS = [
    {# Fight 1
        1: 1
    }, 
    {# Fight 2
        1: 2
    },
    {# Fight 3
        1: 3
    },    
    {# Fight 4
        1: 4
        },     
    {# Fight 5 Mini Boss
        "miniboss": 1
    },     
    {# Fight 6
        1: 1,
        2: 1,
    },      
    {# Fight 7
        1: 0,
        2: 2,
    },       
    {# Fight 8
        1: 6,
        2: 0,
    },      
    {# Fight 9
        1: 2,
        2: 2,
    },      
    {# Fight 10 Mini Boss
        "miniboss": 2
    },      
    {# Fight 11
        1: 1,
        2: 0,
        3: 1,
    },      
    {# Fight 12
        1: 1,
        2: 1,
        3: 1,
    },      
    {# Fight 13
        1: 1,
        2: 2,
        3: 1,
    },      
    {# Fight 14
        1: 3,
        2: 2,
        3: 1,
    },      
    {# Fight 15 Mini Boss
        "miniboss": 3
    },      
    {# Fight 16
        1: 1,
        2: 0,
        3: 2,
    },      
    {# Fight 17
        1: 0,
        2: 2,
        3: 2,
    },      
    {# Fight 18
        1: 1,
        2: 0,
        3: 3,
    },      
    {# Fight 19
        1: 0,
        2: 3,
        3: 3,
    },      
    {# Fight 20 Final Boss
        "finalboss": 1
    },
]
