# Roadmap

Tick items off as they're done. "Check" lists what gets verified when you ask for a review.

## 1. Add more heroes
- [x] Tier 1 heroes (Warrior, Berserker, Archer, Rogue, Mage, Speller)
- [x] Tier 2 heroes (Knight, Paladin, Assassin, Hunter, Magician, Sorcerer)
- [x] Tier 3 heroes (Barbarian, Ragebringer, Sniper, Quartermaster, Queen, Cleric)
- [x] Decide how tier 2 and 3 heroes enter a run: after every even fight win, pick 1 of 2 upgrades for a lowest-tier hero (`upgrades.py`)

Check: every class is in its file's `HEROES` list, has exactly 6 faces, and every face exists in `faces.py`. Party options never repeat a hero.

## 2. Add more enemies
- [x] Tier 1 (Slime, Goblin, Skeleton, Crawler)
- [x] Tier 2 (Ogre, Troll, Vampire, Slime Mother)
- [x] Tier 3 (Hawk, Dice, Werewolf, Bomber)
- [x] Minibosses (Witch, Pirate, Vampire)
- [x] Final bosses (Dragon, Graveyard King)
- [ ] Two different enemies are both named "Vampire" (tier 2 and miniboss)

Check: same as heroes, using the `ENEMIES` lists.

## 3. Finish all fights
- [x] Fights 1-6
- [x] Fights 7-19
- [x] Fight 20 set to final boss

Check: every tier used in `Levels/fights.py` has at least one enemy; a full run from fight 1 to 20 completes without errors.

## 4 Add new effects
- [ ] Poison
- [ ] Group Heal
- [ ] Mana and autospell (5 mana for 8 damage or something)


## 5. Add upgrades
- [ ] Decide what an upgrade is (e.g. swap a die face, raise max HP, hero tier up)
- [ ] Decide when upgrades are offered (after each fight, after minibosses, ...)
- [ ] Implement choosing an upgrade

Check: permanent HP upgrades raise `base_max_hp`; upgrades persist across fights within a run.

## 6. Add items
- [ ] Decide what items do and how they're obtained (drops, shop)
- [ ] Temporary items raise `max_hp` only (removed by the full heal after a fight)
- [ ] Permanent items raise `base_max_hp`
- [ ] Implement an inventory / shop

Check: temporary effects end after the fight; permanent effects last the whole run.

## 7. Add prestige
Beat fight 20 to prestige; then a prestige shop, and run fights 1-20 again at a harder prestige level.
- [ ] Track the current prestige level
- [ ] Decide what "harder" means per prestige level (more enemy HP, more damage, more enemies, ...)
- [ ] Prestige currency and what it's earned from
- [ ] Prestige shop
- [ ] Decide what carries over into the next prestige run and what resets

Check: prestige 1 is harder than prestige 0; shop purchases apply in the next run; prestige ends at 10.

## 8. Add rebirth
Beat prestige 10 to rebirth. Rebirth is account based.
- [ ] Save file so progress survives closing the game (needed before rebirth; prestige probably needs it too)
- [ ] Decide what rebirth gives and what it resets (prestige back to 0?)
- [ ] Rebirth rewards / shop

Check: rebirth progress is still there after restarting the game; a corrupt or missing save file doesn't crash the game.
