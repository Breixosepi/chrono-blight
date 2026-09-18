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
        
        self.is_survival = (self.room.map_name == "sala_past")
        self.survival_time = 80.0
        self.max_survival_time = 80.0
        
        self.banner_text = ""
        self.banner_color = (255, 230, 80)
        self._banner_timer: Optional[After] = None
        
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
            "boss": (48.0, 95.0),
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
                    elif "center" in obj_name:
                        spawns["center"] = (float(obj["x"]), float(obj["y"]))
                    elif "boss" in obj_name:
                        spawns["boss"] = (float(obj["x"]), float(obj["y"]))
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
        settings.stop_music("ambient")
        self.barrier_active = True
        settings.SOUNDS["close"].play()
        self.room.camera.shake(4.5, 0.4)

        if self.is_survival:
            settings.play_music("boss_survive")
            self.state = "intro_delay"
            self._show_banner("¡LA LAVA VA SUBIENDO!", (255, 120, 80), 3.0)
            Timer.after(1.5, lambda: setattr(self.room, "lava_rising", True))
            Timer.after(3.0, self._start_survival_active)
        else:
            boss_track = "final_boss" if self.room.map_name == "big_room" else "giant_boss"
            settings.play_music(boss_track)
            self.state = "active"
            self.boss_phase = 1
            self.lava_shower.reset()
            pos_boss = self.spawn_positions.get("right", (464.0, 128.0))
            self.boss = self.spawn_enemy("cultist_priest", pos_boss[0], pos_boss[1], is_boss=True)
            if self.boss:
                self.boss.facing = "left"
                self.boss.change_state("chase")
            self.spawn_minions_for_phase(1)
            self._show_banner("¡SUMO SACERDOTE DEL VACÍO!", (255, 100, 200), 3.0)

    def _start_survival_active(self) -> None:
        self.state = "active"
        self.boss_phase = 1
        pos_boss = self.spawn_positions.get("boss", (48.0, 95.0))
        self.boss = self.spawn_enemy("monster2_boss", pos_boss[0], pos_boss[1], is_boss=True)
        if self.boss:
            self.boss.facing = "right"
            self.boss.shield_active = True
            self.boss.change_state("idle", cooldown=1.5)
        self._show_banner("¡EL ACECHADOR TEMPORAL!", (120, 255, 180), 3.0)

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
            enemy.shield_active = True
            enemy.boss_phase = 1
            if enemy_type == "cultist_priest":
                enemy._max_health = 220.0
                enemy.health = 220.0
                enemy.attack_cooldown = 2.4
                enemy.walk_speed = 0.0
            elif enemy_type == "monster2_boss":
                enemy._max_health = 80.0
                enemy.health = 80.0
                enemy.attack_cooldown = 2.2
                enemy.walk_speed = 0.0
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
        if self.boss:
            self.boss.boss_phase = new_phase
            self.boss.shield_active = True
            self.boss.attack_cooldown = 2.0
            self.boss.change_state("idle", cooldown=1.2)

        self._show_banner(banner_text, banner_color, 2.6)
        self.room.camera.shake(shake_intensity, 0.45)

        if not self.is_survival:
            for en in list(self.room.enemies):
                if en != self.boss and not en.dead:
                    en.dead = True
                    en.change_state("death")

            self.spawn_minions_for_phase(new_phase)
            Timer.after(2.4, lambda: self.boss.change_state("chase") if self.boss and not self.boss.dead else None)

    def on_arena_cleared(self) -> None:
        settings.stop_music("boss_survive")
        settings.stop_music("giant_boss")
        settings.stop_music("final_boss")
        if "lava" in settings.SOUNDS:
            settings.SOUNDS["lava"].stop()
        settings.SOUNDS["arena-cleared"].play()
        settings.play_music("ambient")
        
        self.state = "cleared"
        self.room.camera.shake(4.0, 0.4)
        if hasattr(self, "barrier_rect") and getattr(self, "barrier_rect", None):
            self.room.spawn_dust(self.barrier_rect.centerx, self.barrier_rect.bottom, count=16)
        elif getattr(self.room, "solid_blockers", None):
            for b in self.room.solid_blockers:
                self.room.spawn_dust(b.centerx, b.bottom, count=16)
        elif self.boss:
            self.room.spawn_dust(self.boss.hitbox.centerx, self.boss.hitbox.bottom, count=16)
        self.room.respawn_queue.clear()

        if self.is_survival:
            self._show_banner("¡SUPERVIVENCIA COMPLETADA!", (100, 255, 140), 3.5)
            if "lava" in settings.SOUNDS:
                settings.SOUNDS["lava"].stop()
            if getattr(self.room, "rising_hazard", None):
                self.room.rising_hazard.reset()
            if self.boss and not self.boss.dead:
                self.boss.shield_active = False
                self.boss.dead = True
                self.boss.change_state("death")
            if self.boss:
                self.boss.burst_hazards.clear()
                self.boss.side_shoots.clear()
            self.room.rising_hazard = None
            self.room.lava_rising = False
            for saw in self.room.saw_hazards:
                saw.stop()
            if hasattr(self.room, "play_state") and self.room.play_state:
                self.room.play_state.cleared_events.add("survival_boss_defeated")
                form_to_unlock = "sword"

        else:
            self._show_banner("¡SUMO SACERDOTE DERROTADO!", (100, 255, 140), 3.5)
            for en in list(self.room.enemies):
                if not en.dead:
                    en.dead = True
                    en.change_state("death")
            if hasattr(self.room, "play_state") and self.room.play_state:
                self.room.play_state.cleared_events.add("boss_cultist_defeated")
                form_to_unlock = "stats"

        # Delay unlock cutscene by 1.8s so the player can appreciate the defeat banner and boss death
        self.state = "clearing"
        def _trigger_unlock():
            if hasattr(self.room, "player") and not self.room.player.is_dead():
                self.state = "unlocking"
                self.room.player.change_state("unlock", form=form_to_unlock)
            else:
                self.on_unlock_finished()

        Timer.after(1.8, _trigger_unlock)

    def on_unlock_finished(self) -> None:
        self.state = "cleared"
        if hasattr(self.room, "elevators"):
            for elev in self.room.elevators:
                elev.activate()
        if hasattr(self.room, "_check_cleared_events"):
            self.room._check_cleared_events()

    def update(self, dt: float) -> None:
        if self.state == "inactive":
            if self.trigger_rect.colliderect(self.room.player.hitbox):
                self.start_arena()
            return

        if self.state == "active":
            if not self.is_survival:
                self.lava_shower.update(dt)

            self.room.respawn_queue.clear()

            if self.is_survival:
                if self.boss is not None and (self.boss.dead or self.boss.health <= 0 or getattr(self.boss, "state_name", "") == "death"):
                    if "lava" in settings.SOUNDS:
                        settings.SOUNDS["lava"].stop()
                    self.on_arena_cleared()
                    return

                self.survival_time -= dt
                if self.survival_time <= 0.0:
                    self.survival_time = 0.0
                    self.on_arena_cleared()
                    return

                if self.boss_phase == 1 and self.survival_time <= 55.0:
                    self._transition_to_phase(2, "¡FASE 2: DISPAROS TEMPORALES!", (255, 140, 60), 4.5)
                elif self.boss_phase == 2 and self.survival_time <= 30.0:
                    self._transition_to_phase(3, "¡FASE 3: COLAPSO TEMPORAL!", (255, 80, 80), 5.5)

            else:
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
        if self.state == "active" and not self.is_survival:
            self.lava_shower.render(surface, cam_x, cam_y)

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

            if self.is_survival:
                render_text(
                    surface,
                    f"SOBREVIVE: {int(self.survival_time)}s",
                    settings.FONTS["hud"],
                    settings.VIRTUAL_WIDTH // 2,
                    10,
                    (255, 120, 120),
                    center=True,
                    shadowed=True,
                )

                boss_name = "EL ACECHADOR TEMPORAL"
                phase_colors = {
                    1: ((100, 255, 180), (40, 180, 120)),
                    2: ((255, 150, 60), (200, 70, 20)),
                    3: ((255, 60, 90), (190, 20, 40)),
                }
                top_col, fill_col = phase_colors.get(self.boss_phase, ((100, 255, 180), (40, 180, 120)))
                progress_pct = max(0.0, min(1.0, self.survival_time / self.max_survival_time))
            else:
                boss_name = "SUMO SACERDOTE DEL VACÍO"
                phase_colors = {
                    1: ((240, 100, 220), (180, 40, 160)),
                    2: ((255, 150, 60), (200, 70, 20)),
                    3: ((255, 60, 90), (190, 20, 40)),
                }
                top_col, fill_col = phase_colors.get(self.boss_phase, ((240, 100, 220), (180, 40, 160)))
                progress_pct = max(0.0, min(1.0, self.boss.health / self.boss._max_health))

            render_text(
                surface,
                boss_name,
                settings.FONTS["hud"],
                settings.VIRTUAL_WIDTH // 2,
                by - 9,
                (240, 230, 255),
                center=True,
                shadowed=True,
            )

            bg_rect = pygame.Rect(bx - 2, by - 2, bar_w + 4, bar_h + 4)
            pygame.draw.rect(surface, (15, 10, 22), bg_rect)

            shield_border_col = (100, 255, 180) if self.is_survival else ((190, 80, 255) if self.boss.shield_active else (100, 30, 80))
            pygame.draw.rect(surface, shield_border_col, bg_rect, 1)

            fill_w = int(bar_w * progress_pct)
            if fill_w > 0:
                pygame.draw.rect(surface, fill_col, (bx, by, fill_w, bar_h))
                pygame.draw.rect(surface, top_col, (bx, by, fill_w, 2))

            tick_1 = bx + int(bar_w * (55.0 / 80.0 if self.is_survival else 0.70))
            tick_2 = bx + int(bar_w * (30.0 / 80.0 if self.is_survival else 0.30))
            pygame.draw.line(surface, (255, 230, 140, 180), (tick_1, by), (tick_1, by + bar_h - 1), 1)
            pygame.draw.line(surface, (255, 230, 140, 180), (tick_2, by), (tick_2, by + bar_h - 1), 1)