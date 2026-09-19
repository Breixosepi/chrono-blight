from typing import Optional
import pygame
import random
import math
import pathlib
from gale.text import render_text

import settings


class RoomRenderer:
    def __init__(self, room):
        self.room = room
        self.bg_surfaces = {}
        self._tile_cache = {}
        self._ghost_tile_cache = {}
        
        self._particles_surface = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
        self._bullet_surf = pygame.Surface((14, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(self._bullet_surf, (255, 100, 30, 220), (0, 0, 14, 8))
        pygame.draw.ellipse(self._bullet_surf, (255, 250, 180, 255), (3, 1, 8, 6))
        
        self._trail_surf = pygame.Surface((8, 6), pygame.SRCALPHA)
        
        tex = settings.TEXTURES.get("destructible_block")
        frames = settings.FRAMES.get("destructible_block", [])
        if tex and frames:
            self._brick_tile = pygame.transform.scale(tex.subsurface(frames[0]), (self.room.TILE_SIZE, self.room.TILE_SIZE))
        else:
            self._brick_tile = pygame.Surface((self.room.TILE_SIZE, self.room.TILE_SIZE))
            self._brick_tile.fill((120, 110, 100))

    def init_graphics(self, map_data):
        props = self.room._parse_props(map_data)
        bg_configs = [
            ("green", props.get("bg_past", f"{self.room.map_name}_past"), f"{self.room.map_name}_past", (8, 16, 20, 130)),
            ("red", props.get("bg_future", f"{self.room.map_name}_future"), f"{self.room.map_name}_future", (22, 10, 14, 135)),
        ]
        for phase, target, fallback, wash_color in bg_configs:
            raw_bg = self._load_background_image(target) or self._load_background_image(fallback)
            if raw_bg:
                bg = raw_bg.copy()
                wash = pygame.Surface(bg.get_size(), pygame.SRCALPHA)
                wash.fill(wash_color)
                bg.blit(wash, (0, 0))
                self.bg_surfaces[phase] = bg

    def _load_background_image(self, candidate_name: str) -> Optional[pygame.Surface]:
        if not candidate_name: 
            return None
        if candidate_name in settings.TEXTURES: 
            return settings.TEXTURES[candidate_name]
        
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

    def _get_tile_surface(self, gid: int, flip_h: bool, flip_v: bool, flip_d: bool, ghost: bool) -> Optional[pygame.Surface]:
        clean_gid = gid & 0x1FFFFFFF
        key = (clean_gid, flip_h, flip_v, flip_d)
        cache = self._ghost_tile_cache if ghost else self._tile_cache
        if key in cache: return cache[key]
        
        tileset = self.room.tilemap.tileset_for_gid(clean_gid)
        if not tileset: return None
        
        try:
            sub = tileset.image.subsurface(tileset.rect_for(clean_gid))
        except (IndexError, ValueError):
            return None
        if flip_d: sub = pygame.transform.flip(pygame.transform.rotate(sub, 270), True, False)
        if flip_h or flip_v: sub = pygame.transform.flip(sub, flip_h, flip_v)
        
        if ghost:
            ghost_surf = pygame.Surface(sub.get_size(), pygame.SRCALPHA)
            ghost_surf.blit(sub, (0, 0))
            ghost_surf.fill((255, 255, 255, 75), special_flags=pygame.BLEND_RGBA_MULT)
            cache[key] = ghost_surf
            return ghost_surf
            
        cache[key] = sub
        return sub

    def _render_layer(self, layer_name: str, surface: pygame.Surface, cam_x: float, cam_y: float, ghost: bool = False) -> None:
        if layer_name not in self.room.tilemap.layer_names(): return
        
        min_col = max(0, int(cam_x // self.room.TILE_SIZE))
        min_row = max(0, int(cam_y // self.room.TILE_SIZE))
        max_col = min(self.room.MAP_COLS - 1, int((cam_x + settings.VIRTUAL_WIDTH) // self.room.TILE_SIZE) + 1)
        max_row = min(self.room.MAP_ROWS - 1, int((cam_y + settings.VIRTUAL_HEIGHT) // self.room.TILE_SIZE) + 1)
        
        grid = self.room.tilemap.get_layer(layer_name)
        for row in range(min_row, max_row + 1):
            for col in range(min_col, max_col + 1):
                gid = grid[row][col]
                if gid == 0: continue
                
                flip_h, flip_v, flip_d = self.room.flipped_tiles.get((layer_name, row, col), (False, False, False))
                tile_surf = self._get_tile_surface(gid, flip_h, flip_v, flip_d, ghost=ghost)
                if tile_surf:
                    surface.blit(tile_surf, (col * self.room.TILE_SIZE - cam_x, row * self.room.TILE_SIZE - cam_y))

    def render(self, surface: pygame.Surface) -> None:
        cam_x, cam_y = self.room.camera_offset
        phase = self.room.player.phase_color
        surface.fill((10, 10, 15))

        self._render_environment(surface, cam_x, cam_y, phase)
        self._render_vfx_background(surface, cam_x, cam_y, phase)
        self._render_entities(surface, cam_x, cam_y, phase)
        self._render_ui(surface, cam_x, cam_y)

    def _render_environment(self, surface: pygame.Surface, cam_x: float, cam_y: float, phase: str) -> None:
        bg_surf = self.bg_surfaces.get(phase, settings.TEXTURES.get(f"{self.room.map_name}_{'past' if phase == 'green' else 'future'}"))
        if bg_surf:
            bg_w, bg_h = bg_surf.get_size()
            if bg_w < self.room.MAP_WIDTH:
                scroll_x = -int(cam_x * 0.4) % bg_w - bg_w
                scroll_y = -cam_y if bg_h >= self.room.MAP_HEIGHT else -int(cam_y * 0.3)
                curr_x = scroll_x
                while curr_x < settings.VIRTUAL_WIDTH:
                    surface.blit(bg_surf, (curr_x, scroll_y))
                    curr_x += bg_w
            else:
                surface.blit(bg_surf, (-cam_x, -cam_y))

        self._render_layer("background", surface, cam_x, cam_y)
        self._render_layer("ground", surface, cam_x, cam_y)
        self._render_layer("decoration", surface, cam_x, cam_y)

        active_pfx, inactive_pfx = ("green", "red") if phase == "green" else ("red", "green")
        self._render_layer(f"{active_pfx}_background", surface, cam_x, cam_y)
        self._render_layer(f"{active_pfx}_ground", surface, cam_x, cam_y)
        self._render_layer(f"{active_pfx}_decoration", surface, cam_x, cam_y)
        self._render_layer(f"{inactive_pfx}_ground", surface, cam_x, cam_y, ghost=True)

        if self.room.solid_blockers and self._brick_tile:
            ground_grid = self.room.tilemap.get_layer("ground") if "ground" in self.room.tilemap.layer_names() else None
            for rect in self.room.solid_blockers:
                for bx in range(rect.left, rect.right, self.room.TILE_SIZE):
                    for by in range(rect.top, rect.bottom, self.room.TILE_SIZE):
                        col = bx // self.room.TILE_SIZE
                        row = by // self.room.TILE_SIZE
                        has_tile = False
                        if ground_grid and 0 <= row < self.room.MAP_ROWS and 0 <= col < self.room.MAP_COLS:
                            has_tile = (ground_grid[row][col] != 0)
                        if not has_tile:
                            surface.blit(self._brick_tile, (bx - cam_x, by - cam_y))

    def _render_vfx_background(self, surface: pygame.Surface, cam_x: float, cam_y: float, phase: str) -> None:
        self._particles_surface.fill((0, 0, 0, 0))
        part_col = (120, 255, 190) if phase == "green" else (255, 135, 80)
        
        for p in self.room.particle_system.ambient_particles:
            px, py = int(p["x"] - cam_x), int(p["y"] - cam_y)
            if 0 <= px < settings.VIRTUAL_WIDTH and 0 <= py < settings.VIRTUAL_HEIGHT:
                pygame.draw.circle(self._particles_surface, (*part_col, p["alpha"]), (px, py), p["radius"])

        dust_default = (140, 240, 190) if phase == "green" else (240, 150, 130)
        for d in self.room.particle_system.dust_particles:
            px, py = int(d["x"] - cam_x), int(d["y"] - cam_y)
            alpha = int(220 * max(0.0, min(1.0, d["life"] / d["max_life"])))
            if 0 <= px < settings.VIRTUAL_WIDTH and 0 <= py < settings.VIRTUAL_HEIGHT:
                c = d.get("color") or dust_default
                pygame.draw.circle(self._particles_surface, (*c, alpha), (px, py), d["radius"])
                
        surface.blit(self._particles_surface, (0, 0))

    def _render_entities(self, surface: pygame.Surface, cam_x: float, cam_y: float, phase: str) -> None:
        for t in self.room.falling_traps: t.render(surface, cam_x, cam_y)
        for e in self.room.elevators: e.render(surface, cam_x, cam_y)
        for s in self.room.saw_hazards: s.render(surface, cam_x, cam_y)
        for a in self.room.altars: a.render(surface, cam_x, cam_y)
        for enemy in self.room.enemies: enemy.render(surface, cam_x, cam_y)

        for orb in self.room.health_orbs:
            orb.render(surface, cam_x, cam_y)
            
        for p in self.room.enemy_projectiles:
            px, py = int(p["x"] - cam_x), int(p["y"] - cam_y)
            for tr in p.get("trail", []):
                self._trail_surf.fill((0,0,0,0))
                pygame.draw.ellipse(self._trail_surf, (*p.get("color", (255, 120, 40))[:3], int(180 * (tr["life"] / 0.14))), (0, 0, 8, 6))
                surface.blit(self._trail_surf, (int(tr["x"] - cam_x) - 4, int(tr["y"] - cam_y) - 3))
                
            surface.blit(self._bullet_surf, (px - 7, py - 4))

        self.room.player.render(surface, cam_x, cam_y)
        
        if hasattr(self.room, "crumbling_blocks") and self.room.crumbling_blocks:
            tex = settings.TEXTURES.get("destructible_block")
            frames = settings.FRAMES.get("destructible_block", [])
            if tex and frames:
                idle_surf = tex.subsurface(frames[0])
                for b in self.room.crumbling_blocks:
                    shaking = b["timer"] < 1.2
                    offset_x = random.uniform(-2, 2) if shaking else 0.0
                    offset_y = random.uniform(-1, 1) if shaking else 0.0
                    surface.blit(idle_surf, (b["x"] - cam_x + offset_x, b["y"] - cam_y + offset_y))

        if self.room.rising_hazard: self.room.rising_hazard.render_world(surface, cam_x, cam_y, phase)
        if self.room.arena: self.room.arena.render(surface, cam_x, cam_y)

    def _render_ui(self, surface: pygame.Surface, cam_x: float, cam_y: float) -> None:
        for a in self.room.altars: a.render_ui(surface)
        if self.room.rising_hazard: self.room.rising_hazard.render_hud(surface, self.room.player)

    def render_top_ui(self, surface: pygame.Surface) -> None:
        cam_x, cam_y = self.room.camera_offset
        if self.room.arena:
            self.room.arena.render_hud(surface)
        if self.room.player.state_name == "unlock":
            curr_state = self.room.player.state_machine.current
            if hasattr(curr_state, "render_banner"):
                curr_state.render_banner(surface)
        for p in self.room.damage_popups:
            render_text(surface, p["text"], settings.FONTS["hud"], int(p["x"] - cam_x), int(p["y"] - cam_y), p["color"], center=True, shadowed=True)

