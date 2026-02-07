# Dead End - Design Document

Design evolution and roadmap for contributors.

---

## Core Concept

Maze-based tower defense where players create the path. Unlike traditional TD where paths are fixed, here towers become walls that zombies must path around. Longer path = more time to shoot.

---

## Design Pillars

1. **Player Agency** - You build the maze, not just place towers
2. **Clarity** - Every tile matters, no visual noise
3. **Depth through simplicity** - Few towers, many combinations

---

## Current State (MVP)

### Grid
- 30x20 tiles
- Auto-centers on screen
- Real-time pathfinding validation

### Towers (3)
| Tower | Role | Key Trait |
|-------|------|-----------|
| Rifleman | Basic DPS | Reliable, cheap |
| Sniper | Long range | Slow but strong |
| Barricade | Wall | Blocks, high HP |

### Enemies (2)
| Enemy | Counter |
|-------|---------|
| Walker | Anything |
| Runner | Fast fire rate |

---

## Planned Content

### Additional Towers

**Shotgunner** - Cone damage, short range
**Flamethrower** - Piercing beam, DoT
**Tesla** - Chain lightning
**Freezer** - Slows enemies
**Mortar** - Long range AoE

### Additional Enemies

**Tank** - High HP, slow, ignores first hit
**Spitter** - Ranged, attacks towers
**Swarmer** - Weak but numerous
**Boss** - Every 10 waves, heals others

### Upgrade System

Each tower: 2 upgrade paths
- Path A: More damage
- Path B: Faster firing

---

## UI Design

### Screen Layout

```
[Top Left]       [Center]      [Top Right]
Phase indicator   Game Grid     Money/Lives
Wave status                     Enemy count

[Bottom: Tower Selection]
```

### Future Additions

- Left: Wave preview (what's coming)
- Right: Mini-map, speed control
- Bottom: Upgrade panel when tower selected

---

## Roadmap

| Phase | Status | Content |
|-------|--------|---------|
| 1 | Done | MVP - 3 towers, 2 enemies, 5 waves |
| 2 | Next | 5 more towers, 4 more enemies, upgrades |
| 3 | Future | Sound, particles, polish |
| 4 | Future | Multiple maps, skill tree, saves |

---

## Contributing

See a bug? Want to add a tower? PRs welcome.

Design discussions in Issues before major changes.
