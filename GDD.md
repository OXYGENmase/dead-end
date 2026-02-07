# Dead End - GDD

Maze-based zombie tower defense. Build a maze, kill zombies, survive waves.

## Core Loop

1. **Build** - Place towers to create maze
2. **Defend** - Survive zombie waves  
3. **Earn** - Get money for kills
4. **Upgrade** - Buy more towers
5. **Repeat** - Next wave, stronger enemies

## Mechanics

### Maze Building
- Towers block paths
- Zombies pathfind around them
- Longer path = more time to shoot
- Must keep path open (start to exit)

### Towers (3 types)

| Tower | Cost | Dmg | Range | Notes |
|-------|------|-----|-------|-------|
| Rifleman | $50 | 10 | 4 | Fast fire, single target |
| Sniper | $100 | 40 | 8 | Slow, instant hit |
| Barricade | $25 | - | - | Blocks path, high HP |

### Enemies (2 types)

| Enemy | HP | Speed | Reward |
|-------|-----|-------|--------|
| Walker | 30 | Slow | $5 |
| Runner | 15 | Fast | $8 |

### Waves
- 5 waves, escalating difficulty
- More runners in later waves
- Wave clear bonus: $10 + wave * 5

## Controls

| Key | Action |
|-----|--------|
| Click | Select/place tower |
| Right-click | Cancel |
| Space | Start wave |
| ESC | Pause |
| F3 | Debug overlay |
| F5 | Screenshot |
| F6 | Snapshot |

## Tech

- Python 3.11+
- Pygame-CE 2.5+
- No external deps

## Architecture

```
game/
  entities/     # Tower, Enemy, Projectile
  systems/      # Economy, Waves, Pathfinder, Debug
  ui/           # HUD, Menus
```

State machine: MENU -> BUILD -> WAVE -> (repeat) -> GAMEOVER/VICTORY

## Build

```bash
pip install -r requirements.txt
python main.py
```

## Todo

- [ ] More tower types
- [ ] Tower upgrades  
- [ ] More enemy types
- [ ] Multiple maps
- [ ] Sound
- [ ] Sprite art
