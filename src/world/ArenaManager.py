"""
Chrono Blight - Arena Manager
"""
import math
from typing import TYPE_CHECKING, Dict, Optional, Tuple
import pygame
from gale.text import render_text
from gale.timer import Timer, After

import settings
from src.definitions import entity as entity_defs
from src.entities.Enemy import Enemy
from src.entities.Boss import Boss
from src.world.LavaShower import LavaShower

if TYPE_CHECKING:
    from src.world.Room import Room

class ArenaManager:
    def __init__(self, room: "Room"):
        self.room = room
        self.state = "inactive"  
        self.boss_phase = 1      
        
        self.banner_text = ""
        self.banner_color = (255, 230, 80)
        self._banner_timer: Optional[After] = None
        
        self.barrier_active = False
        self.barrier_pulse = 0.0
        self.barrier_rect = pygame.Rect(16, 112, 16, 64)
        
        self.lava_shower = LavaShower(room)
        self.boss: Optional[Boss] = None
        self.spawn_positions = self._extract_spawn_positions()
        
        self.trigger_rect = pygame.Rect(72, 0, 2000, 2000)
        self._extract_trigger_rect()

    def _extract_trigger_rect(self) -> None:
        for layer in self.room.map_data.get("layers", []):
            if layer.get("type") == "objectgroup" or "objects" in layer:
                for obj in layer.get("objects", []):
                    if (obj.get("name", "") or "").lower().strip() == "arena_trigger":
                        self.trigger_rect = pygame.Rect(
                            int(obj.get("x", 0)),
                            int(obj.get("y", 0)),
                            int(obj.get("width", 16)),
                            int(obj.get("height", 16)),
                        )
                        return

    def _extract_spawn_positions(self) -> Dict[str, Tuple[float, float]]:
        spawns = {
            "left": (144.0, 128.0),
            "right": (464.0, 128.0),
            "center": (304.0, 128.0),
        }
        spawn_layer_names = {"spawns", "spwans", "arena_spawns", "enemies"}
        for layer in self.room.map_data.get("layers", []):
            if layer.get("name") in spawn_layer_names and "objects" in layer:
                for obj in layer["objects"]:
                    obj_name = (obj.get("name", "") or "").lower().strip()
                    if "left" in obj_name:
                        spawns["left"] = (float(obj["x"]), float(obj["y"]))
                    elif "right" in obj_name:
                        spawns["right"] = (float(obj["x"]), float(obj["y"]))
                    elif "center" in obj_name or "boss" in obj_name:
                        spawns["center"] = (float(obj["x"]), float(obj["y"]))
        return spawns

    def is_locked(self) -> bool:
        return self.state == "active"

    def _show_banner(self, text: str, color: Tuple[int, int, int], duration: float) -> None:
        self.banner_text = text
        self.banner_color = color
        if self._banner_timer:
            self._banner_timer.remove()
        self._banner_timer = Timer.after(duration, self._clear_banner)

    def _clear_banner(self) -> None:
        self.banner_text = ""
        self._banner_timer = None

    def start_arena(self) -> None:
        self.state = "active"
        self.barrier_active = True
        self.room.camera.shake(4.0, 0.35)
        self.boss_phase = 1
        self.lava_shower.reset()

        pos_boss = self.spawn_positions.get("right", (464.0, 128.0))
        self.boss = self.spawn_enemy("cultist_priest", pos_boss[0], pos_boss[1], is_boss=True)
        if self.boss:
            self.boss.facing = "left"
            self.boss.change_state("chase")

        self.spawn_minions_for_phase(1)
        self._show_banner("¡SUMO SACERDOTE DEL VACÍO!", (255, 100, 200), 3.0)

    def spawn_minions_for_phase(self, phase: int) -> None:
        pos_left = self.spawn_positions["left"]
        pos_center = self.spawn_positions["center"]
        if phase == 1:
            self.spawn_enemy("monster2", pos_left[0], pos_left[1])
            self.spawn_enemy("skeleton_sword", pos_left[0] + 48, pos_left[1])
            self.spawn_enemy("skeleton_sword", pos_center[0] - 24, pos_center[1])
        elif phase == 2:
            self.spawn_enemy("monster3", pos_left[0], pos_left[1])
            self.spawn_enemy("monster2", pos_center[0], pos_center[1])
        elif phase == 3:
            self.spawn_enemy("big_monster", pos_left[0] + 32, pos_left[1])
            self.spawn_enemy("monster3", pos_center[0], pos_center[1])

    def spawn_enemy(
        self,
        enemy_type: str,
        x: float,
        y: float,
        is_boss: bool = False,
    ) -> Optional[Enemy]:
        all_defs = {**entity_defs.ENEMY_DEFS, **entity_defs.BOSS_DEFS}
        if enemy_type not in all_defs:
            return None

        boss_types = set(entity_defs.BOSS_DEFS.keys())
        if is_boss or enemy_type in boss_types:
            enemy = Boss(
                x,
                y,
                enemy_type=enemy_type,
                floor_y=float(self.room.MAP_HEIGHT),
                map_w=float(self.room.MAP_WIDTH),
            )
            enemy.is_boss = True
            enemy._max_health = 220.0
            enemy.health = 220.0
            enemy.attack_cooldown = 2.4
            enemy.walk_speed = 0.0
            enemy.shield_active = True
            enemy.boss_phase = 1
        else:
            enemy = Enemy(
                x,
                y,
                enemy_type=enemy_type,
                floor_y=float(self.room.MAP_HEIGHT),
                map_w=float(self.room.MAP_WIDTH),
            )
            enemy.walk_speed *= 1.20
            enemy.attack_cooldown = max(0.5, enemy.attack_cooldown * 0.75)
            enemy._max_health = round(enemy._max_health * 1.05)
            enemy.health = enemy._max_health

        enemy.room = self.room
        enemy.player = self.room.player
        enemy.tilemap = self.room.tilemap
        enemy.active_collision_layers = self.room._get_enemy_collision_layers(enemy)
        enemy.on_hazard_hit = self.room._on_hazard_hit
        enemy.in_arena = True
        enemy.detect_range = 800.0

        self.room.enemies.append(enemy)
        return enemy

    def _transition_to_phase(
        self,
        new_phase: int,
        banner_text: str,
        banner_color: Tuple[int, int, int],
        shake_intensity: float,
    ) -> None:
        self.boss_phase = new_phase
        self.boss.boss_phase = new_phase
        self.boss.shield_active = True
        self.boss.attack_cooldown = 3.0
        self.boss.change_state("idle")

        self._show_banner(banner_text, banner_color, 2.6)
        self.room.camera.shake(shake_intensity, 0.45)

        for en in list(self.room.enemies):
            if en != self.boss and not en.dead:
                en.dead = True
                en.change_state("death")

        self.spawn_minions_for_phase(new_phase)

        Timer.after(2.4, lambda: self.boss.change_state("chase") if self.boss and not self.boss.dead else None)

    def on_arena_cleared(self) -> None:
        self.state = "cleared"
        self.barrier_active = False
        self._show_banner("¡SUMO SACERDOTE DERROTADO!", (100, 255, 140), 3.5)
        self.room.camera.shake(4.0, 0.4)
        self.room.spawn_dust(self.barrier_rect.centerx, self.barrier_rect.bottom, count=16)
        self.room.respawn_queue.clear()

        for en in list(self.room.enemies):
            if not en.dead:
                en.dead = True
                en.change_state("death")

        if hasattr(self.room, "play_state") and self.room.play_state:
            self.room.play_state.cleared_events.add("boss_cultist_defeated")

        if hasattr(self.room, "elevators"):
            for elev in self.room.elevators:
                Timer.after(1.5, elev.activate)

    def update(self, dt: float) -> None:
        if self.state == "inactive":
            if self.trigger_rect.colliderect(self.room.player.hitbox):
                self.start_arena()
            return

        if self.state == "active":
            self.barrier_pulse += dt * 4.0
            self.lava_shower.update(dt)

            player = self.room.player
            if player.hitbox.left < 36:
                player.x = 36.0
                player.hitbox.x = 36
                player.vx = max(0.0, player.vx)

            self.room.respawn_queue.clear()

            if self.boss is None or self.boss.dead or self.boss.health <= 0:
                self.on_arena_cleared()
                return

            active_minions = [e for e in self.room.enemies if e != self.boss and not e.dead]
            if active_minions:
                self.boss.shield_active = True
            elif self.boss.shield_active:
                self.boss.shield_active = False
                self._show_banner("¡ESCUDO ROTO! ¡ATACA AL JEFE!", (255, 240, 90), 2.0)
                self.room.camera.shake(3.5, 0.25)
                self.room.spawn_dust(self.boss.hitbox.centerx, self.boss.hitbox.bottom, count=12)

            hp_pct = max(0.0, self.boss.health / self.boss._max_health)
            if self.boss_phase == 1 and hp_pct <= 0.70:
                self.boss.health = self.boss._max_health * 0.70
                self._transition_to_phase(2, "¡FASE 2: ORBES DEL VACÍO!", (255, 140, 60), 5.0)
            elif self.boss_phase == 2 and hp_pct <= 0.30:
                self.boss.health = self.boss._max_health * 0.30
                self._transition_to_phase(3, "¡FASE 3: DESATAR EL VACÍO!", (255, 80, 80), 6.0)

    def render(self, surface: pygame.Surface, cam_x: float, cam_y: float) -> None:
        if self.state == "active":
            self.lava_shower.render(surface, cam_x, cam_y)

        if not self.barrier_active:
            return

        bx = int(self.barrier_rect.x - cam_x)
        by = int(self.barrier_rect.y - cam_y)
        bw = self.barrier_rect.width
        bh = self.barrier_rect.height

        alpha = int(170 + 60 * math.sin(self.barrier_pulse))
        barrier_surf = pygame.Surface((bw, bh), pygame.SRCALPHA)
        pygame.draw.rect(barrier_surf, (180, 50, 220, alpha // 2), (0, 0, bw, bh))

        for y_offset in range(4, bh, 8):
            line_alpha = min(255, alpha + 30)
            pygame.draw.line(barrier_surf, (240, 120, 255, line_alpha), (2, y_offset), (bw - 2, y_offset), 2)

        pygame.draw.rect(barrier_surf, (255, 200, 255, alpha), (0, 0, bw, bh), 2)
        surface.blit(barrier_surf, (bx, by))

    def render_hud(self, surface: pygame.Surface) -> None:
        if self.banner_text:
            render_text(
                surface,
                self.banner_text,
                settings.FONTS["title"],
                settings.VIRTUAL_WIDTH // 2,
                24,
                self.banner_color,
                center=True,
                shadowed=True,
            )

        if self.boss is not None and not self.boss.dead and self.state == "active":
            bar_w = 180
            bar_h = 7
            bx = (settings.VIRTUAL_WIDTH - bar_w) // 2
            by = settings.VIRTUAL_HEIGHT - 16

            phase_colors = {
                1: ((240, 100, 220), (180, 40, 160)),
                2: ((255, 150, 60), (200, 70, 20)),
                3: ((255, 60, 90), (190, 20, 40)),
            }
            top_col, fill_col = phase_colors.get(self.boss_phase, ((240, 100, 220), (180, 40, 160)))

            render_text(
                surface,
                "SUMO SACERDOTE DEL VACÍO",
                settings.FONTS["hud"],
                settings.VIRTUAL_WIDTH // 2,
                by - 9,
                (240, 230, 255),
                center=True,
                shadowed=True,
            )

            bg_rect = pygame.Rect(bx - 2, by - 2, bar_w + 4, bar_h + 4)
            pygame.draw.rect(surface, (15, 10, 22), bg_rect)

            shield_border_col = (190, 80, 255) if self.boss.shield_active else (100, 30, 80)
            pygame.draw.rect(surface, shield_border_col, bg_rect, 1)

            hp_pct = max(0.0, min(1.0, self.boss.health / self.boss._max_health))
            fill_w = int(bar_w * hp_pct)
            if fill_w > 0:
                pygame.draw.rect(surface, fill_col, (bx, by, fill_w, bar_h))
                pygame.draw.rect(surface, top_col, (bx, by, fill_w, 2))

            tick_70 = bx + int(bar_w * 0.70)
            tick_30 = bx + int(bar_w * 0.30)
            pygame.draw.line(surface, (255, 230, 140, 180), (tick_70, by), (tick_70, by + bar_h - 1), 1)
            pygame.draw.line(surface, (255, 230, 140, 180), (tick_30, by), (tick_30, by + bar_h - 1), 1)