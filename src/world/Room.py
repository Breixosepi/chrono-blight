"""
Chrono Blight - World Room Component
"""
import json
import math
import pathlib
import random
from typing import Any, Dict, List, Optional, Tuple, Set

import pygame
from gale.text import render_text
from gale.tilemap import TileMap, load_tiled_map

import settings
from src.definitions import entity as entity_defs
from src.entities.Player import Player
from src.entities.Enemy import Enemy
from src.world.Camera import Camera as SmoothCamera
from src.world.FallingTrap import FallingTrap
from src.world.SawHazard import SawHazard
from src.world.RisingHazard import RisingHazard
from src.world.Elevator import Elevator
from src.world.ArenaManager import ArenaManager
from src.world.combat import CombatResolver

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

_PHASE_LAYERS: Dict[str, List[str]] = {
    "green": ["ground", "green_ground"],
    "red":   ["ground", "red_ground"],
}

class Room:
    TILE_SIZE: int = settings.TILE_SIZE
    DEFAULT_SPAWN_X: float = 48.0
    DEFAULT_SPAWN_Y: float = 220.0

    def __init__(
        self,
        map_name: str = "middle",
        spawn_x: Optional[float] = None,
        spawn_y: Optional[float] = None,
        player: Optional[Player] = None,
    ) -> None:
        self.map_name = map_name
        self.play_state: Any = None
        map_file = settings.BASE_DIR / "assets" / "tilemaps" / f"{map_name}.json"
        
        with open(str(map_file), "r", encoding="utf-8") as f:
            self.map_data = json.load(f)
            
        self.tilemap: TileMap = load_tiled_map(str(map_file))
        self.MAP_COLS, self.MAP_ROWS = self.tilemap.cols, self.tilemap.rows
        self.MAP_WIDTH, self.MAP_HEIGHT = self.tilemap.pixel_width, self.tilemap.pixel_height

        self.spawn_x, self.spawn_y = self._extract_spawn_point(spawn_x, spawn_y, player)
        self._preprocess_tilemap()

        self.camera = SmoothCamera(
            settings.VIRTUAL_WIDTH,
            settings.VIRTUAL_HEIGHT,
            bounds=pygame.Rect(0, 0, self.MAP_WIDTH, self.MAP_HEIGHT),
        )

        self._init_player(player)
        self.camera.snap_to(self.player.hitbox.centerx, self.player.hitbox.centery)

        self.enemies: List[Enemy] = []
        self.falling_traps: List[FallingTrap] = []
        self.saw_hazards: List[SawHazard] = []
        self.elevators: List[Elevator] = []
        self.enemy_projectiles: List[dict] = []
        
        self.dust_particles: List[dict] = []
        self.health_orbs: list = []
        self.damage_popups: List[Dict[str, Any]] = []
        self.respawn_queue: List[Dict[str, Any]] = []
        self.combat_resolver = CombatResolver(self)
        self.rising_hazard = RisingHazard(self) if self.map_name == "subida" else None
        self.solid_blockers: List[pygame.Rect] = []

        self._init_enemies()
        self._init_traps()
        self._init_graphics()

        self.arena = ArenaManager(self) if self.map_name in ("sala_future", "sala_past") else None
        self.cleared_events: set = getattr(self.play_state, "cleared_events", set()) if hasattr(self, "play_state") and self.play_state else set()
        self._check_cleared_events()

    def _check_cleared_events(self) -> None:
        cleared = getattr(self.play_state, "cleared_events", None)
        if cleared is None:
            cleared = getattr(self, "cleared_events", set())
        
        if "boss_cultist_defeated" in cleared and self.map_name == "sala_future":
            if self.arena and self.arena.state not in ("cleared", "clearing", "unlocking"):
                self.arena = None
            self.enemies = []
            for elev in self.elevators:
                if elev.state not in ("descending", "ascending", "arriving", "arriving_open"):
                    elev.state = "open"
                    elev.image = elev.tex_open
                    elev.y = elev.start_y - elev.height
                    elev.hitbox.y = int(elev.y)

        if "survival_boss_defeated" in cleared and self.map_name == "sala_past":
            if "lava" in settings.SOUNDS:
                settings.SOUNDS["lava"].stop()
            if self.arena and self.arena.state not in ("cleared", "clearing", "unlocking"):
                self.arena = None
            self.enemies = []
            if getattr(self, "rising_hazard", None):
                self.rising_hazard.reset()
            self.rising_hazard = None
            self.lava_rising = False
            for saw in self.saw_hazards:
                saw.stop()
            for elev in self.elevators:
                if elev.state not in ("descending", "ascending", "arriving", "arriving_open"):
                    elev.state = "open"
                    elev.image = elev.tex_open
                    elev.y = elev.start_y - elev.height
                    elev.hitbox.y = int(elev.y)

        if "subida_cleared" in cleared and self.map_name in ("subida", "subida_past", "subida_future"):
            if "lava" in settings.SOUNDS:
                settings.SOUNDS["lava"].stop()
            if getattr(self, "rising_hazard", None):
                self.rising_hazard.reset()
            self.rising_hazard = None

        # Elevator to Final Boss in 'middle' (unlocked only when all major challenges are cleared)
        all_major_events = {"survival_boss_defeated", "boss_cultist_defeated", "subida_cleared"}
        all_cleared = all_major_events.issubset(cleared)
        if self.map_name == "middle":
            for elev in self.elevators:
                if "middle_elevator_unlocked" in cleared:
                    if elev.state not in ("ascending", "arriving", "arriving_open"):
                        elev.state = "open"
                        elev.image = elev.tex_open
                        elev.y = elev.start_y - elev.height
                        elev.hitbox.y = int(elev.y)
                elif all_cleared:
                    if elev.state in ("hidden", "hidden_permanently"):
                        elev.activate()
                        cleared.add("middle_elevator_unlocked")
                        if self.play_state:
                            self.play_state.cleared_events.add("middle_elevator_unlocked")
                    elif elev.state not in ("descending", "ascending", "arriving", "arriving_open"):
                        elev.state = "open"
                        elev.image = elev.tex_open
                        elev.y = elev.start_y - elev.height
                        elev.hitbox.y = int(elev.y)
                else:
                    elev.state = "hidden"

        # Dynamic door / passage blockers defined via Tiled objects (e.g. in 'traps' layer)
        self.solid_blockers = []
        for layer in self.map_data.get("layers", []):
            if layer.get("type") == "objectgroup":
                for obj in layer.get("objects", []):
                    props = self._parse_props(obj)
                    obj_name = str(obj.get("name", "")).lower()
                    obj_type = str(obj.get("type", "")).lower()
                    req_event = props.get("requires_event", props.get("event"))

                    # If object has an event requirement or is a blocker/door
                    if req_event or "block" in obj_name or "block" in obj_type or "door" in obj_name or "door" in obj_type:
                        if not req_event:
                            continue

                        # Determine tile range: either from explicit properties (col, row, count) or bounding box
                        if "col" in props or "column" in props:
                            c = int(props.get("col", props.get("column", 0)))
                            r = int(props.get("row", 0))
                            count = int(props.get("count", 1))
                            axis = str(props.get("axis", "vertical")).lower()
                            if axis == "vertical":
                                start_col, end_col = c, c
                                start_row, end_row = r, r + count - 1
                            else:
                                start_col, end_col = c, c + count - 1
                                start_row, end_row = r, r
                            ox = float(start_col * self.TILE_SIZE)
                            oy = float(start_row * self.TILE_SIZE)
                            ow = float((end_col - start_col + 1) * self.TILE_SIZE)
                            oh = float((end_row - start_row + 1) * self.TILE_SIZE)
                        else:
                            ox = float(obj.get("x", 0.0))
                            oy = float(obj.get("y", 0.0))
                            ow = max(1.0, float(obj.get("width", 16.0)))
                            oh = max(1.0, float(obj.get("height", 16.0)))
                            start_col = int(ox // self.TILE_SIZE)
                            end_col = int((ox + ow - 1) // self.TILE_SIZE)
                            start_row = int(oy // self.TILE_SIZE)
                            end_row = int((oy + oh - 1) // self.TILE_SIZE)

                        is_event_cleared = (
                            req_event in cleared
                            or (req_event in ("all_events", "all_bosses_defeated", "all_cleared") and all_cleared)
                        )
                        if is_event_cleared:
                            # Event completed: remove tiles from tilemap layers
                            for row_idx in range(start_row, end_row + 1):
                                for col_idx in range(start_col, end_col + 1):
                                    if 0 <= row_idx < self.MAP_ROWS and 0 <= col_idx < self.MAP_COLS:
                                        self.tilemap.set_gid("ground", row_idx, col_idx, 0)
                                        self.tilemap.set_gid("red_ground", row_idx, col_idx, 0)
                                        self.tilemap.set_gid("green_ground", row_idx, col_idx, 0)
                        else:
                            # Event NOT completed: add solid blocker
                            blocker_rect = pygame.Rect(int(ox), int(oy), int(ow), int(oh))
                            if not any(s == blocker_rect for s in self.solid_blockers):
                                self.solid_blockers.append(blocker_rect)

    @property
    def camera_offset(self) -> Tuple[float, float]:
        ox, oy = self.camera.offset
        return (round(ox), round(oy))

    def _get_tiled_objects(self, valid_layer_names: Set[str]) -> List[Dict[str, Any]]:
        objects = []
        for layer in self.map_data.get("layers", []):
            name = str(layer.get("name", "")).lower()
            if name in valid_layer_names and "objects" in layer:
                objects.extend(layer["objects"])
            elif layer.get("type") == "objectgroup" and not valid_layer_names:
                objects.extend(layer.get("objects", []))
        return objects

    def _parse_props(self, obj: dict) -> dict:
        return {p.get("name"): p.get("value") for p in obj.get("properties", []) if isinstance(p, dict) and "name" in p}

    def _spawn_enemy(self, x: float, y: float, enemy_type: str) -> None:
        enemy = Enemy(x, y, enemy_type=enemy_type, floor_y=float(self.MAP_HEIGHT), map_w=float(self.MAP_WIDTH))
        enemy.room, enemy.player, enemy.tilemap = self, self.player, self.tilemap
        enemy.active_collision_layers = self._get_enemy_collision_layers(enemy)
        enemy.on_hazard_hit = self._on_hazard_hit
        self.enemies.append(enemy)

    def _init_player(self, player_instance: Optional[Player]) -> None:
        if player_instance is None:
            self.player = Player(
                self.spawn_x, self.spawn_y, 
                floor_y=float(self.MAP_HEIGHT), map_w=float(self.MAP_WIDTH)
            )
            self.player.phase = "past"
            self.player.phase_color = "green"
        else:
            self.player = player_instance
            self.player.x, self.player.y = self.spawn_x, self.spawn_y
            self.player.hitbox.topleft = (int(self.spawn_x), int(self.spawn_y))
            self.player.vx = self.player.vy = 0.0
            self.player.floor_y = float(self.MAP_HEIGHT)
            self.player.map_w = float(self.MAP_WIDTH)
            if not getattr(self.player, "arriving_via_elevator", False):
                self.player.hidden = False
                self.player.active = True

        if self.map_name == "sala_future":
            self.player.phase, self.player.phase_color = "future", "red"

        self.player.room = self
        self.player.tilemap = self.tilemap
        self.tilemap.room = self
        self.player.active_collision_layers = self._get_active_collision_layers()
        
        old_on_land = getattr(self.player, "on_land", lambda: None)
        def _on_player_land() -> None:
            old_on_land()
            self.spawn_dust(self.player.hitbox.centerx, self.player.hitbox.bottom, 4)
            
        self.player.on_land = _on_player_land
        self.player.on_jump_effect = lambda: self.spawn_dust(self.player.hitbox.centerx, self.player.hitbox.bottom, 4)

    def _extract_spawn_point(
        self,
        override_x: Optional[float],
        override_y: Optional[float],
        player: Optional[Player] = None,
    ) -> Tuple[float, float]:
        if player is not None and getattr(player, "arriving_via_elevator", False):
            for obj in self._get_tiled_objects(set()):
                combined = f"{obj.get('name', '')} {obj.get('type', '')}".lower()
                if "elevator" in combined or "ascensor" in combined:
                    props = self._parse_props(obj)
                    if str(props.get("start_state", "")) == "arriving":
                        return float(obj.get("x", 0)), float(obj.get("y", 0))
            for obj in self._get_tiled_objects(set()):
                combined = f"{obj.get('name', '')} {obj.get('type', '')}".lower()
                if "elevator" in combined or "ascensor" in combined:
                    return float(obj.get("x", 0)), float(obj.get("y", 0))

        if override_x is not None and override_y is not None:
            return float(override_x), float(override_y)

        for obj in self._get_tiled_objects(set()):
            name = str(obj.get("name", "")).lower()
            obj_type = str(obj.get("type", "")).lower()
            if name in ("spawn", "player_spawn", "player", "start") or obj_type in ("spawn", "player_spawn"):
                return float(obj.get("x", 0)), float(obj.get("y", 0))

        props = self._parse_props(self.map_data)
        if "spawn_x" in props and "spawn_y" in props:
            return float(props["spawn_x"]), float(props["spawn_y"])

        if override_x is not None:
            return float(override_x), self.DEFAULT_SPAWN_Y
        if self.map_name == "sala_past":
            return 580.0, 136.0
        return self.DEFAULT_SPAWN_X, self.DEFAULT_SPAWN_Y

    def _init_enemies(self) -> None:
        valid_layers = {"spawns", "spwans", "enemies", "enemy_spawns"}
        for obj in self._get_tiled_objects(valid_layers):
            props = self._parse_props(obj)
            t_name = (obj.get("name", "") or str(props.get("name", ""))).lower().strip()
            t_type = (obj.get("type", "") or obj.get("class", "") or str(props.get("enemy_type", ""))).lower().strip()
            
            if t_name in ("spawn", "player", "start", "arena_trigger", "boss_survival", "safe_point") or t_type in ("spawn", "player", "start", "arena_trigger", "boss_survival", "safe_point"):
                continue

            enemy_type = t_name if t_name in entity_defs.ENEMY_DEFS else (t_type if t_type in entity_defs.ENEMY_DEFS else None)
            if enemy_type:
                self._spawn_enemy(float(obj.get("x", 0.0)), float(obj.get("y", 0.0)), enemy_type)

    def _init_traps(self) -> None:
        self.altars: list = []
        self.safe_point_x = 543.0
        self.safe_point_y = 136.0
        
        for obj in self._get_tiled_objects({"traps", "objects", "interactables", "spawns", "spwans"}):
            props = self._parse_props(obj)
            t_name = obj.get("name", "") or str(props.get("name", ""))
            t_type = obj.get("type", "") or obj.get("class", "") or str(props.get("type", ""))
            combined_id = f"{t_name} {t_type}".lower()
            
            x, y = float(obj.get("x", 0.0)), float(obj.get("y", 0.0))

            if "altar" in combined_id or "obelisk" in combined_id:
                from src.world.Altar import Altar
                obj_h = float(obj.get("height", 16.0))
                self.altars.append(Altar(x, y, self, obj_height=obj_h))
            elif "saw" in combined_id or "shuriken" in combined_id:
                h_type = "shuriken" if "shuriken" in combined_id else "saw"
                phase = "green" if "green" in combined_id else ("red" if "red" in combined_id else "neutral")
                init_dir = int(props.get("initial_direction", props.get("direction", props.get("dir", 0))))
                if init_dir == 0:
                    init_dir = -1 if x > 300 else 1
                self.saw_hazards.append(SawHazard(
                    self, x, y, hazard_type=h_type, phase=phase,
                    patrol_dist=float(props.get("patrol_dist", 0.0)), axis=str(props.get("axis", "y")),
                    speed=float(props.get("speed", 50.0)), damage=int(props.get("damage", 15)),
                    initial_direction=init_dir
                ))
            elif "elevator" in combined_id or "ascensor" in combined_id:
                start_state = str(props.get("start_state", "hidden"))
                if start_state == "arriving":
                    if getattr(self.player, "arriving_via_elevator", False):
                        self.player.arriving_via_elevator = False
                        self.player.active = False
                        self.player.state_machine.change("idle")
                    else:
                        start_state = "hidden_permanently"
                elev_obj = Elevator(self, x, y, dest_map=str(props.get("dest_map", "")), start_state=start_state)
                self.elevators.append(elev_obj)
                if start_state == "arriving":
                    self.camera.snap_to(elev_obj.hitbox.centerx, elev_obj.start_y - elev_obj.height // 2)
            elif "green" in combined_id or "red" in combined_id:
                phase = "green" if "green" in combined_id else "red"
                self.falling_traps.append(FallingTrap(self, x, y, phase))
            elif "lava" in combined_id:
                self.lava_target_y = y
                cleared_ev = getattr(self.play_state, "cleared_events", set()) if hasattr(self, "play_state") and self.play_state else getattr(self, "cleared_events", set())
                if "survival_boss_defeated" in cleared_ev and self.map_name == "sala_past":
                    if "lava" in settings.SOUNDS:
                        settings.SOUNDS["lava"].stop()
                    continue
                if not self.rising_hazard:
                    self.rising_hazard = RisingHazard(self, speed=0.0)
                    self.rising_hazard.is_pool = True
                    self.rising_hazard.start_y = float(self.MAP_HEIGHT)
                    self.rising_hazard.current_y = float(self.MAP_HEIGHT)
                    self.rising_hazard.alert_timer = 0.0
                    self.rising_hazard.alert_text = ""
                    self.rising_hazard.state = RisingHazard.STATE_MOVING
            elif "safe_point" in combined_id:
                self.safe_point_x = x
                self.safe_point_y = y

    def _preprocess_tilemap(self) -> None:
        self.flipped_tiles: Dict[Tuple[str, int, int], Tuple[bool, bool, bool]] = {}
        for layer_name in self.tilemap.layer_names():
            for r in range(self.tilemap.rows):
                for c in range(self.tilemap.cols):
                    raw = self.tilemap.get_gid(layer_name, r, c)
                    if raw > 100000:
                        fh, fv, fd = bool(raw & 0x80000000), bool(raw & 0x40000000), bool(raw & 0x20000000)
                        self.flipped_tiles[(layer_name, r, c)] = (fh, fv, fd)
                        self.tilemap.set_gid(layer_name, r, c, raw & 0x1FFFFFFF)
        self._tile_cache, self._ghost_tile_cache = {}, {}

    def _get_active_collision_layers(self) -> List[str]:
        return _PHASE_LAYERS.get(self.player.phase_color, ["ground", "red_ground"])

    def _get_enemy_collision_layers(self, enemy: Enemy) -> List[str]:
        return _PHASE_LAYERS.get(enemy.phase, ["ground", "green_ground", "red_ground"])

    def _init_graphics(self) -> None:
        props = self._parse_props(self.map_data)
        bg_configs = [
            ("green", props.get("bg_past", f"{self.map_name}_past"), f"{self.map_name}_past", (8, 16, 20, 130)),
            ("red", props.get("bg_future", f"{self.map_name}_future"), f"{self.map_name}_future", (22, 10, 14, 135)),
        ]
        self.bg_surfaces = {}
        for phase, target, fallback, wash_color in bg_configs:
            raw_bg = self._load_background_image(target) or self._load_background_image(fallback)
            if raw_bg:
                bg = raw_bg.copy()
                wash = pygame.Surface(bg.get_size(), pygame.SRCALPHA)
                wash.fill(wash_color)
                bg.blit(wash, (0, 0))
                self.bg_surfaces[phase] = bg

        self._ambient_particles = [{
            "x": random.uniform(0, self.MAP_WIDTH), "y": random.uniform(0, self.MAP_HEIGHT),
            "speed_y": random.uniform(-14.0, -5.0), "speed_x": random.uniform(-4.0, 4.0),
            "drift_timer": random.uniform(0.0, 6.28), "radius": random.choice([1, 1, 2]), "alpha": random.randint(85, 175)
        } for _ in range(40)]
        self._particles_surface = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
        
        self._bullet_surf = pygame.Surface((14, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(self._bullet_surf, (255, 100, 30, 220), (0, 0, 14, 8))
        pygame.draw.ellipse(self._bullet_surf, (255, 250, 180, 255), (3, 1, 8, 6))
        
        self._trail_surf = pygame.Surface((8, 6), pygame.SRCALPHA)
        
        tex = settings.TEXTURES.get("destructible_block")
        frames = settings.FRAMES.get("destructible_block", [])
        if tex and frames:
            self._brick_tile = pygame.transform.scale(tex.subsurface(frames[0]), (self.TILE_SIZE, self.TILE_SIZE))
        else:
            self._brick_tile = pygame.Surface((self.TILE_SIZE, self.TILE_SIZE))
            self._brick_tile.fill((120, 110, 100))

    def _load_background_image(self, candidate_name: str) -> Optional[pygame.Surface]:
        if not candidate_name: return None
        if candidate_name in settings.TEXTURES: return settings.TEXTURES[candidate_name]
        
        bg_dir = settings.BASE_DIR / "assets" / "graphics" / "backgrounds"
        clean_name = pathlib.Path(candidate_name).stem
        for p in (bg_dir / candidate_name, bg_dir / f"{candidate_name}.png", bg_dir / f"{clean_name}.png"):
            if p.is_file():
                try:
                    surf = pygame.image.load(str(p)).convert_alpha()
                    settings.TEXTURES[candidate_name] = surf
                    return surf
                except (pygame.error, FileNotFoundError):
                    pass
        return None

    def update(self, dt: float) -> None:
        self._is_sword_special = (self.player.state_name == "attack_special" and self.player.skin == "sword")
        self._update_particles(dt)
        self._update_projectiles(dt)
        
        self.player.active_collision_layers = self._get_active_collision_layers()
        self.player.update(dt)

        for b in self.solid_blockers:
            if self.player.hitbox.colliderect(b):
                overlap_left = self.player.hitbox.right - b.left
                overlap_right = b.right - self.player.hitbox.left
                overlap_top = self.player.hitbox.bottom - b.top
                overlap_bottom = b.bottom - self.player.hitbox.top
                min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
                if min_overlap == overlap_left:
                    self.player.hitbox.right = b.left
                    self.player.x = float(self.player.hitbox.x)
                    self.player.vx = 0.0
                elif min_overlap == overlap_right:
                    self.player.hitbox.left = b.right
                    self.player.x = float(self.player.hitbox.x)
                    self.player.vx = 0.0
                elif min_overlap == overlap_top:
                    self.player.hitbox.bottom = b.top
                    self.player.y = float(self.player.hitbox.y)
                    self.player.vy = 0.0
                    self.player.is_grounded = True
                elif min_overlap == overlap_bottom:
                    self.player.hitbox.top = b.bottom
                    self.player.y = float(self.player.hitbox.y)
                    self.player.vy = 0.0

        for trap in self.falling_traps: trap.update(dt)
        for elev in self.elevators: elev.update(dt)
        for saw in self.saw_hazards: saw.update(dt)
        for altar in self.altars: altar.update(dt, self.player)
        for b in getattr(self, "crumbling_blocks", []): b["timer"] = max(0.0, b["timer"] - dt)

        if self.arena:
            self.arena.update(dt)

        for orb in self.health_orbs:
            orb.update(dt, self.player)
        self.health_orbs = [orb for orb in self.health_orbs if not orb.is_dead]

        self.camera.update(self.player.hitbox.centerx, self.player.hitbox.centery, dt)

        self._check_environmental_hazards(dt)

        for p in self.damage_popups[:]:
            p["timer"] -= dt
            p["y"] -= 20.0 * dt
            if p["timer"] <= 0.0: self.damage_popups.remove(p)

        self._update_enemies_and_combat(dt)
        self._process_respawns(dt)

    def _update_particles(self, dt: float) -> None:
        for p in self._ambient_particles:
            p["drift_timer"] += dt * 1.5
            p["y"] += p["speed_y"] * dt
            p["x"] += (p["speed_x"] + math.sin(p["drift_timer"]) * 6.0) * dt
            if p["y"] < 0: p["y"], p["x"] = float(self.MAP_HEIGHT), random.uniform(0, self.MAP_WIDTH)
            elif p["x"] < 0: p["x"] = float(self.MAP_WIDTH)
            elif p["x"] > self.MAP_WIDTH: p["x"] = 0.0

        for d in self.dust_particles[:]:
            d["life"] -= dt
            d["x"] += d["vx"] * dt
            d["y"] += d["vy"] * dt
            if d["life"] <= 0.0: self.dust_particles.remove(d)

    def _update_projectiles(self, dt: float) -> None:
        for p in self.enemy_projectiles[:]:
            p["life"] -= dt
            p["x"] += p["vx"] * dt
            p["trail"].append({"x": p["x"], "y": p["y"], "life": 0.14})
            
            for tr in p["trail"][:]:
                tr["life"] -= dt
                if tr["life"] <= 0: p["trail"].remove(tr)

            p_rect = pygame.Rect(int(p["x"] - 6), int(p["y"] - 4), 12, 8)
            can_hit_player = (
                not self.player.is_dead() 
                and self.player.state_name not in ("hit", "death", "dash")
                and not self._is_sword_special
                and self.player.invulnerable_timer <= 0.0
            )

            if can_hit_player and p_rect.colliderect(self.player.hitbox):
                self.player.take_damage(int(p["damage"]), source_x=p["x"])
                self.camera.shake(2.5, 0.15)
                self._spawn_popup(f"-{int(p['damage'])}", self.player.hitbox.centerx, self.player.hitbox.top - 8, 0.6, (255, 60, 60))
                self.enemy_projectiles.remove(p)
                continue

            if p["x"] <= 12.0 or p["x"] >= float(self.MAP_WIDTH) - 12.0 or p["life"] <= 0:
                self.enemy_projectiles.remove(p)

    def _check_environmental_hazards(self, dt: float) -> None:
        if self.player.state_name == "unlock":
            return

        if self.rising_hazard is None and self.player.hitbox.bottom >= (self.MAP_HEIGHT - 4):
            if self.player.state_name != "death":
                self.player.take_damage(20)
                self.camera.shake(4.0, 0.25)
                self._spawn_popup("-20 (SPIKES)", self.player.hitbox.centerx, self.player.hitbox.top - 10, 0.8, (255, 50, 50))
                if self.player.state_name != "death": self._reset_player_to_spawn()

        if self.rising_hazard:
            if getattr(self, "lava_rising", False) and self.map_name == "sala_past":
                if self.rising_hazard.current_y > self.lava_target_y:
                    self.rising_hazard.current_y -= dt * 28.0
                    if self.rising_hazard.current_y <= self.lava_target_y:
                        self.rising_hazard.current_y = self.lava_target_y
                        self.lava_rising = False
            self.rising_hazard.update(dt, self.player)
            
            if self.rising_hazard.check_player_hit(self.player) and self.player.state_name != "death" and self.player.invulnerable_timer <= 0:
                settings.SOUNDS["fall-lava"].play()
                if self.map_name == "sala_past":
                    self.player.take_damage(20)
                    self.camera.shake(4.0, 0.25)
                    self._spawn_popup("-20 (LAVA)", self.player.hitbox.centerx, self.player.hitbox.top - 10, 0.8, (255, 50, 50))
                    if self.player.state_name != "death":
                        col = int(self.safe_point_x // self.TILE_SIZE)
                        row = 6
                        
                        # Position player squarely on top of the solid platform
                        self.player.x = float(col * self.TILE_SIZE)
                        self.player.y = float(row * self.TILE_SIZE - self.player.height)
                        self.player.hitbox.topleft = (int(self.player.x), int(self.player.y))
                        self.player.vx = 0.0
                        self.player.vy = 0.0
                        self.player.on_ground = True
                        self.player.change_state("idle")
                        self.player.invulnerable_timer = 2.0
                        
                        cols = [col - 1, col, col + 1, col + 2]
                        valid_cols = [c for c in cols if 0 <= c < self.MAP_COLS]
                        
                        if 0 <= row < self.MAP_ROWS:
                            orig_gids = {c: self.tilemap.get_gid("ground", row, c) for c in valid_cols}
                            solid_gid = 20 if self.player.phase_color == "green" else 904
                            for c in valid_cols:
                                self.tilemap.set_gid("ground", row, c, solid_gid)
                            
                            # Add 2 crumbling 32x32 blocks to room for rendering and shaking
                            self.crumbling_blocks = [
                                {"x": float((col - 1) * self.TILE_SIZE), "y": float(row * self.TILE_SIZE), "timer": 2.0},
                                {"x": float((col + 1) * self.TILE_SIZE), "y": float(row * self.TILE_SIZE), "timer": 2.0},
                            ]
                            
                            def remove_blocks():
                                if hasattr(self, "tilemap"):
                                    for c, gid in orig_gids.items():
                                        self.tilemap.set_gid("ground", row, c, gid)
                                    self.crumbling_blocks = []
                                    self.spawn_dust((col - 1) * 16 + 16, row * 16 + 16, count=8)
                                    self.spawn_dust((col + 1) * 16 + 16, row * 16 + 16, count=8)
                                    
                            from gale.timer import Timer
                            Timer.after(2.0, remove_blocks)
                else:
                    self.player.take_damage(25)
                    self.camera.shake(5.0, 0.3)
                    self._spawn_popup("-25 (HAZARD)", self.player.hitbox.centerx, self.player.hitbox.top - 10, 0.9, (255, 60, 40))
                    self.rising_hazard.reset()
                    if self.player.state_name != "death": self._reset_player_to_spawn()

    def _update_enemies_and_combat(self, dt: float) -> None:
        self.combat_resolver.update()
        active_enemies = []
        for enemy in self.enemies:
            enemy.update(dt)
            if not self.player.is_dead() and not enemy.dead and enemy.is_active():
                self.combat_resolver.handle_melee_combat(enemy)
                self.combat_resolver.handle_magic_combat(enemy)
                self.combat_resolver.handle_contact_damage(enemy)

            if enemy.dead:
                if random.random() < 0.25:
                    from src.world.HealthOrb import HealthOrb
                    self.health_orbs.append(HealthOrb(enemy.hitbox.centerx - 8, enemy.hitbox.centery - 8, self))
                
                if not getattr(enemy, "in_arena", False) and self.map_name != "sala_future" and self.arena is None:
                    self.respawn_queue.append({"type": enemy.enemy_type, "x": enemy.spawn_x, "y": enemy.spawn_y, "timer": 3.0})
            else:
                active_enemies.append(enemy)
                
        self.enemies = active_enemies
        self._resolve_enemy_collisions()

    def _resolve_enemy_collisions(self) -> None:
        active = [e for e in self.enemies if e.is_active() and e.state_name != "death" and not e.dead and e.enemy_type != "monster2"]
        for i in range(len(active)):
            e1 = active[i]
            for j in range(i + 1, len(active)):
                e2 = active[j]
                if e1.hitbox.colliderect(e2.hitbox):
                    overlap_x = min(e1.hitbox.right, e2.hitbox.right) - max(e1.hitbox.left, e2.hitbox.left)
                    if overlap_x > 0:
                        m1, m2 = _ENEMY_MASS.get(e1.enemy_type, 1.0), _ENEMY_MASS.get(e2.enemy_type, 1.0)
                        push1, push2 = overlap_x * (m2 / (m1 + m2)), overlap_x * (m1 / (m1 + m2))
                        if e1.hitbox.centerx <= e2.hitbox.centerx:
                            e1.x = max(0.0, e1.x - push1)
                            e2.x = min(float(self.MAP_WIDTH - e2.hitbox.width), e2.x + push2)
                        else:
                            e1.x = min(float(self.MAP_WIDTH - e1.hitbox.width), e1.x + push1)
                            e2.x = max(0.0, e2.x - push2)
                        e1.hitbox.x, e2.hitbox.x = int(e1.x), int(e2.x)

    def _process_respawns(self, dt: float) -> None:
        for req in self.respawn_queue[:]:
            req["timer"] -= dt
            if req["timer"] <= 0.0:
                self.respawn_queue.remove(req)
                self._spawn_enemy(req["x"], req["y"], req["type"])

    def check_room_exits(self) -> Optional[Tuple[str, float, float]]:
        if self.arena and self.arena.is_locked(): return None
        if self.player.state_name == "unlock": return None
        if not getattr(self.player, "active", True): return None
        if getattr(self.player, "hidden", False): return None
        
        from src.world.room_connections import ROOM_CONNECTIONS
        for exit_def in ROOM_CONNECTIONS.get(self.map_name, []):
            if exit_def["check"](self.player, self):
                return exit_def["target_room"], float(exit_def["target_spawn"][0]), float(exit_def["target_spawn"][1])
        return None

    def spawn_enemy_projectile(self, x: float, y: float, vx: float, damage: int = 12, color: tuple = (255, 220, 80)) -> None:
        self.enemy_projectiles.append({"x": float(x), "y": float(y), "vx": float(vx), "damage": int(damage), "life": 2.2, "color": color, "trail": []})

    def _on_hazard_hit(self, hazard: dict) -> None:
        self.camera.shake(2.0, 0.15)
        self._spawn_popup(f"-{int(hazard['damage'])}", hazard["hitbox"].centerx, hazard["hitbox"].top - 6, 0.6, (255, 60, 60))

    def _spawn_popup(self, text: str, x: float, y: float, timer: float, color: tuple) -> None:
        self.damage_popups.append({"text": text, "x": x, "y": y, "timer": timer, "color": color})

    def spawn_dust(self, x: float, y: float, count: int = 4, color: Optional[tuple] = None) -> None:
        for _ in range(count):
            self.dust_particles.append({
                "x": x + random.uniform(-5.0, 5.0), "y": y + random.uniform(-1.0, 1.0),
                "vx": random.uniform(-30.0, 30.0), "vy": random.uniform(-14.0, -4.0),
                "life": 0.22, "max_life": 0.22, "radius": random.choice([1, 2]),
                "color": color
            })

    def _reset_player_to_spawn(self) -> None:
        self.player.x, self.player.y = self.spawn_x, self.spawn_y
        self.player.vx = self.player.vy = 0.0
        self.player.hitbox.topleft = (int(self.spawn_x), int(self.spawn_y))
        self.player.change_state("idle")

    def _get_tile_surface(self, gid: int, flip_h: bool = False, flip_v: bool = False, flip_d: bool = False, ghost: bool = False) -> Optional[pygame.Surface]:
        key = (gid, flip_h, flip_v, flip_d)
        cache = self._ghost_tile_cache if ghost else self._tile_cache
        if key in cache: return cache[key]
        
        tileset = self.tilemap.tileset_for_gid(gid)
        if not tileset: return None
        
        sub = tileset.image.subsurface(tileset.rect_for(gid))
        if flip_d: sub = pygame.transform.flip(pygame.transform.rotate(sub, 270), True, False)
        if flip_h or flip_v: sub = pygame.transform.flip(sub, flip_h, flip_v)
        
        if ghost:
            ghost_surf = sub.copy()
            ghost_surf.set_alpha(75)
            cache[key] = ghost_surf
            return ghost_surf
            
        cache[key] = sub
        return sub

    def _render_layer(self, layer_name: str, surface: pygame.Surface, ghost: bool = False) -> None:
        if layer_name not in self.tilemap.layer_names(): return
        
        cam_x, cam_y = self.camera_offset
        min_col, min_row = max(0, int(cam_x // self.TILE_SIZE)), max(0, int(cam_y // self.TILE_SIZE))
        max_col = min(self.MAP_COLS - 1, int((cam_x + settings.VIRTUAL_WIDTH) // self.TILE_SIZE) + 1)
        max_row = min(self.MAP_ROWS - 1, int((cam_y + settings.VIRTUAL_HEIGHT) // self.TILE_SIZE) + 1)
        
        grid = self.tilemap.get_layer(layer_name)
        for row in range(min_row, max_row + 1):
            for col in range(min_col, max_col + 1):
                gid = grid[row][col]
                if gid == 0: continue
                
                flip_h, flip_v, flip_d = self.flipped_tiles.get((layer_name, row, col), (False, False, False))
                tile_surf = self._get_tile_surface(gid, flip_h, flip_v, flip_d, ghost=ghost)
                if tile_surf:
                    surface.blit(tile_surf, (col * self.TILE_SIZE - cam_x, row * self.TILE_SIZE - cam_y))

    def render(self, surface: pygame.Surface) -> None:
        cam_x, cam_y = self.camera_offset
        phase = self.player.phase_color
        surface.fill((10, 10, 15))

        self._render_environment(surface, cam_x, cam_y, phase)
        self._render_vfx_background(surface, cam_x, cam_y, phase)
        self._render_entities(surface, cam_x, cam_y, phase)
        self._render_ui(surface, cam_x, cam_y)

    def _render_environment(self, surface: pygame.Surface, cam_x: float, cam_y: float, phase: str) -> None:
        bg_surf = self.bg_surfaces.get(phase, settings.TEXTURES.get(f"{self.map_name}_{'past' if phase == 'green' else 'future'}"))
        if bg_surf:
            bg_w, bg_h = bg_surf.get_size()
            if bg_w < self.MAP_WIDTH:
                scroll_x, scroll_y = -int(cam_x * 0.4) % bg_w - bg_w, -cam_y if bg_h >= self.MAP_HEIGHT else -int(cam_y * 0.3)
                curr_x = scroll_x
                while curr_x < settings.VIRTUAL_WIDTH:
                    surface.blit(bg_surf, (curr_x, scroll_y))
                    curr_x += bg_w
            else:
                surface.blit(bg_surf, (-cam_x, -cam_y))

        self._render_layer("background", surface)
        self._render_layer("ground", surface)
        self._render_layer("decoration", surface)

        active_pfx, inactive_pfx = ("green", "red") if phase == "green" else ("red", "green")
        self._render_layer(f"{active_pfx}_background", surface)
        self._render_layer(f"{active_pfx}_ground", surface)
        self._render_layer(f"{active_pfx}_decoration", surface)
        self._render_layer(f"{inactive_pfx}_ground", surface, ghost=True)

        # Render visible stone/brick blocks for active solid blockers (temporary door/boss locks)
        if self.solid_blockers and hasattr(self, "_brick_tile") and self._brick_tile:
            ground_grid = self.tilemap.get_layer("ground") if "ground" in self.tilemap.layer_names() else None
            for rect in self.solid_blockers:
                for bx in range(rect.left, rect.right, self.TILE_SIZE):
                    for by in range(rect.top, rect.bottom, self.TILE_SIZE):
                        col = bx // self.TILE_SIZE
                        row = by // self.TILE_SIZE
                        has_tile = False
                        if ground_grid and 0 <= row < self.MAP_ROWS and 0 <= col < self.MAP_COLS:
                            has_tile = (ground_grid[row][col] != 0)
                        if not has_tile:
                            surface.blit(self._brick_tile, (bx - cam_x, by - cam_y))

    def _render_vfx_background(self, surface: pygame.Surface, cam_x: float, cam_y: float, phase: str) -> None:
        self._particles_surface.fill((0, 0, 0, 0))
        part_col = (120, 255, 190) if phase == "green" else (255, 135, 80)
        
        for p in self._ambient_particles:
            px, py = int(p["x"] - cam_x), int(p["y"] - cam_y)
            if 0 <= px < settings.VIRTUAL_WIDTH and 0 <= py < settings.VIRTUAL_HEIGHT:
                pygame.draw.circle(self._particles_surface, (*part_col, p["alpha"]), (px, py), p["radius"])

        dust_default = (140, 240, 190) if phase == "green" else (240, 150, 130)
        for d in self.dust_particles:
            px, py = int(d["x"] - cam_x), int(d["y"] - cam_y)
            alpha = int(220 * max(0.0, min(1.0, d["life"] / d["max_life"])))
            if 0 <= px < settings.VIRTUAL_WIDTH and 0 <= py < settings.VIRTUAL_HEIGHT:
                c = d.get("color") or dust_default
                pygame.draw.circle(self._particles_surface, (*c, alpha), (px, py), d["radius"])
                
        surface.blit(self._particles_surface, (0, 0))

    def _render_entities(self, surface: pygame.Surface, cam_x: float, cam_y: float, phase: str) -> None:
        for t in self.falling_traps: t.render(surface, cam_x, cam_y)
        for e in self.elevators: e.render(surface, cam_x, cam_y)
        for s in self.saw_hazards: s.render(surface, cam_x, cam_y)
        for a in self.altars: a.render(surface, cam_x, cam_y)
        for enemy in self.enemies: enemy.render(surface, cam_x, cam_y)

        for orb in self.health_orbs:
            orb.render(surface, cam_x, cam_y)
            
        for p in self.enemy_projectiles:
            px, py = int(p["x"] - cam_x), int(p["y"] - cam_y)
            for tr in p.get("trail", []):
                self._trail_surf.fill((0,0,0,0))
                pygame.draw.ellipse(self._trail_surf, (*p.get("color", (255, 120, 40))[:3], int(180 * (tr["life"] / 0.14))), (0, 0, 8, 6))
                surface.blit(self._trail_surf, (int(tr["x"] - cam_x) - 4, int(tr["y"] - cam_y) - 3))
                
            surface.blit(self._bullet_surf, (px - 7, py - 4))

        self.player.render(surface, cam_x, cam_y)
        
        if hasattr(self, "crumbling_blocks") and self.crumbling_blocks:
            tex = settings.TEXTURES.get("destructible_block")
            frames = settings.FRAMES.get("destructible_block", [])
            if tex and frames:
                idle_surf = tex.subsurface(frames[0])
                for b in self.crumbling_blocks:
                    shaking = b["timer"] < 1.2
                    offset_x = random.uniform(-2, 2) if shaking else 0.0
                    offset_y = random.uniform(-1, 1) if shaking else 0.0
                    surface.blit(idle_surf, (b["x"] - cam_x + offset_x, b["y"] - cam_y + offset_y))

        if self.rising_hazard: self.rising_hazard.render_world(surface, cam_x, cam_y, phase)
        if self.arena: self.arena.render(surface, cam_x, cam_y)

    def _render_ui(self, surface: pygame.Surface, cam_x: float, cam_y: float) -> None:
        for p in self.damage_popups:
            render_text(surface, p["text"], settings.FONTS["hud"], int(p["x"] - cam_x), int(p["y"] - cam_y), p["color"], center=True, shadowed=True)
            
        for a in self.altars: a.render_ui(surface)
            
        if self.rising_hazard: self.rising_hazard.render_hud(surface, self.player)
        if self.arena: self.arena.render_hud(surface)