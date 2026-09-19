# Chrono Blight

> A 2D pixel-art Metroidvania built with Python, Pygame, and the Gale framework — featuring temporal phase-shifting, three combat forms, and a multi-phase final boss.

---

## Story

The timeline is fracturing. A corrupted force known as **The Harvester** is bleeding the two eras — Past and Future — into chaos. You are a traveler who can shift between both, wielding three forms of power to restore balance.

Explore 8 interconnected rooms across crumbling sanctuaries, abysses, and ancient pyramids. Defeat three bosses. Survive.

---

## Features

- **Temporal Phase-Shifting** — toggle between Past (green) and Future (red) to reveal hidden platforms, open new paths, and interact with phase-locked hazards
- **3 Unlockable Combat Forms:**
  - 🔮 **Phase Mage** — ranged arcane bolt + Infernal Flame area attack, mana-focused
  - ⚔️ **Swordmaster** — melee combo + double jump + Thrust Dash
  - 🐾 **Beast Morph** — high HP, claw strikes, dash, Primal Impact slam
- **3 Bosses with multiple phases:**
  - *Temporal Lurker* — timed survival challenge (80 seconds)
  - *Void High Priest* — arcane shield, void orbs, ground shockwaves, lava shower
  - *The Harvester* — 3-phase climax: open combat → darkness with light monoliths → aerial platform duel
- **8 interconnected rooms** with blocked doors, event-driven progression, and a full world map
- **Visual novel intro** — 9-panel cinematic story sequence when starting a new game
- **3 save slots** with full persistence (room, form, HP, exploration %, playtime)
- **Fully remappable controls** with persistent `controls.json`
- **HUD** with HP/MP bars, active form indicator, cooldown wheel, and ghost mode during arena events
- **Animated paper map** with fog-of-war, radar pulse, and room details

---

## Requirements

| Dependency | Version |
|---|---|
| Python | 3.13+ |
| Pygame | 2.6.0+ |
| Gale Engine | 1.16.0+ |

---

## Installation & Running

```bash
# 1. Clone the repository
git clone https://github.com/Breixosepi/chrono-blight.git
cd chrono-blight

# 2. Create a virtual environment
py -3.13 -m venv .venv

# 3. Activate it
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the game
python main.py
```

---

## Default Controls

| Action | Key |
|---|---|
| Move left / right | `A` / `D` |
| Jump | `Space` |
| Look up (elevator) | `W` |
| Dash | `Left Shift` |
| Basic attack | `J` |
| Special attack | `K` |
| Phase shift (Past ↔ Future) | `L` |
| Previous form | `Q` |
| Next form | `E` |
| World map | `M` |
| Pause | `P` |

> All controls are fully remappable from the **SETTINGS** screen, accessible from the main menu or the pause menu. Bindings are saved automatically to `src/controls.json`.

---

## Project Structure

```
chrono-blight/
├── main.py                      # Entry point
├── settings.py                  # Global config, asset loading, fonts, sounds, utilities
├── requirements.txt
├── CHANGELOG.md
├── assets/
│   ├── fonts/                   # Pixel-art fonts (golden-apple.ttf, Undaunted-DEMO.otf)
│   ├── graphics/                # Sprites, backgrounds, effects, UI sheets
│   ├── sounds/                  # SFX and music tracks (.wav / .mp3)
│   └── tilemaps/                # Tiled JSON maps for all 8 rooms
└── src/
    ├── ChronoBlight.py          # Main game class (extends gale.game.Game)
    ├── controls_manager.py      # Remappable keybind manager with JSON persistence
    ├── definitions/             # Entity stats, animation defs, frame generators
    ├── entities/                # Entity, Player, Enemy, Boss base classes
    ├── states/
    │   ├── game/                # TitleState, SplashState, StoryIntroState, PlayState,
    │   │                        # PauseState, MapState, SettingsState, PhaseShiftState,
    │   │                        # SlotSelectState, GameOverState, VictoryState
    │   ├── entity/              # Player, enemy and boss state machines (FSM)
    │   │   ├── player/          # Idle, Walk, Jump, Fall, Dash, Attack, Special, Hit, Death, Unlock
    │   │   ├── enemy/           # Patrol, Chase, Attack, Hit, Death
    │   │   └── boss/            # Cultist, Lurker, Harvester states
    │   └── hazard/              # Inactive, Triggered, Moving, Escaped states
    ├── ui/                      # HUD, MenuBackground
    └── world/
        ├── Room.py              # Active room: tilemap, camera, entities, hazards, arena
        ├── room_connections.py  # Room graph with exit validation lambdas
        ├── objects/             # Altar, Elevator, FallingTrap, SawHazard,
        │                        # RisingHazard, LavaShower, LightMonolith, HealthOrb
        └── systems/             # ArenaManager, Camera, CombatResolver, DarknessOverlay,
                                 # ParticleSystem, RoomRenderer, RoomEventLogic, tile_collision
```

---

## Architecture Highlights

- **StateStack** (Gale) — game-level screen management. States push/pop cleanly without leaking audio or input.
- **StateMachine** (Gale) — per-entity FSM for player, enemies, and each boss. Every behavior is an isolated state.
- **Timer.after / Timer.tween / Timer.every** (Gale) — all timed events (arena banners, teleports, door openings, darkness fades) use Gale's timer system.
- **SaveManager** (Gale) — slot-based save/load with metadata envelope. Persistence lives in `saves/slot_X.sav`.
- **Command Pattern** (Gale) — all player inputs are bound via `CommandBindings`; controls_manager rebuilds bindings dynamically on remap.
- **Animation** (Gale) — `Entity._create_animations()` wraps Gale `Animation` objects from frame rect lists.

---

## Asset Credits

See [CREDITS.md](CREDITS.md) for the full list of free-use assets with authors and licenses.

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for the complete version history.

---

## License

This project is an academic submission developed for the **ISPPV1** course. All original code is authored by the project team. Third-party assets are used under their respective free/open licenses (see `CREDITS.md`).

