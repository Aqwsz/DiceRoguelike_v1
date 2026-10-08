# Roadmap

Tick items off as they're done. "Check" lists what gets verified when you ask for a review.

## 1. Add more heroes
- [x] Tier 1 heroes (Warrior, Berserker, Archer, Rogue, Mage, Speller)
- [x] Tier 2 heroes (Knight, Paladin, Assassin, Hunter, Magician, Sorcerer)
- [x] Tier 3 heroes (Barbarian, Ragebringer, Sniper, Quartermaster, Queen, Cleric)
- [x] Decide how tier 2 and 3 heroes enter a run: after every even fight win, pick 1 of 2 rank-ups for a lowest-tier hero (`hero_rankup.py`)

Check: every class is in its file's `HEROES` list, has exactly 6 faces, and every face exists in `faces.py`. Party options never repeat a hero.

## 2. Add more enemies
- [x] Tier 1 (Slime, Goblin, Skeleton, Crawler)
- [x] Tier 2 (Ogre, Troll, Vampire, Slime Mother)
- [x] Tier 3 (Hawk, Dice, Werewolf, Bomber)
- [x] Minibosses (Witch, Pirate, Vampire)
- [x] Final bosses (Dragon, Graveyard King)
- [x] Two different enemies are both named "Vampire" (tier 2 and miniboss)

Check: same as heroes, using the `ENEMIES` lists.

## 3. Finish all fights
- [x] Fights 1-6
- [x] Fights 7-19
- [x] Fight 20 set to final boss

Check: every tier used in `Levels/fights.py` has at least one enemy; a full run from fight 1 to 20 completes without errors.

## 4 Add new effects
Combat stays an autobattler: no choosing who to hit.
- [x] Poison damage (`faces.POISON_N`; used by Potioner)
- [x] Group Heal (`faces.GROUP_HEAL_N`; used by Potioner)
- [x] Mana and autospell (`faces.MANA_N`; after hero turns, spend 5 mana for 8 damage, can cast multiple times)
- [x] Monster death effects: `SPAWN_ON_DEATH = {Class: count}` (Slime Mother spawns 2 Slimes, Graveyard King spawns 2 Skeletons)
- [x] Shield / block (`faces.SHIELD_N`; random ally, absorbs damage, expires each round)
- [x] Stun (`faces.STUN`; random foe skips its next roll)
- [x] Weaken (`faces.WEAKEN_N`; N damage and target deals N less)
- [x] Burn (`faces.BURN_N`; like poison but fades by 1 each round)
- [x] Thorns (`faces.THORNS`; random ally — attackers take the hit instead)
- [ ] Taunt (enemies must target this hero)
- [x] Damage all enemies (`faces.DAMAGE_ALL_N`)

Check: each effect has a `faces.EFFECT_N` (or equivalent) and applies in combat without errors.

## 4b. Combo stickers
Not a new die face by itself: extra rules stuck onto an existing face (and items can add them).
- [x] Decide sticker format (`Characters/stickers.py`; stacked multipliers on a die slot)
- [x] Stickers can be on a face in a hero/enemy die (`Die.stickers` per slot)
- [x] Items can add a sticker to a face (`StickerItem` / `common.STICKER_*`)
- [x] Unequipping an item removes the sticker it added
- [x] Double damage if at full HP (`stickers.FIRST_STRIKE`, tier-1 item)
- [x] Double damage if below half HP (`stickers.EXECUTE`, tier-2 item)

Check: a face with a sticker still rolls as that face, plus the extra rule; removing the item undoes the sticker.

## 5. Add items
- [x] Item types: one hero max HP, party max HP, swap a die face, or custom code (`Items/item.py`); ready-made numbered items in `Items/common.py`
- [x] Obtained after every odd fight win, 1 of 2; item tier = 1 after fight 1, 2 after fight 3, ... 10 after fight 19
- [x] Inventory of every item obtained this prestige (`inventory.py`), shown at the end of a run
- [x] Every item is equipped on a hero (max 3 per hero, `MAX_ITEMS` in `Characters/Heroes/hero.py`); unequip moves it to the bag and undoes its effect
- [x] Equip / unequip menu after each item pick; a full hero must unequip one item to take a new one
- [x] Permanent items raise `base_max_hp`
- [x] Tier 1-2 items (started)
- [x] Tier 3-10 items (`Items/tier3.py` ... `tier10.py`, currently empty)
- [x] Temporary items (raise `max_hp` only, removed by the full heal after a fight)
- [ ] Extra reward after every miniboss fight
- [ ] Permanent HP carries into prestige runs (needs prestige, see 7)

Check: every item class is in its file's `ITEMS` list and applies without errors; permanent HP items raise `base_max_hp` and survive full heals and hero rank-ups; the inventory lists every item obtained.

## 6. Random events
25% chance after a won fight that is not a miniboss or final boss (`Levels/events.py`).
- [x] After each non-boss fight, 25% chance of an event (`EVENT_CHANCE`)
- [x] Event file so new events are easy to add (`Levels/events.py`, list `EVENTS`)
- [x] A few starter events (Shrine of Vigor, Blood Altar, Forked Path)
- [ ] More events
- [ ] Event outcomes apply and can be undone only if they are temporary effects

Check: an event can appear after a normal fight; miniboss and boss fights never roll one; adding a class to `EVENTS` is enough to include it.

## Add UI
- [x] Browser UI (`python3 -m ui.server` → http://127.0.0.1:8765)
- [x] Party select, fight view, item/rank-up/event choices
- [ ] Polish: animations, sound, inventory manage screen

## Organize files
- [ ] Python files that only describe the framework and keep the game intact like combat.py and inventory.py go into a directory called /src/. If there are files like this inside directorys, like /Items/ or /Characters/, put in its own /src/ directory inside the initial directory
- [ ] Files that require edits in the future, like items, tiers, heroes, enemies, should stay mostly where they currently are

## Make minibosses harder

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

## 9. Enemy passives
Always-on enemy abilities beyond the die (and beyond `SPAWN_ON_DEATH`).
- [ ] Passive hook on enemies (e.g. regenerate 2 HP each round, explode on death)
- [ ] A few starter passives on existing enemies

Check: passives fire at the right time; adding a new one is one field/class on the enemy, no copied combat code.

## 10. Hero passives and party synergies
- [ ] Each hero class can have one always-on passive (e.g. Berserker +1 damage below half HP)
- [ ] Party synergies from team makeup (e.g. 2+ magic users: all spells +1)

Check: passives and synergies apply in combat; ranking up a hero updates which passives/synergies are active.

## 11. Quality of life (options)
- [ ] Colored output option (e.g. red damage, green heal, purple poison)
- [ ] Auto-roll option (skip "press Enter" each round)

Check: both can be turned on and off; the game still plays correctly with either off.

## Later (not now)
- [ ] Rerolls (each hero gets rerolls per fight; items could add more)
- Target choosing: skipped on purpose; combat stays an autobattler.
