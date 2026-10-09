# Dice Roguelike

Python dice autobattler — three heroes, twenty fights, items and rank-ups.

## Play (browser UI)

```bash
python3 -m ui.server
```

Open [http://127.0.0.1:8765](http://127.0.0.1:8765)

## To kill the UI

```bash
lsof -ti :8765 | xargs kill
```

## Play (terminal)

```bash
python3 main.py
```

## Balance sims

```bash
python3 tools_sim_items.py
```

Results land in `Simulation_Results/<timestamp>/` and a new Cursor canvas.