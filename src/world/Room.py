"""
Chrono Blight - World Room Component
"""

from typing import List
import pygame

from gale.camera import Camera
from gale.text import render_text

import settings
from src.definitions import entity as entity_defs
from src.entities.Player import Player
from src.entities.Enemy import Enemy


class Room:

    TILE_SIZE: int = settings.TILE_SIZE
    MAP_COLS: int = 78
    MAP_ROWS: int = 13
    MAP_WIDTH: int = MAP_COLS * TILE_SIZE    # 1248 px
    MAP_HEIGHT: int = MAP_ROWS * TILE_SIZE   # 208 px
    FLOOR_ROW: int = 10
    FLOOR_Y: float = float(FLOOR_ROW * TILE_SIZE)

    def __init__(self) -> None:
        self.camera = Camera(
            settings.VIRTUAL_WIDTH,
            settings.VIRTUAL_HEIGHT,
            bounds=pygame.Rect(0, 0, self.MAP_WIDTH, self.MAP_HEIGHT),
        )

        spawn_x = 48.0
        spawn_y = float(self.FLOOR_Y - entity_defs.PLAYER_HIT_H)
        self.player = Player(spawn_x, spawn_y, floor_y=self.FLOOR_Y, map_w=float(self.MAP_WIDTH))

        self.camera.x = self.player.hitbox.centerx
        self.camera.y = self.player.hitbox.centery
        self.camera.update(0.0)

        self._init_enemies()
        self._init_graphics()

        # Tracking de golpes por swing
        self._hit_this_swing: set = set()
        self._flame_hits: set = set()
        self._prev_attack_state: bool = False
        self.damage_popups: list[dict] = []
        self.respawn_queue: list[dict] = []

    @property
    def camera_offset(self) -> tuple[float, float]:
        ox, oy = self.camera.offset
        return (round(ox), round(oy))

    def _init_enemies(self) -> None:
        floor_y = self.FLOOR_Y
        map_w = float(self.MAP_WIDTH)

        self.enemies: List[Enemy] = []

        spawn_configs = [
            ("skeleton_sword", 160.0),  
            ("monster_eyes",   280.0),  
            ("goblin",         420.0),  
            ("crown",          560.0), 
            ("big_monster",    720.0),  
            ("monster2",       860.0),  
            ("monster3",      1000.0),  
            ("cultist_priest",1120.0),  
        ]

        for enemy_type, x_pos in spawn_configs:
            h = entity_defs.ENEMY_DEFS[enemy_type]["hitbox"]["height"]
            enemy = Enemy(
                x=x_pos,
                y=float(floor_y - h),
                enemy_type=enemy_type,
                floor_y=floor_y,
                map_w=map_w,
            )
            enemy.player = self.player
            enemy.on_hazard_hit = self._on_hazard_hit
            self.enemies.append(enemy)

    def _on_hazard_hit(self, hazard: dict) -> None:
        self.camera.shake(2.0, 0.15)
        self.damage_popups.append({
            "text": f"-{int(hazard['damage'])}",
            "x": hazard["hitbox"].centerx,
            "y": hazard["hitbox"].top - 6,
            "timer": 0.6,
            "color": (255, 60, 60),
        })

    def _create_radial_glow(self, radius: int, color_rgb: tuple, max_alpha: int = 40) -> pygame.Surface:
        surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        for r in range(radius, 0, -2):
            alpha = int(max_alpha * (1.0 - (r / radius) ** 1.5))
            pygame.draw.circle(surf, (*color_rgb, alpha), (radius, radius), r)
        return surf

    def _init_graphics(self) -> None:
        sky_h = int(self.FLOOR_Y)
        self.sky_surfaces = {}

        palettes = {
            "red":   ((42, 28, 36), (78, 50, 62)),
            "green": ((20, 30, 46), (50, 72, 102)),
        }
        for phase, (top_col, bot_col) in palettes.items():
            sky = pygame.Surface((self.MAP_WIDTH, sky_h))
            for y in range(sky_h):
                t = y / max(1, sky_h)
                r = int(top_col[0] + (bot_col[0] - top_col[0]) * t)
                g = int(top_col[1] + (bot_col[1] - top_col[1]) * t)
                b = int(top_col[2] + (bot_col[2] - top_col[2]) * t)
                pygame.draw.line(sky, (r, g, b), (0, y), (self.MAP_WIDTH, y))
            self.sky_surfaces[phase] = sky

        self.glow_surfaces = {
            "red":   self._create_radial_glow(36, (255, 100, 100), max_alpha=40),
            "green": self._create_radial_glow(36, (70, 230, 140), max_alpha=45),
        }

    def update(self, dt: float) -> None:
        self.player.update(dt)

        self.camera.x = self.player.hitbox.centerx
        self.camera.y = self.player.hitbox.centery
        self.camera.update(dt)

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
                    floor_y=self.FLOOR_Y,
                    map_w=float(self.MAP_WIDTH),
                )
                new_enemy.player = self.player
                new_enemy.on_hazard_hit = self._on_hazard_hit
                self.enemies.append(new_enemy)
                self.damage_popups.append({
                    "text": "RESPAWN!",
                    "x": new_enemy.hitbox.centerx,
                    "y": new_enemy.hitbox.top - 10,
                    "timer": 0.8,
                    "color": (120, 255, 160),
                })

    def _resolve_combat(self, enemy: Enemy) -> None:
        player = self.player
        if player.state_name == "death":
            return

        # Jugador -> Enemigo (Ataque cuerpo a cuerpo / magia directa)
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
                self.damage_popups.append({
                    "text": f"-{dmg}",
                    "x": enemy.hitbox.centerx,
                    "y": enemy.hitbox.top - 6,
                    "timer": 0.5,
                    "color": (255, 230, 80),
                })
            elif not enemy.is_active() and hit_key not in self._hit_this_swing:
                self._hit_this_swing.add(hit_key)
                self.damage_popups.append({
                    "text": "IMMUNE",
                    "x": enemy.hitbox.centerx,
                    "y": enemy.hitbox.top - 6,
                    "timer": 0.4,
                    "color": (160, 190, 255),
                })

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
                    self.damage_popups.append({
                        "text": f"-{dmg}",
                        "x": enemy.hitbox.centerx,
                        "y": enemy.hitbox.top - 8,
                        "timer": 0.5,
                        "color": (255, 130, 40),
                    })

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
            self.damage_popups.append({
                "text": f"-{dmg}",
                "x": player.hitbox.centerx,
                "y": player.hitbox.top - 8,
                "timer": 0.6,
                "color": (255, 75, 75),
            })

    def _resolve_enemy_collisions(self) -> None:
        mass_table = {
            "big_monster":   3.5,
            "cultist_priest": 2.5,
            "monster3":       1.4,
            "skeleton_sword": 1.2,
            "monster_eyes":   1.0,
            "goblin":         0.9,
            "monster2":       0.85,
            "crown":          0.8,
        }

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
                        m1 = mass_table.get(e1.enemy_type, 1.0)
                        m2 = mass_table.get(e2.enemy_type, 1.0)
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

    def render(self, surface: pygame.Surface) -> None:
        cam_x, cam_y = self.camera_offset
        phase = self.player.phase_color

        if phase == "red":
            ground_top_color  = (175, 95, 95)
            ground_body_color = (65, 45, 54)
            grid_line_color   = (90, 60, 72)
            wall_color        = (130, 65, 65)
        else:
            ground_top_color  = (95, 155, 205)
            ground_body_color = (36, 52, 74)
            grid_line_color   = (52, 75, 105)
            wall_color        = (60, 100, 150)

        surface.fill((10, 10, 15))

        room_screen_x = int(0 - cam_x)
        room_screen_y = int(0 - cam_y)
        sky_surf = self.sky_surfaces.get(phase)
        if sky_surf:
            surface.blit(sky_surf, (room_screen_x, room_screen_y))

        pygame.draw.rect(surface, wall_color, pygame.Rect(room_screen_x, room_screen_y, 4, self.MAP_HEIGHT))
        pygame.draw.rect(surface, wall_color, pygame.Rect(room_screen_x + self.MAP_WIDTH - 4, room_screen_y, 4, self.MAP_HEIGHT))

        floor_screen_y = int(self.FLOOR_Y - cam_y)
        floor_height   = self.MAP_HEIGHT - int(self.FLOOR_Y)
        floor_rect     = pygame.Rect(room_screen_x, floor_screen_y, self.MAP_WIDTH, floor_height)
        pygame.draw.rect(surface, ground_body_color, floor_rect)
        pygame.draw.line(surface, ground_top_color, (room_screen_x, floor_screen_y), (room_screen_x + self.MAP_WIDTH, floor_screen_y), 2)

        start_col = max(0, int(cam_x // self.TILE_SIZE))
        end_col   = min(self.MAP_COLS, int((cam_x + settings.VIRTUAL_WIDTH) // self.TILE_SIZE) + 2)
        for col in range(start_col, end_col):
            tile_screen_x = int(col * self.TILE_SIZE - cam_x)
            pygame.draw.line(surface, grid_line_color, (tile_screen_x, floor_screen_y), (tile_screen_x, floor_screen_y + floor_height), 1)
            sub_y = floor_screen_y + self.TILE_SIZE
            pygame.draw.line(surface, grid_line_color, (tile_screen_x, sub_y), (tile_screen_x + self.TILE_SIZE, sub_y), 1)

        glow_surf = self.glow_surfaces.get(phase)
        if glow_surf:
            player_center_x = int(self.player.hitbox.centerx - cam_x)
            player_center_y = int(self.player.hitbox.centery - cam_y)
            surface.blit(glow_surf, (player_center_x - 36, player_center_y - 36))

        for enemy in self.enemies:
            enemy.render(surface, cam_x, cam_y)

        self.player.render(surface, cam_x, cam_y)

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

