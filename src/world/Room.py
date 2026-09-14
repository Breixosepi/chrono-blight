"""
Chrono Blight - World Room Component
Integrates Tiled TileMaps, dual-phase backgrounds, ghost platforms, and entity management.
"""

from typing import Any, Dict, List, Optional, Tuple
import json
import math
import pathlib
import random
import pygame

from gale.camera import Camera
from gale.text import render_text
from gale.tilemap import TileMap, load_tiled_map

import settings
from src.definitions import entity as entity_defs
from src.entities.Player import Player
from src.entities.Enemy import Enemy
from src.world.FallingTrap import FallingTrap
from src.world.SawHazard import SawHazard
from src.world.RisingHazard import RisingHazard


_ENEMY_MASS: Dict[str, float] = {
    "big_monster":    3.5,
    "cultist_priest": 2.5,
    "monster3":       1.4,
    "skeleton_sword": 1.2,
    "monster_eyes":   1.0,
    "goblin":         0.9,
    "monster2":       0.85,
    "crown":          0.8,
}


class Room:

    TILE_SIZE: int = settings.TILE_SIZE
    DEFAULT_SPAWN_X: float = 48.0
    DEFAULT_SPAWN_Y: float = 220.0

    def __init__(
        self,
        map_name: str = "sala_future",
        spawn_x: Optional[float] = None,
        spawn_y: Optional[float] = None,
        player: Optional[Player] = None,
    ) -> None:
        self.map_name = map_name
        map_file = settings.BASE_DIR / "assets" / "tilemaps" / f"{map_name}.json"

        # Load raw map JSON for object layers and custom properties
        with open(str(map_file), "r", encoding="utf-8") as f:
            self.map_data = json.load(f)

        self.tilemap: TileMap = load_tiled_map(str(map_file))

        self.MAP_COLS = self.tilemap.cols
        self.MAP_ROWS = self.tilemap.rows
        self.MAP_WIDTH = self.tilemap.pixel_width
        self.MAP_HEIGHT = self.tilemap.pixel_height

        # Dynamic spawn resolution: parameter > object layer > map properties > default
        self.spawn_x, self.spawn_y = self._extract_spawn_point(self.map_data, spawn_x, spawn_y)

        self._preprocess_tilemap()

        self.camera = Camera(
            settings.VIRTUAL_WIDTH,
            settings.VIRTUAL_HEIGHT,
            bounds=pygame.Rect(0, 0, self.MAP_WIDTH, self.MAP_HEIGHT),
        )

        if player is None:
            self.player = Player(
                self.spawn_x,
                self.spawn_y,
                floor_y=float(self.MAP_HEIGHT),
                map_w=float(self.MAP_WIDTH),
            )
            self.player.phase = "past"
            self.player.phase_color = "green"
        else:
            self.player = player
            self.player.x = self.spawn_x
            self.player.y = self.spawn_y
            self.player.hitbox.x = int(self.spawn_x)
            self.player.hitbox.y = int(self.spawn_y)
            self.player.vx = 0.0
            self.player.vy = 0.0
            self.player.floor_y = float(self.MAP_HEIGHT)
            self.player.map_w = float(self.MAP_WIDTH)

        self.player.tilemap = self.tilemap
        self.player.active_collision_layers = self._get_active_collision_layers()

        self.camera.x = self.player.hitbox.centerx
        self.camera.y = self.player.hitbox.centery
        self.camera.update(0.0)

        self._init_enemies()
        self._init_graphics()

        self.dust_particles: list[dict] = []
        old_on_land = self.player.on_land
        def _on_player_land() -> None:
            old_on_land()
            self.spawn_dust(self.player.hitbox.centerx, self.player.hitbox.bottom, count=4)
        self.player.on_land = _on_player_land
        self.player.on_jump_effect = lambda: self.spawn_dust(self.player.hitbox.centerx, self.player.hitbox.bottom, count=4)

        # Tracking de golpes por swing
        self._hit_this_swing: set = set()
        self._flame_hits: set = set()
        self._prev_attack_state: bool = False
        self.damage_popups: list[dict] = []
        self.respawn_queue: list[dict] = []
        self.rising_hazard: Optional[RisingHazard] = (
            RisingHazard(self) if self.map_name == "subida" else None
        )
        self.falling_traps: list[FallingTrap] = []
        self.saw_hazards: list[SawHazard] = []
        self._init_traps(self.map_data)

    @property
    def camera_offset(self) -> tuple[float, float]:
        ox, oy = self.camera.offset
        return (round(ox), round(oy))

    def _init_traps(self, map_data: dict) -> None:
        """Parsea la capa 'traps' y crea las trampas y sierras correspondientes."""
        trap_layer = next((l for l in map_data.get("layers", []) if l.get("name") == "traps"), None)
        if trap_layer and "objects" in trap_layer:
            for obj in trap_layer["objects"]:
                props = {p.get("name"): p.get("value") for p in obj.get("properties", []) if isinstance(p, dict)}
                
                t_name = obj.get("name", "") or str(props.get("name", ""))
                t_type = obj.get("type", "") or obj.get("class", "") or str(props.get("type", ""))
                combined_id = f"{t_name} {t_type}".lower()
                
                # 1. Sierras y Shurikens
                if "saw" in combined_id or "shuriken" in combined_id:
                    h_type = "shuriken" if "shuriken" in combined_id else "saw"
                    phase = "green" if "green" in combined_id else ("red" if "red" in combined_id else "neutral")
                    patrol_dist = float(props.get("patrol_dist", 0.0))
                    axis = str(props.get("axis", "y"))
                    speed = float(props.get("speed", 50.0))
                    damage = int(props.get("damage", 15))
                    
                    self.saw_hazards.append(
                        SawHazard(
                            self,
                            float(obj.get("x", 0.0)),
                            float(obj.get("y", 0.0)),
                            hazard_type=h_type,
                            phase=phase,
                            patrol_dist=patrol_dist,
                            axis=axis,
                            speed=speed,
                            damage=damage,
                        )
                    )
                    continue

                # 2. Falling Traps (pasado/futuro)
                phase = "green" if "green" in combined_id else ("red" if "red" in combined_id else None)
                if not phase:
                    continue
                
                tile_col = int(props.get("tile_col", props.get("col", 1)))
                tile_row = int(props.get("tile_row", props.get("row", 2)))
                
                width = int(obj.get("width", 16))
                height = int(obj.get("height", 16))
                obj_x = float(obj.get("x", 0.0))
                obj_y = float(obj.get("y", 0.0))
                
                self.falling_traps.append(
                    FallingTrap(
                        self,
                        obj_x,
                        obj_y,
                        phase,
                        tile_col=tile_col,
                        tile_row=tile_row,
                        width=width,
                        height=height,
                    )
                )

    def check_room_exits(self) -> Optional[Tuple[str, float, float]]:
        """Comprueba si el jugador cruza una salida configurada para esta sala."""
        from src.world.room_connections import ROOM_CONNECTIONS
        exits = ROOM_CONNECTIONS.get(self.map_name, [])
        for exit_def in exits:
            if exit_def["check"](self.player, self):
                target_x, target_y = exit_def["target_spawn"]
                return (exit_def["target_room"], float(target_x), float(target_y))
        return None

    def _extract_spawn_point(
        self,
        map_data: dict,
        override_x: Optional[float] = None,
        override_y: Optional[float] = None,
    ) -> Tuple[float, float]:
        """
        Resolves the player's initial spawn coordinates with this priority:
        1. Explicitly passed override_x / override_y
        2. Tiled object in an 'objectgroup' layer named 'spawn', 'player_spawn', 'player', or 'start'
        3. Tiled map properties 'spawn_x' and 'spawn_y'
        4. Class default (DEFAULT_SPAWN_X, DEFAULT_SPAWN_Y)
        """
        if override_x is not None and override_y is not None:
            return (float(override_x), float(override_y))

        # 1. Search object layers
        for layer in map_data.get("layers", []):
            if layer.get("type") == "objectgroup":
                for obj in layer.get("objects", []):
                    name = str(obj.get("name", "")).lower()
                    obj_type = str(obj.get("type", "")).lower()
                    if name in ("spawn", "player_spawn", "player", "start") or obj_type in ("spawn", "player_spawn"):
                        ox = float(obj.get("x", 0))
                        oy = float(obj.get("y", 0))
                        return (ox, oy)

        # 2. Search map properties
        props = {p.get("name"): p.get("value") for p in map_data.get("properties", []) if "name" in p}
        if "spawn_x" in props and "spawn_y" in props:
            return (float(props["spawn_x"]), float(props["spawn_y"]))

        if override_x is not None:
            return (float(override_x), self.DEFAULT_SPAWN_Y)

        return (self.DEFAULT_SPAWN_X, self.DEFAULT_SPAWN_Y)

    def _preprocess_tilemap(self) -> None:
        """
        Strips Tiled flip flags (bits 31, 30, 29) so that Gale tilemap collision
        and property lookups work flawlessly, while recording the flip flags
        for visual rendering.
        """
        self.flipped_tiles: Dict[Tuple[str, int, int], Tuple[bool, bool, bool]] = {}
        for layer_name in self.tilemap.layer_names():
            for r in range(self.tilemap.rows):
                for c in range(self.tilemap.cols):
                    raw = self.tilemap.get_gid(layer_name, r, c)
                    if raw > 100000:
                        fh = bool(raw & 0x80000000)
                        fv = bool(raw & 0x40000000)
                        fd = bool(raw & 0x20000000)
                        self.flipped_tiles[(layer_name, r, c)] = (fh, fv, fd)
                        self.tilemap.set_gid(layer_name, r, c, raw & 0x1FFFFFFF)

        self._tile_cache: Dict[Tuple[int, bool, bool, bool], pygame.Surface] = {}
        self._ghost_tile_cache: Dict[Tuple[int, bool, bool, bool], pygame.Surface] = {}

    def _get_tile_surface(
        self,
        gid: int,
        flip_h: bool = False,
        flip_v: bool = False,
        flip_d: bool = False,
        ghost: bool = False,
    ) -> Optional[pygame.Surface]:
        key = (gid, flip_h, flip_v, flip_d)
        cache = self._ghost_tile_cache if ghost else self._tile_cache
        if key in cache:
            return cache[key]

        tileset = self.tilemap.tileset_for_gid(gid)
        if tileset is None:
            cache[key] = None
            return None

        source_rect = tileset.rect_for(gid)
        sub = tileset.image.subsurface(source_rect)

        if flip_d:
            sub = pygame.transform.rotate(sub, 270)
            sub = pygame.transform.flip(sub, True, False)
        if flip_h or flip_v:
            sub = pygame.transform.flip(sub, flip_h, flip_v)

        if ghost:
            ghost_surf = sub.copy()
            ghost_surf.set_alpha(75)
            cache[key] = ghost_surf
            return ghost_surf

        cache[key] = sub
        return sub

    def _get_active_collision_layers(self) -> List[str]:
        if self.player.phase_color == "green":
            return ["ground", "green_ground"]
        return ["ground", "red_ground"]

    def _get_enemy_collision_layers(self, enemy: Enemy) -> List[str]:
        if enemy.phase == "green":
            return ["ground", "green_ground"]
        elif enemy.phase == "red":
            return ["ground", "red_ground"]
        return ["ground", "green_ground", "red_ground"]

    def _init_enemies(self) -> None:
        self.enemies: List[Enemy] = []
        spawn_layer_names = {"spawns", "spwans", "enemies", "enemy_spawns"}
        for layer in self.map_data.get("layers", []):
            if layer.get("name") in spawn_layer_names and "objects" in layer:
                for obj in layer["objects"]:
                    props = {p.get("name"): p.get("value") for p in obj.get("properties", []) if isinstance(p, dict)}
                    t_name = (obj.get("name", "") or str(props.get("name", ""))).lower().strip()
                    t_type = (obj.get("type", "") or obj.get("class", "") or str(props.get("enemy_type", ""))).lower().strip()
                    
                    if t_name in ("spawn", "player", "start") or t_type in ("spawn", "player", "start"):
                        continue
                        
                    enemy_type = t_name if t_name in entity_defs.ENEMY_DEFS else (t_type if t_type in entity_defs.ENEMY_DEFS else None)
                    if enemy_type:
                        x = float(obj.get("x", 0.0))
                        y = float(obj.get("y", 0.0))
                        enemy = Enemy(
                            x,
                            y,
                            enemy_type=enemy_type,
                            floor_y=float(self.MAP_HEIGHT),
                            map_w=float(self.MAP_WIDTH),
                        )
                        enemy.player = self.player
                        enemy.tilemap = self.tilemap
                        enemy.active_collision_layers = self._get_enemy_collision_layers(enemy)
                        enemy.on_hazard_hit = self._on_hazard_hit
                        self.enemies.append(enemy)

    def _on_hazard_hit(self, hazard: dict) -> None:
        self.camera.shake(2.0, 0.15)
        self._spawn_popup(
            f"-{int(hazard['damage'])}", hazard["hitbox"].centerx, hazard["hitbox"].top - 6, 0.6, (255, 60, 60)
        )

    def _create_radial_glow(self, radius: int, color_rgb: tuple, max_alpha: int = 40) -> pygame.Surface:
        surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        for r in range(radius, 0, -2):
            alpha = int(max_alpha * (1.0 - (r / radius) ** 1.5))
            pygame.draw.circle(surf, (*color_rgb, alpha), (radius, radius), r)
        return surf

    def _load_background_image(self, candidate_name: str) -> Optional[pygame.Surface]:
        """
        Dynamically loads a background surface from memory or from assets/graphics/backgrounds.
        """
        if not candidate_name:
            return None

        # 1. Look up in settings.TEXTURES
        if candidate_name in settings.TEXTURES:
            return settings.TEXTURES[candidate_name]

        # 2. Look up in assets/graphics/backgrounds
        bg_dir = settings.BASE_DIR / "assets" / "graphics" / "backgrounds"
        clean_name = pathlib.Path(candidate_name).stem
        for p in (
            bg_dir / candidate_name,
            bg_dir / f"{candidate_name}.png",
            bg_dir / f"{candidate_name}.jpg",
            bg_dir / f"{clean_name}.png",
            bg_dir / f"{clean_name}.jpg",
        ):
            if p.is_file():
                try:
                    surf = pygame.image.load(str(p)).convert_alpha()
                    settings.TEXTURES[candidate_name] = surf
                    return surf
                except Exception:
                    pass
        return None

    def _init_graphics(self) -> None:
        self.glow_surfaces = {
            "red":   self._create_radial_glow(36, (255, 100, 100), max_alpha=40),
            "green": self._create_radial_glow(36, (70, 230, 140), max_alpha=45),
        }

        # Resolve backgrounds dynamically: Tiled properties > naming convention > default fallback
        props = {p.get("name"): p.get("value") for p in self.map_data.get("properties", []) if "name" in p}
        past_bg_target = props.get("bg_past", f"{self.map_name}_past")
        future_bg_target = props.get("bg_future", f"{self.map_name}_future")

        self.bg_surfaces = {}
        for phase, bg_target, fallback_key, wash_color in [
            ("green", past_bg_target, f"{self.map_name}_past", (8, 16, 20, 130)),
            ("red", future_bg_target, f"{self.map_name}_future", (22, 10, 14, 135)),
        ]:
            raw_bg = (
                self._load_background_image(bg_target)
                or self._load_background_image(fallback_key)
                or self._load_background_image(f"abismo_1_{'past' if phase == 'green' else 'future'}")
            )
            if raw_bg:
                bg = raw_bg.copy()
                wash = pygame.Surface(bg.get_size(), pygame.SRCALPHA)
                wash.fill(wash_color)
                bg.blit(wash, (0, 0))
                self.bg_surfaces[phase] = bg

        # Ambient floating atmospheric particles (motes/embers)
        self._ambient_particles: List[Dict[str, Any]] = [
            {
                "x": random.uniform(0, self.MAP_WIDTH),
                "y": random.uniform(0, self.MAP_HEIGHT),
                "speed_y": random.uniform(-14.0, -5.0),
                "speed_x": random.uniform(-4.0, 4.0),
                "drift_timer": random.uniform(0.0, 6.28),
                "radius": random.choice([1, 1, 2]),
                "alpha": random.randint(85, 175),
            }
            for _ in range(40)
        ]
        self._particles_surface = pygame.Surface(
            (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA
        )

    def _spawn_popup(
        self,
        text: str,
        x: float,
        y: float,
        timer: float,
        color: tuple,
    ) -> None:
        self.damage_popups.append({"text": text, "x": x, "y": y, "timer": timer, "color": color})

    def _reset_player_to_spawn(self) -> None:
        self.player.x = self.spawn_x
        self.player.y = self.spawn_y
        self.player.vx = 0.0
        self.player.vy = 0.0
        self.player.hitbox.x = int(self.spawn_x)
        self.player.hitbox.y = int(self.spawn_y)
        self.player.change_state("idle")

    def _handle_player_fall_hazard(self) -> None:
        if self.player.state_name == "death":
            return

        self.player.take_damage(20)
        self.camera.shake(4.0, 0.25)
        self._spawn_popup("-20 (SPIKES)", self.player.hitbox.centerx, self.player.hitbox.top - 10, 0.8, (255, 50, 50))

        if self.rising_hazard is not None:
            self.rising_hazard.reset()

        if self.player.state_name != "death":
            self._reset_player_to_spawn()

    def _handle_player_rising_hazard(self) -> None:
        if self.player.state_name == "death":
            return

        self.player.take_damage(25)
        self.camera.shake(5.0, 0.3)
        self._spawn_popup("-25 (HAZARD)", self.player.hitbox.centerx, self.player.hitbox.top - 10, 0.9, (255, 60, 40))

        if self.rising_hazard is not None:
            self.rising_hazard.reset()

        if self.player.state_name != "death":
            self._reset_player_to_spawn()

    def spawn_dust(self, x: float, y: float, count: int = 4) -> None:
        for _ in range(count):
            self.dust_particles.append({
                "x": x + random.uniform(-5.0, 5.0),
                "y": y + random.uniform(-1.0, 1.0),
                "vx": random.uniform(-30.0, 30.0),
                "vy": random.uniform(-14.0, -4.0),
                "life": 0.22,
                "max_life": 0.22,
                "radius": random.choice([1, 2]),
            })

    def update(self, dt: float) -> None:
        # Update ambient particles drifting with wind
        for p in self._ambient_particles:
            p["drift_timer"] += dt * 1.5
            p["y"] += p["speed_y"] * dt
            p["x"] += (p["speed_x"] + math.sin(p["drift_timer"]) * 6.0) * dt
            if p["y"] < 0:
                p["y"] = float(self.MAP_HEIGHT)
                p["x"] = random.uniform(0, self.MAP_WIDTH)
            elif p["x"] < 0:
                p["x"] = float(self.MAP_WIDTH)
            elif p["x"] > self.MAP_WIDTH:
                p["x"] = 0.0

        # Update jump/land dust particles
        for d in self.dust_particles[:]:
            d["life"] -= dt
            d["x"] += d["vx"] * dt
            d["y"] += d["vy"] * dt
            if d["life"] <= 0.0:
                self.dust_particles.remove(d)

        self.player.active_collision_layers = self._get_active_collision_layers()
        self.player.update(dt)

        for trap in self.falling_traps:
            trap.update(dt)

        for saw in self.saw_hazards:
            saw.update(dt)

        # Update camera following player smoothly
        self.camera.x = self.player.hitbox.centerx
        self.camera.y = self.player.hitbox.centery
        self.camera.update(dt)

        # Check spikes / bottom fall hazard in pit rooms
        if self.rising_hazard is None and self.player.hitbox.bottom >= (self.MAP_HEIGHT - 4):
            self._handle_player_fall_hazard()

        # Gate collision & rising hazard
        if self.rising_hazard is not None:
            if self.rising_hazard.gate_current_y >= 570.0:
                if self.player.hitbox.left < 28 and self.player.hitbox.bottom >= 540:
                    self.player.x = 28.0
                    self.player.hitbox.left = 28
                    self.player.vx = max(0.0, self.player.vx)

            self.rising_hazard.update(dt, self.player)
            if self.rising_hazard.check_player_hit(self.player):
                self._handle_player_rising_hazard()

        currently_attacking = self.player.state_name in ("attack", "attack_special")
        if currently_attacking and not self._prev_attack_state:
            self._hit_this_swing.clear()
            self._flame_hits.clear()
        self._prev_attack_state = currently_attacking

        for p in self.damage_popups[:]:
            p["timer"] -= dt
            p["y"] -= 20.0 * dt
            if p["timer"] <= 0.0:
                self.damage_popups.remove(p)

        for enemy in self.enemies[:]:
            enemy.update(dt)
            self._resolve_combat(enemy)

        self._resolve_enemy_collisions()

        active_enemies = []
        for e in self.enemies:
            if e.dead:
                self.respawn_queue.append({
                    "enemy_type": e.enemy_type,
                    "spawn_x": e.spawn_x,
                    "spawn_y": e.spawn_y,
                    "timer": 3.0,
                })
            else:
                active_enemies.append(e)
        self.enemies = active_enemies

        for req in self.respawn_queue[:]:
            req["timer"] -= dt
            if req["timer"] <= 0.0:
                self.respawn_queue.remove(req)
                new_enemy = Enemy(
                    x=req["spawn_x"],
                    y=req["spawn_y"],
                    enemy_type=req["enemy_type"],
                    floor_y=float(self.MAP_HEIGHT),
                    map_w=float(self.MAP_WIDTH),
                )
                new_enemy.player = self.player
                new_enemy.tilemap = self.tilemap
                new_enemy.active_collision_layers = self._get_enemy_collision_layers(new_enemy)
                new_enemy.on_hazard_hit = self._on_hazard_hit
                self.enemies.append(new_enemy)

    def _resolve_combat(self, enemy: Enemy) -> None:
        player = self.player
        if player.state_name == "death":
            return

        attack_hb = player.get_attack_hitbox()
        if attack_hb is not None and attack_hb.colliderect(enemy.hitbox):
            hit_key = (id(enemy), getattr(player, "swing_id", 0))
            if enemy.is_active() and hit_key not in self._hit_this_swing:
                action_name = "special" if player.state_name == "attack_special" else "attack"
                action = player.get_action(action_name)
                combo = action.get("combo", {})
                current_state = player.state_machine.current if player.state_machine else None

                if getattr(current_state, "in_combo_followup", False) and "hit2_damage" in combo:
                    dmg = int(combo["hit2_damage"])
                    self.camera.shake(3.0, 0.15)
                else:
                    dmg = int(action.get("damage", 10))
                    self.camera.shake(1.5, 0.1)

                atk_func = action.get("func")
                if atk_func:
                    atk_func(player, enemy, action_name)
                else:
                    enemy.take_damage(float(dmg))

                self._hit_this_swing.add(hit_key)
                self._spawn_popup(f"-{dmg}", enemy.hitbox.centerx, enemy.hitbox.top - 6, 0.5, (255, 230, 80))
            elif not enemy.is_active() and hit_key not in self._hit_this_swing:
                self._hit_this_swing.add(hit_key)
                self._spawn_popup("IMMUNE", enemy.hitbox.centerx, enemy.hitbox.top - 6, 0.4, (160, 190, 255))

        if player.skin == "mage" and player.area_active:
            for f in player.flames:
                flame_rect = pygame.Rect(int(f["x"]) - 32, int(f["y"]) - 56, 64, 56)
                hit_key = (id(enemy), f["idx"])
                if enemy.is_active() and flame_rect.colliderect(enemy.hitbox) and hit_key not in self._flame_hits:
                    action = player.get_action("special")
                    dmg = int(action.get("damage", 25))
                    atk_func = action.get("func")
                    if atk_func:
                        atk_func(player, enemy, "special")
                    else:
                        enemy.take_damage(float(dmg))
                    self.camera.shake(2.0, 0.12)
                    self._flame_hits.add(hit_key)
                    self._spawn_popup(f"-{dmg}", enemy.hitbox.centerx, enemy.hitbox.top - 8, 0.5, (255, 130, 40))

        is_sword_special = (player.state_name == "attack_special" and player.skin == "sword")
        if (
            enemy.is_active()
            and enemy.state_name not in ("hit", "death")
            and player.state_name not in ("hit", "death", "dash")
            and not is_sword_special
            and player.invulnerable_timer <= 0.0
            and enemy.hitbox.colliderect(player.hitbox)
        ):
            dmg = int(enemy.contact_damage)
            player.take_damage(dmg, source_x=enemy.hitbox.centerx)
            self.camera.shake(3.5, 0.2)
            self._spawn_popup(f"-{dmg}", player.hitbox.centerx, player.hitbox.top - 8, 0.6, (255, 75, 75))

    def _resolve_enemy_collisions(self) -> None:
        active = [
            e for e in self.enemies
            if e.is_active() and e.state_name != "death" and not e.dead
        ]

        for i in range(len(active)):
            e1 = active[i]
            for j in range(i + 1, len(active)):
                e2 = active[j]

                if e1.hitbox.colliderect(e2.hitbox):
                    overlap_x = min(e1.hitbox.right, e2.hitbox.right) - max(e1.hitbox.left, e2.hitbox.left)
                    if overlap_x > 0:
                        m1 = _ENEMY_MASS.get(e1.enemy_type, 1.0)
                        m2 = _ENEMY_MASS.get(e2.enemy_type, 1.0)
                        total_m = m1 + m2

                        push1 = overlap_x * (m2 / total_m)
                        push2 = overlap_x * (m1 / total_m)

                        if e1.hitbox.centerx <= e2.hitbox.centerx:
                            e1.x = max(0.0, e1.x - push1)
                            e2.x = min(float(self.MAP_WIDTH - e2.hitbox.width), e2.x + push2)
                        else:
                            e1.x = min(float(self.MAP_WIDTH - e1.hitbox.width), e1.x + push1)
                            e2.x = max(0.0, e2.x - push2)

                        e1.hitbox.x = int(e1.x)
                        e2.hitbox.x = int(e2.x)

    def _visible_tile_range(self) -> Tuple[int, int, int, int]:
        ox, oy = self.camera_offset
        min_col = max(0, int(ox // self.TILE_SIZE))
        min_row = max(0, int(oy // self.TILE_SIZE))
        max_col = min(self.MAP_COLS - 1, int((ox + settings.VIRTUAL_WIDTH) // self.TILE_SIZE) + 1)
        max_row = min(self.MAP_ROWS - 1, int((oy + settings.VIRTUAL_HEIGHT) // self.TILE_SIZE) + 1)
        return (min_row, min_col, max_row, max_col)

    def _render_layer(self, layer_name: str, surface: pygame.Surface, ghost: bool = False) -> None:
        if layer_name not in self.tilemap.layer_names():
            return

        min_row, min_col, max_row, max_col = self._visible_tile_range()
        grid = self.tilemap.get_layer(layer_name)
        cam_x, cam_y = self.camera_offset

        for row in range(min_row, max_row + 1):
            for col in range(min_col, max_col + 1):
                gid = grid[row][col]
                if gid == 0:
                    continue

                flip_h, flip_v, flip_d = self.flipped_tiles.get(
                    (layer_name, row, col),
                    (False, False, False),
                )
                tile_surf = self._get_tile_surface(gid, flip_h, flip_v, flip_d, ghost=ghost)
                if tile_surf is not None:
                    dest_x = col * self.TILE_SIZE - cam_x
                    dest_y = row * self.TILE_SIZE - cam_y
                    surface.blit(tile_surf, (dest_x, dest_y))

    def render(self, surface: pygame.Surface) -> None:
        cam_x, cam_y = self.camera_offset
        phase = self.player.phase_color

        surface.fill((10, 10, 15))

        # 1. Fondo dual correspondiente a la fase activa con velo de profundidad atmosférica
        bg_key = f"{self.map_name}_past" if phase == "green" else f"{self.map_name}_future"
        bg_surf = self.bg_surfaces.get(phase, settings.TEXTURES.get(bg_key))
        if bg_surf:
            bg_w, bg_h = bg_surf.get_size()
            if bg_w < self.MAP_WIDTH:
                # Room is wider than background image: repeat horizontally with smooth parallax
                scroll_x = -int(cam_x * 0.4) % bg_w - bg_w
                scroll_y = -cam_y if bg_h >= self.MAP_HEIGHT else -int(cam_y * 0.3)
                curr_x = scroll_x
                while curr_x < settings.VIRTUAL_WIDTH:
                    surface.blit(bg_surf, (curr_x, scroll_y))
                    curr_x += bg_w
            else:
                surface.blit(bg_surf, (-cam_x, -cam_y))

        self._render_layer("background", surface, ghost=False)
        self._render_layer("ground", surface, ghost=False)
        self._render_layer("decoration", surface, ghost=False)

        # 2. Capas de tiles según la fase activa
        if phase == "green":
            # Capas base y del Pasado
            self._render_layer("green_background", surface, ghost=False)
            self._render_layer("green_ground", surface, ghost=False)
            self._render_layer("green_decoration", surface, ghost=False)
            # Plataformas del Futuro en modo fantasma (semitransparentes)
            self._render_layer("red_ground", surface, ghost=True)
        else:
            # Capas base y del Futuro
            self._render_layer("red_background", surface, ghost=False)
            self._render_layer("red_ground", surface, ghost=False)
            self._render_layer("red_decoration", surface, ghost=False)
            # Plataformas del Pasado en modo fantasma (semitransparentes)
            self._render_layer("green_ground", surface, ghost=True)

        # 3. Partículas atmosféricas flotantes y polvo de impacto
        self._particles_surface.fill((0, 0, 0, 0))
        part_col = (120, 255, 190) if phase == "green" else (255, 135, 80)
        for p in self._ambient_particles:
            screen_px = int(p["x"] - cam_x)
            screen_py = int(p["y"] - cam_y)
            if 0 <= screen_px < settings.VIRTUAL_WIDTH and 0 <= screen_py < settings.VIRTUAL_HEIGHT:
                pygame.draw.circle(
                    self._particles_surface,
                    (*part_col, p["alpha"]),
                    (screen_px, screen_py),
                    p["radius"],
                )

        dust_col = (140, 240, 190) if phase == "green" else (240, 150, 130)
        for d in self.dust_particles:
            screen_px = int(d["x"] - cam_x)
            screen_py = int(d["y"] - cam_y)
            alpha = int(220 * max(0.0, min(1.0, d["life"] / d["max_life"])))
            if 0 <= screen_px < settings.VIRTUAL_WIDTH and 0 <= screen_py < settings.VIRTUAL_HEIGHT:
                pygame.draw.circle(
                    self._particles_surface,
                    (*dust_col, alpha),
                    (screen_px, screen_py),
                    d["radius"],
                )
        surface.blit(self._particles_surface, (0, 0))

        # (Player outline already communicates phase color — floor glow removed to avoid
        #  the bright oval artifact over tiles.)

        for trap in self.falling_traps:
            trap.render(surface, cam_x, cam_y)

        for saw in self.saw_hazards:
            saw.render(surface, cam_x, cam_y)

        # 4. Entidades
        for enemy in self.enemies:
            enemy.render(surface, cam_x, cam_y)

        self.player.render(surface, cam_x, cam_y)

        # 5. Peligro de Líquido ascendente y Reja en el mundo
        if self.rising_hazard is not None:
            self.rising_hazard.render_world(surface, cam_x, cam_y, phase)

        # 6. Popups de daño y efectos
        for p in self.damage_popups:
            render_text(
                surface,
                p["text"],
                settings.FONTS["hud"],
                int(p["x"] - cam_x),
                int(p["y"] - cam_y),
                p["color"],
                center=True,
                shadowed=True,
            )

        # 7. Indicador lateral de la torre (HUD)
        if self.rising_hazard is not None:
            self.rising_hazard.render_hud(surface, self.player)
