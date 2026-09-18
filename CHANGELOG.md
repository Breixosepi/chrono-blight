# Changelog — Chrono Blight

All notable changes to **Chrono Blight** (2D Action Platformer / Metroidvania built with Gale and Pygame) are documented in this file.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [0.22.0] - 2026-09-18

### Added
- **9-Panel Visual Novel Cinematic Prologue (`src/states/game/StoryIntroState.py`)**:
  - Interactive narrative state with retro visual-novel aesthetics, automatically triggered when starting a new game from `SlotSelectState`.
  - 9 full-screen illustrations displayed with smooth crossfade transitions via `Timer.tween` transparency interpolation.
  - Panoramic bottom dialogue box optimized to avoid covering the central artwork, laid out in `hud_small` (9pt) font.
  - Panel progress counter and thematic speaker badges (*Ancient Chronicler*, *Phase Mage*, *Voice of Fate*).
  - Dynamic typewriter effect at 0.022s per character with subtle rhythmic keystroke sound and volume attenuation.
  - Fast-forward with `[ENTER]` / `[SPACE]`, dimensional audio transitions between panels (`phase_shift_past` and `phase_shift_future`), and direct prologue skip to game with `[ESC]`.
- **Vector Composition for HD Splash Screen (`src/states/game/SplashState.py`)**:
  - Replaced low-resolution flattened graphics with a real-time programmatic composition pipeline.
  - Procedural generation of pure elliptic radial gradients (deep emerald for the Past and crimson for the Future) eliminating color banding and compression artifacts.
  - Rendered high-definition transparent logo (`2816x1536`) scaled with bilinear `pygame.transform.smoothscale`, delivering maximum sharpness, contrast, and legibility for lettering and clockwork gears.

---

## [0.21.0] - 2026-09-18

### Changed / Improved
- **Final Boss Tuning and Dynamism (The Harvester)**:
  - *Phase 1*: Removed exclusive phase-color vulnerability condition; the boss is now vulnerable to any player form without forcing constant era switching.
  - *Phase 2*: Increased challenge during darkness. Attack cooldown reduced (0.65s – 1.0s), combined rapid falling-sword bursts (0.35s warning), predictive cut toward player movement (0.60s), and horizontal wind blades to force active jumps and dodges toward monoliths.
  - *Phase 3*: Replaced conditional temporal platforms with exclusively neutral base-layer `ground` platforms (`(672.0, 133.0)`, `(896.0, 133.0)`, `(785.0, 85.0)`, upper wing ledges), eliminating the visual bug where the boss levitated when alternating eras.
- **Ergonomic and Remappable Controls (`src/controls_manager.py` and `SettingsState.py`)**:
  - Interactive key-rebinding screen (`SettingsState`) accessible from both `TitleState` and `PauseState`.
  - Automatic persistence of custom controls in `controls.json`, with a reset-to-defaults button.
  - Modern default layout: WASD (movement), Q/E (cycle forms), J (attack), K (special), L (phase shift), L-SHIFT (dash), SPACE (jump), M (map), P (pause).
- **Dynamic and Soundscaped Elevators (`Elevator.py`)**:
  - Elevator interaction key now dynamically uses the configured "up" binding (W or arrow key per user settings), with a contextual on-screen prompt `[W] GO UP`.
  - Added rock-crumbling and mechanism sound effects (`rock-crack` + `close`) when descending, and a heavy impact + open sound (`rock-smash` + `open`) when landing on the ground floor.

---

## [0.20.0] - 2026-09-18

### Added
- **Opening Cinematic Splash (`src/states/game/SplashState.py`)**:
  - Initial display of `logo_past` for 1.0s, then a temporal transition to `logo_future` for 1.0s with a red dimensional flash and `phase_shift_future` sound.
  - Smooth transition to `TitleState` after 2.0s, with support for instant skip via any key (`[ENTER]`, `[SPACE]`, `[ESC]`).
  - Fires exclusively on initial game boot (`ChronoBlight.init()`); death restarts and pauses return directly to the menu without forcing the intro again.
- **Dynamic Crossfade Menu Background Manager (`src/ui/MenuBackground.py`)**:
  - Shared continuous background component between `TitleState` and `SlotSelectState`.
  - Cyclic alternation every 30 seconds between Past era (`gothic_castle_past`) and Future era (`gothic_castle_future`).
  - Smooth 1.5-second crossfade between textures with a translucent contrast overlay (`(14, 10, 20, 130)`) ensuring full readability of golden fonts and pixel art.

### Changed / Improved
- **Menu Visual Ambiance (`TitleState.py` and `SlotSelectState.py`)**:
  - Replaced flat solid backgrounds (`surface.fill((16, 12, 24))`) with the coordinated `menu_background` cycle, keeping the temporal transition active and continuous when navigating between both screens without restarts or cuts.

---

## [0.19.0] - 2026-09-18

### Added
- **Top UI Layer and Smart Ghost HUD (`render_top_ui` and `HUD.py`)**:
  - Added `render_top_ui` method in `RoomRenderer`, `Room`, and `PlayState` so arena text, unlock labels, and damage popups render on top of the player HUD.
  - Dynamic ghost mode on the HUD (`alpha = 65`) when active arena banners, top-left popups, or form/stat unlock animations are displayed.
- **Permanent Stat Boost Persistence (`UnlockState.py` and `Player.py`)**:
  - Linked the `stats` event after defeating the Void High Priest to effectively apply +30 HP and +20 MP permanently to all current and future player forms.

### Changed / Improved
- **Post-Final-Boss Metroidvania Save (`VictoryState.py` and `SlotSelectState.py`)**:
  - Removed auto-save in `VictoryState`: defeating The Harvester no longer overwrites the slot from inside the boss chamber.
  - The run retains the last altar or monolith checkpoint, allowing resumption before the boss fight with the boss alive and free exploration.
  - Sanitization in `SlotSelectState`: safe redirect to `middle` in front of the elevator and removal of lock flags for saves previously made in `big_room`.
- **Boss Rebalance for Extended Combat (`entity.py` and `ArenaManager.py`)**:
  - *Void High Priest (`cultist_priest`)*: Health increased to 350 HP, contact damage to 10, projectile damage to 12 (cooldown 2.4s).
  - *The Harvester (`the_harvester`)*: Health increased to 520 HP, allowing its 3 phases (regular combat, darkness with monoliths, platform duel) to have proper duration. Slash and dash damage calibrated to 14.
  - *Temporal Lurker (`monster2_boss`)*: Maintained in timed survival mode (60s) with adjusted damage of 8 and 12.
- **Player Form Rebalance (`src/definitions/entity.py` and `combat.py`)**:
  - *Phase Mage*: 55 HP, 75 MP, 4.0 MP/s regen. Arcane Bolt (25 dmg, 0 MP) and Infernal Flame Area (60 dmg to normal enemies in area, calibrated to 20 dmg with 1 hit per cast against bosses to prevent disproportionate damage, 25 MP).
  - *Beast Morph*: 90 HP, 45 MP, 3.0 MP/s regen, 1 jump. Beast Claw (14 dmg, 0 MP), Primal Impact (25 dmg, 15 MP), Beast Dash (12 MP).
  - *Swordmaster*: 70 HP, 30 MP, 2.2 MP/s regen, 2 jumps (double jump). Sword combo (16 and 22 dmg, 0 MP) and Thrust Dash (20 MP).

### Fixed
- **Mojibake in Boss Combat Announcements (`ArenaManager.py`)**:
  - Removed corrupt characters (mojibake) in boss phase announcements and transitions, eliminating glyph-missing text boxes.
- **Floating Damage Popup Cleanup (`Room.py`, `Boss.py`, `FallingTrap.py`, `HarvesterAttackState.py`, `HarvesterDashState.py`)**:
  - Removed attack descriptions from popups, now displaying only the clean damage number received.

---

## [0.18.0] - 2026-09-18

### Added
- **Pixel-Art Typography Standardization (`settings.FONTS` and `assets/fonts/`)**:
  - Official font set in `settings.FONTS`: `hud` (10pt), `hud_small` (9pt), `ui` (10pt), `title` (18pt) with `golden-apple.ttf`, and `main-title` (24pt) with `Undaunted-DEMO.otf`.
  - Minimum font size threshold set at 9pt (`hud_small`), ensuring maximum pixel-art sharpness and readability at retro virtual resolution (320×180).
- **Multiline Text and Perimeter Clamping in `_crisp_render_text` (`settings.py`)**:
  - Native newline (`\n`) support with dynamic proportional vertical spacing (`font.get_linesize()`), avoiding non-printable glyph artifacts.
  - Automatic perimeter clamping to surface bounds (`clamp_to_surface=True`): contains floating text and combat numbers within visible screen margins, preventing popups from being clipped out of the window.
- **Technical Architecture Documentation (`ARCHITECTURE.md`)**:
  - Created the architectural technical document at the project root detailing modules, decoupled subsystems (FSM, StateStack, Command Pattern), rendering pipeline, world topology, and Mermaid diagrams.

### Changed / Improved
- **Overflow Prevention and Layout in Pause Menu (`src/states/game/PauseState.py`)**:
  - Expanded scroll board width to `BOARD_W = 264` px for comfortable visual margin at 320 px resolution.
  - Reorganized `CONTROLS & FORMS` sub-screen into two clean columns (`key` at `bx + 12`, `description` at `bx + 84`).
  - Adopted `hud_small` (9pt) font and condensed skill descriptions, eliminating clipping from long phrases.
- **Anti-Collision Restructuring in the World Map (`src/states/game/MapState.py`)**:
  - Condensed unexplored room description from a 283px overflowing string to a 146px `hud_small` string.
  - Full footer reorganization: clean separation between controls on the left and exploration percentage with progress bar on the right.
- **Save Slot Card Margin Adjustments (`src/states/game/SlotSelectState.py`)**:
  - Increased card width to `card_w = 236` px.
  - Applied `hud_small` (9pt) for save details, playtime, exploration %, and empty slot text.
- **HUD Visual Calibration (`src/ui/HUD.py`)**:
  - Adjusted container dimensions to 88×36 px.
  - Repositioned active form labels to `row_forms_y = 20`, preventing overflow below the frame border.

### Fixed
- **HP/MP Bar vs Digit Overlap in HUD (`src/ui/HUD.py`)**:
  - Reduced HP and MP bar widths to 26 px (`bar_w = 26`, ending at X=63), eliminating graphical overlap of the bar over the life digit when the player exceeds 100 HP (3-digit values starting at X=70).

### Removed
- **Obsolete Font Cleanup (`assets/fonts/Minimal4.ttf`)**:
  - Removed the previous font file after completing migration to `golden-apple.ttf`.

---

## [0.17.0] - 2026-09-18

### Added
- **Victory Screen (`VictoryState`)**:
  - Cinematic victory screen triggered after defeating the final boss The Harvester in the Grand Pyramid (`big_room`).
  - Player ascension and levitation animation with victory title and ceremonial flash in `UnlockState`.
  - Final stat card showing total playtime (`playtime`), map exploration percentage (`exploration`), and clean return to main menu with `[ENTER]`.
  - Automatic checkpoint save on run completion.

### Changed / Improved
- **Save Slot UI and Metadata (`SlotSelectState.py` and `PlayState.py`)**:
  - Correct unpacking of Gale metadata (`extra["metadata"]`) to display real save info instead of defaults (12% and 00m 00s).
  - Redesigned slot labels: now shows zone formal name (`Central Zone`, `West Abyss`, `Past Sanctuary`, `Grand Pyramid`, etc.), active form count (`Forms: X/3`), accumulated playtime, and real exploration %.
  - Backward compatibility via data resolution for saves created previously.
- **Lava Hazard HUD Optimization (`RisingHazard.py`)**:
  - The lava escape HUD indicator now shows exclusively in the vertical map (`subida`), hidden in zones with static magma pools such as `sala_past`.

### Fixed
- **Residual Lava Sound Loop (`LavaShower.py` and `ArenaManager.py`)**:
  - Fixed the infinite `lava-shower` audio loop (`lava_boss.wav`) that played periodically every 2-3 seconds during the entire run.
  - `LavaShower` now starts in inactive state and does not reschedule timers outside the cultist priest battle.
  - Safe stop and cleanup of lava sound timers and channels when bosses are defeated and on room transitions (`PlayState.change_room`).

---

## [0.16.0] - 2026-09-17

### Added
- **Full Soundscape Integration (SFX and Tracks in `settings.SOUNDS`)**:
  - **UI and Navigation**: `change` and `enter` for interactive navigation and confirmation in menus. Tactile `paper-unfold` (`unfold_map.mp3`) and `paper-fold` (`fold_map.wav`) effects when opening and closing the paper UI in `MapState` and `PauseState`.
  - **Player Abilities and States**: `jump`, `morph-dash`, `change-skin`, `on-land`, `sword`, `slash-hit`, `sword-dash`, `mage-attack`, `mage-special`, `morph-fire`, `morph-power`, `phase_shift_past`, `phase_shift_future`, `player-death`, `hit-player`, `heart`, `unlock-state`.
  - **Enemies and Bosses**: `enemy-hurt`, `enemy-death`, `shield-active`, `boss-wind-spell`, boss music tracks (`boss_survive`, `giant_boss`, `final_boss`), and `arena-cleared` victory fanfare.
  - **World and Environment**: `save`, `open`, `close`, `rock-crack`, `rock-smash`, `lava`, `lava-shower`, `saw-hazard`.

### Changed / Refactored
- **Game Over Screen Redesign with Save Loading (`GameOverState.py` and `SlotSelectState.py`)**:
  - Replaced *"Continue from last altar"* with *"Load Save"*.
  - Smooth navigation to `SlotSelectState` in load mode (`from_game_over=True`), letting the player select any of their 3 save slots.
  - Support for canceling back to Game Over with `[P]` or `[Backspace]`.
  - Full state stack flush (`while len(self.state_machine.states) > 0: self.state_machine.pop()`) on load to eliminate zombie states and prevent memory leaks.

### Fixed
- **Immediate Lava Hazard Stop on Death (`DeathState.py` and `settings.py`)**:
  - Forced immediate stop of looping sounds `lava`, `lava-shower`, and `saw-hazard` in `DeathState.enter()`.
  - Safe `lava` stop on entering `InactiveState` and `lava-shower` stop on `LavaShower.reset()` and `settings.stop_all_music()`.
- **Clean Music Cut When Returning to Main Menu (`TitleState.py`, `GameOverState.py`, `ChronoBlight.py`)**:
  - Automatic stop of any active music channel and persistent ambient hazards on entering `TitleState.enter()` or resetting the stack with `_reset_to_title()`.

---

## [0.15.0] - 2026-09-17

### Added
- **Modern Animated Paper UI System (Humble Gift - Paper UI System v1.1)**:
  - **Unfold/Fold Animation (`PauseState` and `MapState`)**: Vertical scroll-open with `out_back` bounce easing on open (0.24s) and `in_back` anticipation on close (0.16s). Dynamic paper drop shadow scaling with the animation progress.
  - **Animated Living Fog in the World Map**: Unexplored rooms feature continuous diffuse fog via sinusoidal waves and floating hatch lines simulating live mist. Floating `?` sign with gentle levitation.
  - **Player Radar Pulse (`MapState`)**: Player position marker enriched with expanding concentric radar rings that fade progressively.
  - **Smooth Lerp Cursor**: Selection frame glides smoothly between rooms in the World Map (`dt * 20.0`). Interactive cursor with smooth transition in Pause Menu.
  - **Redesigned Pause Menu with Interactive Buttons and Sub-screen**: Interactive framed options: `RESUME`, `WORLD MAP`, `CONTROLS & FORMS`, and `MAIN MENU`. Detailed `CONTROLS & FORMS` sub-screen with button guide for all transformations and phase-shift mechanics. Direct access to the World Map from the pause menu.

---

## [0.14.0] - 2026-09-16

### Added
- **Full World Map Screen (`src/states/game/MapState.py`)**:
  - Instant access at any time via `[M]` key.
  - **Humble Gift Scroll Aesthetics**: Warm parchment frame (`#eebd8a`), double dark ink border (`#2c1e28`), and diamond filigrees at corners.
  - **Fog for Unexplored Rooms**: Unvisited rooms displayed as dark silhouettes with fog hatch and central `?`.
  - **Visited Rooms and Points of Interest (POIs)**: Discovered rooms rendered with crisp outline and distinctive mini-icons (save altar, crumbling block, boss faces with `X` after defeat, monolith/obelisk, lava drop, final skull).
  - **Player Position Beacon**: Pulsing real-time marker showing current room.
  - **Bottom INFO Card**: Detail box exposing room icon, title, and description/status.
  - **Arrow Key Exploration**: Navigate with `[↑/↓/←/→]` to inspect any connected room on the map.
- **Interactive Death / Game Over Menu (`src/states/game/GameOverState.py`)**:
  - Replaced automatic title return with a 2-option menu: *Continue from last altar* and *Return to main menu*.
- **Exploration Persistence (`visited_rooms`)**:
  - Explored room tracking in `PlayState` synced with `SaveManager`.

---

## [0.13.0] - 2026-09-16

### Added
- **Dynamic Door Blockers in Tiled Maps (`assets/tilemaps/`)**:
  - `subida.json`: Lower entry blocker with `requires_event="subida_cleared"`.
  - `sala_past.json`: Survival arena blocker with `requires_event="survival_boss_defeated"`.
  - `sala_future.json`: Cultist boss room blocker with `requires_event="boss_cultist_defeated"`.

### Changed / Refactored
- **Removal of Invisible Walls and Hardcoded Procedural Barriers**:
  - `ArenaManager.py`: Full removal of procedural laser field rendering, pulse logic, `barrier_active`, `barrier_rect`, and forced player push.
  - `RisingHazard.py`: Removed procedural descending iron bars, surface, and vertical gate collision logic.
  - `Room.py`: `solid_blockers` initialization during `__init__` and reactive invocation in `ArenaManager.on_unlock_finished()` and `EscapedState.enter()` for instant door opening on challenge completion.

---

## [0.12.0] - 2026-09-16

### Added
- **Form Unlock Progression System and Cinematic (`src/states/entity/player/UnlockState.py`)**:
  - Dedicated form unlock state with cinematic animation: soft player levitation via Gale cubic easing, radiant halo flash, expanding circular shockwave, dust particle burst, fall to ground, and styled top banner revealing the unlocked form.
  - Room entry/exit locked during the animation to guarantee cinematic integrity.
- **Form and World Event Unlocks**:
  - **Swordmaster form (`sword`)**: Unlocked by completing the survival challenge in `sala_past`. Dramatic delay after combat before the cinematic begins; escape elevator revealed only after the transformation completes.
  - **Beast Morph form (`morph`)**: Unlocked in the corner room (`middle`) after successfully completing the vertical escape challenge in `subida`.
- **Dynamic Door and Passage Blockers (`src/world/Room.py`)**:
  - Temporary barrier system via Tiled rectangles with custom `requires_event` / `event` properties. Automatic procedural tiling with brick textures (`destructible_block`), blocking passage with solid AABB collisions in 4 directions until the event is cleared. Instant visual and physical removal when the event is registered in `cleared_events`.

### Changed / Refactored
- **Persistence Centralization and Encapsulation (SRP)**:
  - Created `PlayState.save_game_checkpoint()` centralizing save state packaging and metadata.
  - Created `Player.restore_all_forms()` decoupling `Altar.py` from direct dictionary/property access.
  - Refactored `Altar.interact()` to delegate save and restore to their respective owners.
- **Canonical Form Controls and HUD**:
  - Canonical cycle order: `Mage → Swordmaster → Morph`.
  - `[Q]` rotates left (toward Mage), `[E]` rotates right (toward Morph).
  - Adaptive HUD dynamically listing unlocked forms in strict canonical order.

### Optimized
- **Eliminated Double Player Render**: Removed redundant `self.player.render()` call in `PlayState.render()`, fully delegating entity rendering to `Room.render()`.
- **GC Pressure Prevention**:
  - `PhaseShiftState.py`: Pre-allocated and reused `_RING_SURF` full-screen surface, avoiding 400×225 px allocations at 60 FPS.
  - `RisingHazard.py`: Pre-allocated `_gate_p_surf` (3×3 px), eliminating thousands of allocations per second in the draw loop.

### Fixed
- **Strict Maximum Health Cap for Mage (`Player.py`)**: Implemented strict clamp in `health` and `mana` setters bound to `self.MAX_HEALTH` and `self.MAX_MANA`. Automatic health adjustment on form switch to prevent the Mage from keeping higher HP from other forms. Fixed load order in `PlayState.enter()` to initialize skin before restoring health.

---

## [0.11.0] - 2026-09-16

### Added
- **Save and Restore Altars (`src/world/Altar.py`)**: Interactive ancient monument with animated obelisk graphics. Activated with `[↑]` with a visual prompt above the player. On activation: plays its ignition animation, fully heals all forms to 100% HP and Mana, revives downed forms, and saves state to the active slot via `SaveManager`.
- **Save Slot System and Main Menu (`src/states/game/SlotSelectState.py` and `TitleState.py`)**: Interactive menu with *New Game*, *Load Game*, and *Quit* options. 3-slot selector with save details. Supports new game, load, overwrite confirmation modal, and slot deletion with `[X]`.
- **Collectible Health Orbs (`src/world/HealthOrb.py`)**: 25% drop chance on common enemy death. Physics with gravity, soft floor bounce, and +20 HP recovery on contact with floating text.
- **Event and Challenge Persistence**: `cleared_events` registered in the `.sav` file. Prevents boss respawns (Void High Priest in `sala_future`) and already-cleared parkour traps (`subida`).

### Changed / Fixed
- **Input Mapping and Menu Navigation**: Added `KEY_DOWN` (`"down"`) and `KEY_BACKSPACE` (`"back"`) in `settings.py`. Hierarchical `ESC` handling in `ChronoBlight.py`.
- **Architectural Relocation**: Moved `HealthOrb` from `src/entities/` to `src/world/` to respect the separation between state-machine actors and collectible objects.

---

## [0.10.0] - 2026-09-15

### Added
- **Elevator System (`src/world/Elevator.py`)**: Interactive elevator with open/closed door animations. Transports the player by making them invisible during transit; arrives, releases the player, waits 1 second with doors open, then permanently disappears upward.
- **Combat Resolution Module (`src/world/combat.py`)**: Full extraction of damage evaluation logic, attack impact (melee and magic), and contact damage from `Room.py` into a standalone `CombatResolver` class.

### Changed / Refactored
- **`Room.py` Cleanup Refactor**: Removed abundant duplicated code by centralizing logic with `_parse_props` and `_spawn_enemy`. Simplified collision layer mapping with clean module-level dictionaries (`_PHASE_LAYERS`). Removed orphaned arguments and variables in traps and spawners.
- **Boss State Machine**: Restructured boss state packages, moving boss-specific attacks to their respective entity folders (e.g., `boss/cultist/`) for better decoupling.

### Optimized
- **Memory Thrashing Elimination in Rendering**:
  - *Projectiles*: Pre-allocated `_trail_surf` cache surface. Avoids creation of over 3000 `pygame.Surface` instances per second when drawing enemy bullet trails.
  - *Player Magic*: Introduced lazy cache (`_flame_cache`) for Mage area-attack flames, avoiding the intensive `pygame.transform.scale` call 60 times per second.

---

## [0.9.0] - 2026-09-14

### Added
- **Boss Hierarchy and System (`src/entities/Boss.py` and `src/states/entity/boss/`)**:
  - Dedicated `Boss` class extending `Enemy`, encapsulating phase management, arcane shields, immunity timers, and special projectiles.
  - Decoupled FSM for bosses: `BossBaseState`, `BossIdleState`, `BossChaseState`, `BossAttackState`.
  - Explicit separation of `BOSS_DEFS` and `ENEMY_DEFS` in `src/definitions/entity.py`.
- **Multi-Phase Arena Combat (`src/world/ArenaManager.py` and `src/world/LavaShower.py`)**:
  - Arena room system with magic barrier sealing the exit and ambient lava shower.
  - 3 combat phases with dynamic minion waves: Phase 1 (boss shielded, ground shockwaves + minions), Phase 2 at 70% HP (Void Orb with homing AI + new wave), Phase 3 at 30% HP (simultaneous shockwave + orb + Root Golem).
  - Protective shield active while minions are alive; breaking it allows damaging the boss.
- **Ability Effects and Spritesheets**: `void_orb.png`, `ground_shockwave.png`, internal projectile FSM (`spawn → travel → despawn`) with dynamic horizontal flip, and homing Void Orb AI (5s duration with particle trail).

### Changed / Refactored
- **Asset Structural Reorganization (`assets/graphics/`)**: New folder taxonomy: `player/{sword,morph,mage}/`, `entity/enemies/`, `entity/bosses/`, `effects/`. Updated `settings.TEXTURES` and frame generators in `src/definitions/frames.py`.
- **`Enemy.py` Decoupling**: Purged boss-specific logic from `Enemy.py`, `EnemyAttackState.py`, and `EnemyChaseState.py`, keeping regular enemy states clean and focused on standard AI.

---

## [0.8.0] - 2026-09-14

### Added
- **Falling Trap System (`src/world/FallingTrap.py`)**: Phase-locked falling hazards (`green` or `red`). Player X-proximity detection with 0.45s warning/tremor before gravity fall. Direct tileset tile rendering via Tiled custom properties (`tile_col`, `tile_row`).
- **Rotating Saw Blades and Shurikens (`src/world/SawHazard.py`)**: Contact damage obstacle with continuous animated rotation. Configurable horizontal and vertical patrol axis, distance, and speed from Tiled layers.
- **Dynamic Enemy Spawning from Tiled (`src/world/Room.py`)**: Auto-detection and creation of any enemy placed in Tiled object layers (`spawns`, `spwans`, `enemies`). Multi-layer solid collision assignment for enemies matching their temporal phase.

### Changed / Refactored
- **Dead Code Cleanup and Deduplication**: Removed unused constants and orphaned textures in `settings.py`. Created `EntityBaseState.handle_buffered_inputs()` to unify attack, special, dash, and jump buffer handling across `IdleState`, `WalkState`, `JumpState`, and `FallState`. Unified damage popups (`_spawn_popup()`), spawn-point resets (`_reset_player_to_spawn()`), and enemy collision mass table in `Room.py`.
- **Rising Lava/Magma Integration (`src/world/RisingHazard.py` and `src/states/hazard/RisingState.py`)**: Read initial Y position from Tiled `fire` layer object. Adjusted upper ascent limit to stop exactly 2 tiles from the map ceiling.

---

## [0.7.0] - 2026-09-13

### Added
- **Tiled Map Room System (`assets/tilemaps/` and `src/world/Room.py`)**:
  - Native integration with Tiled JSON maps via `gale.tilemap.load_tiled_map`, supporting arbitrary-dimension levels with multi-layer tiles and objects.
  - 5 new rooms: `abismo_1.json` (800×384 px), `abismo_fixed.json`, `sala_past.json` (Past era, green), `sala_future.json` (Future era, red), `subida.json` (vertical climb, 320×640 px).
- **Multi-Layer Physics and Collision System (`src/world/tile_collision.py`)**: `collision_type_in_layers()`, `move_and_collide_layers()`, `check_on_ground()`. Precise AABB sweep on decoupled X and Y axes for solid tiles and one-way platforms. Dynamic active layers per temporal phase: `["ground", "green_ground"]` in Past, `["ground", "red_ground"]` in Future.
- **Ghost Platforms and Phase Rendering**: Semitransparent rendering (`alpha = 75`) of the opposite temporal plane's layers, letting the player anticipate terrain before performing a Phase Shift. Tiled flip flags support (bits 31, 30, 29). Visible tile culling via `_visible_tile_range()`.
- **Dual Parallax Backgrounds**: `abismo_1_past/future`, `abismo_past/future`, `sala_past/future`, `subida_past/future` in `settings.TEXTURES`. Soft parallax scrolling (factor `0.4`) with automatic horizontal repetition for rooms wider than the background.
- **Particle Effects and Abyss Fall**: Atmospheric floating particles with sinusoidal wind drift colored by active phase. Dust particles on jump (`on_jump_effect`) and landing (`on_land`). Abyss fall detection at `MAP_HEIGHT - 24`: 20 spike damage, screen shake, respawn at spawn point.
- **Dynamic Spawn Point Resolution (`Room._extract_spawn_point`)**: Cascade detection: explicit parameter → Tiled objectgroup (`spawn`, `player_spawn`, `start`) → map properties → default coordinates.

### Changed / Refactored
- **Entity Tilemap Integration (`src/entities/Entity.py`)**: Added `tilemap` and `active_collision_layers` attributes to the base `Entity` class. Adapted `_apply_movement_and_collision()` to use the multi-layer collision engine. Redesigned `render_outline()` with double-pass technique: soft outer halo (alpha 65, 2px offset) + crisp inner outline.
- **Player Visual Palette**: Increased brightness and opacity on neon outline colors.
- **Dedicated Fall Animation (`FallState.py`)**: `FallState` now plays the specific `"fall"` animation instead of reusing the `"jump"` cycle.

---

## [0.6.0] - 2026-09-12

### Added
- **World Simulation Layer (`src/world/Room.py`)**: New `Room` class inspired by `06-princess` (`Dungeon`/`Room`) and `05-super_martian` (`GameLevel`) architectures, encapsulating level geometry (78×13 tiles / 1248×208 px), ambient rendering (phase-based sky gradient, floor, grid, walls), enemy lifecycle with 3s respawn queue, and solid separation physics.
- **Screen Shake and Gale's Official Camera (`gale.camera.Camera`)**: Native `gale.camera.Camera` integration with automatic map bounds clamping. Dynamic screen shake (`camera.shake(...)`) on melee hits, sword combos, Mage fire pillars, and contact damage received.
- **Game Over Screen (`src/states/game/GameOverState.py`)**: New state stacked on `StateStack` with reddish ambient darkening, triggered when the player loses all forms (`player.is_dead()`), allowing clean restart with `Enter`.
- **Decoupled Enemy State Machine with Smart Jump (`src/states/entity/enemy/`)**: Atomic Gale states: `EnemyPatrolState`, `EnemyChaseState`, `EnemyAttackState`, `EnemyHitState`, `EnemyDeathState`. Smart 2D chase with jump: enemies configured with `can_jump` will jump toward the player if on a higher platform or airborne.

### Changed / Refactored
- **Radical `PlayState.py` Simplification**: Reduced from 430+ lines to ~60, transforming it into a pure state orchestrator managing only global inputs (pause, phase shift, form change), `GameOverState` transitions, and HUD projection.
- **Game State Machine Redesign**: `TitleState` centered with golden shadowed title, styled subtitle, blinking *"Press ENTER to start"* animation, and full controls legend. `PauseState` and `PhaseShiftState`: overlay surfaces pre-created in `enter()`, eliminating `pygame.Surface(SRCALPHA)` creation at 60 FPS. Fixed coordinates that placed text off-screen (−40 px).
- **Pixel-Crisp Font Rendering (`settings.py`)**: Font helper with `antialias=False` for the official pixel-art font, eliminating FreeType blur at native 320×180 resolution.
- **Centralized Horizontal Movement (`src/states/entity/EntityBaseState.py`)**: `apply_horizontal_movement()` shared between `WalkState`, `JumpState`, `FallState`, and `AttackState`, eliminating acceleration/deceleration code duplication.
- **Camera Compatibility (`src/world/Camera.py`)**: Adapted as a direct extension of `gale.camera.Camera` preserving backward compatibility for `get_offset()`.

### Fixed
- **Static Walk Animation (`Player.change_animation`)**: Guard clause to avoid restarting identical animations already playing, allowing all three forms to walk and run fluidly in both phases.
- **Attack Damage Window Sync (`Player.is_attack_active`)**: Calibrated windup vs actual impact frames: enemy no longer receives damage on frame 0; damage fires when the weapon visually connects. Sword second-hit combo support with independent `swing_id` and finisher damage (`hit2_damage: 20`).
- **State Leak Prevention on Interrupted Abilities**: Forced `area_active` cleanup in `AttackSpecialState.exit()` if the Mage takes damage or dies during flame channeling. Velocity cleared in `DashState.exit()` on interruptions.

### Removed
- **Dead Code and Duplicate Files Purge**: Removed `PlayerCommands.py`, 8 duplicate/orphaned files in `src/states/entity/player/`, unused entity methods (`Entity.heal()`, `Player.toggle_skin()`, `Player._get_anim_dict()`, `Entity._anim_idx`), and unused enemy surfaces.

---

## [0.5.0] - 2026-09-12

### Added
- **Full Enemy System and AI (`src/entities/Enemy.py` and `src/states/entity/enemy/`)**:
  - Base `Enemy` entity extending `Entity` with vision range detection, de-aggro range (abandons chase if player moves far away), and hostility cease when the player is defeated (returns to patrol).
  - Modular decoupled FSM: `EnemyBaseState`, `EnemyPatrolState`, `EnemyChaseState`, `EnemyAttackState`, `EnemyHitState`, `EnemyDeathState`.
  - **Enemy Separation Physics**: Mutual horizontal collision and repulsion to prevent enemies from overlapping when grouping.
- **8 Enemy Types Integrated and Calibrated**:
  - `skeleton_sword` (Past/Green): 45 frames, two melee attacks.
  - `monster_eyes` (Future/Red): Bite and claw charge, patrol and chase with range limit.
  - `goblin` (Past/Green): Double dagger combo.
  - `crown` (Past/Green): Quick peck, jump animation, low flight.
  - `big_monster` (Future/Red): Body stomp, synchronized `boss_vines` ground hazard (`2a`, `2b`, `2c`, `miss`).
  - `monster2` Shadow Lurker (Past/Green): 48×48 frames, two shadow attack variants.
  - `monster3` Horned Imp (Future/Red): 64×64 frames with full animations.
  - `cultist_priest` (Future/Red): 26 individual frames, 200×200 canvas, feet at `feet_y = 182`.
- **Official Gale Command Pattern (`src/commands.py`)**: Full Command Pattern with `CommandBindings`. Actions: `JUMP`, `STOP_JUMP`, `MOVE_LEFT`, `STOP_MOVE_LEFT`, `MOVE_RIGHT`, `STOP_MOVE_RIGHT`, `LOOK_UP`, `STOP_LOOK_UP`, `RUN`, `STOP_RUN`, `ATTACK`, `SPECIAL_ATTACK`, `DASH`, `NEXT_FORM`, `PREV_FORM`, `SHIFT_PHASE`.
- **Automated Physics and Aerial Ability Tests**: Headless validation suite (`dummy` video driver) for gravity isolation, dash vertical lock, and state transition verification.

### Changed
- **Combat and Player Invulnerability Adjustments**: Swordmaster special attack (`AttackSpecialState.py`) now grants temporary invulnerability during execution and a brief window after, preventing damage interruption mid-attack. Improved damage frame sync: `HitState` animation fires exactly when the attack visually impacts.
- **Attack Hitbox Debug Cleanup**: Removed debug visual hitbox frames from the combat display.

### Removed
- **Temporary Spritesheet Cleanup**: Removed combined synthetic sprite sheets (`big_monster.png`, `cultist_priest.png`, `skeleton_sword.png`) after migrating to modular original frame strips.

### Fixed
- **Morph Aerial Dash Height Lock (`src/states/entity/player/DashState.py`)**: Forced `vy = 0.0` on enter and during update. Eliminated residual upward inertia causing unintended elevation when dashing mid-jump. Clean transition to `FallState` after animation with gravity resuming only post-dash.
- **Swordmaster Special Attack Air Suspension (`src/states/entity/player/AttackSpecialState.py`)**: `has_gravity = False` and `vy = 0.0` during animation. Swordmaster stays suspended without losing height while charging and executing the slash; transitions to `FallState` only on completion.
- **Morph Form Involuntary Dash Prevention**: Immediate `dash_requested` flag discard in all states when the active form has no dash (Mage and Swordmaster). Explicit buffer flush in `Player.change_skin()`.
- **Mage Special Attack Restoration**: Reconnected `on_update` (`_mage_special_update`) and `on_finish` (`_mage_special_finish`) callbacks in `AttackSpecialState`, enabling progressive deployment of the 3 flame circles.
- **Variable Jump Height and Sensitivity**: Removed premature vertical velocity clipping in `JumpState.py`, restoring the natural full jump parabola with authentic variable jump support via `jump_held`.

---

## [0.4.0] - 2026-09-12

### Changed / Refactored
- **Base Architecture Inspired by *Ultimate Fantasy* (`Entity` vs `Player`)**:
  - Complete decoupling of generic physics logic from player-specific logic.
  - **`src/entities/Entity.py`**: New generalized base class managing position (`x`, `y`), velocities (`vx`, `vy`), bounding boxes (`hitbox`), state machine (`StateMachine`), conditional gravity (`apply_gravity`), animation timer, and map/floor boundary collisions.
  - **`src/entities/Player.py`**: Specialized player subclass managing skin transformations (`sword`, `morph`, `mage`), chromatic phases (`red`, `green`), HP/MP stats, cooldowns, combo buffers, and the command system.
- **State Machine Modularization Inspired by *Super Martian***:
  - Replaced the monolithic `PlayerAirborneState` with two atomic aerial states: `JumpState.py` (upward impulse, variable jump, double jump) and `FallState.py` (free-fall, horizontal control, landing).
  - Standardized state file names in `src/states/entity/player/` (`IdleState`, `WalkState`, `JumpState`, `FallState`, `DashState`, `AttackState`, `AttackSpecialState`, `HitState`, `DeathState`).
  - Each state now interacts cleanly through intent flags (`jump_requested`, `attack_requested`, `dash_requested`, etc.).

---

## [0.3.0] - 2026-09-11

### Added
- **HUD and Persistent UI (`src/ui/HUD.py`)**: Proportional HP and MP bars with outlines and dynamic fill. Custom pixel-art font integration (`assets/fonts/Minimal4.ttf`). Numeric HP/MP indicators aligned with bars. Active form avatar with themed border. Cooldown visual indicator (5-second) on form switch: radial arc progress around the icon.
- **Green Phase Color Palette**: Replaced original blue variant with green to sync with the game's temporal phase (`Mage_green.png`, `Morph_green.png`, `sword_green.png`, `flame_green.png`). Added `Entity.render_outline` for maximum character visibility on dark backgrounds.
- **Combo and Directional Attack System**: Upward attack (`is_looking_up` + attack button). Combo buffer window in `AttackState` to chain the second sword hit before the first phase animation ends.

### Changed
- **Animation Timing Adjustments (`src/definitions/entity.py`)**: Modified animation intervals for better visual legibility in fast attacks and sword combos.

---

## [0.2.0] - 2026-09-11

### Added
- **Centralized Entity Mapping (`src/definitions/entity.py`)**: Extracted all constants, hitboxes, physics parameters (`GRAVITY = 850.0`, `WALK_SPEED = 90.0`, `RUN_SPEED = 140.0`, `JUMP_VELOCITY = -320.0`), and animation dictionaries out of `settings.py`. Base stat definitions per character (`health`, `max_health`, `mana`, `max_mana`, mana costs, damage). Modular action callbacks: `_sword_special_finish`, `_mage_special_update`, `_mage_special_finish`, `_morph_dash`.
- **Entity Base States (`src/states/entity/EntityBaseState.py`)**: Standard architecture for entity states supporting per-state flags such as `has_gravity`.
- **Damage and Death States (`HitState`, `DeathState`)**: Damage handling with knockback and recovery time. Zero-health detection with transition to death state or form rotation.

### Fixed
- **Animation End Detection**: Implemented `is_animation_finished()` with fallback timer (`fallback_duration`) to prevent single-cycle animations from stalling indefinitely.
- **Movement and Flip (`facing`)**: Fixed static sprite when moving left-to-right; dynamic sprite orientation based on `move_direction`.
- **Aerial Attacks and Horizontal Inertia**: Allowed basic attacks and dashes while airborne without freezing the game.

---

## [0.1.0] - Project Start

### Added
- **Game Base Structure with Gale Engine**: Initial window setup in `main.py` and `settings.py` (320×180 base resolution, scaled to 1280×720). `ChronoBlight.py` initialization managing the game lifecycle. Texture, spritesheet, and frame clip loading (`assets/graphics/`). Main game state machine (`PlayState`, `TitleState`, `PauseState`, `PhaseShiftState`). Smooth player-follow camera (`src/world/Camera.py`). Initial prototype of the three player transformations: Sword (`Sword`), Mage (`Mage`), and Morph form (`Morph`).
