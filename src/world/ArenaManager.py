import math
import random
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

import pygame
from gale.text import render_text
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
        self.state = "inactive"  # "inactive", "active", "cleared"
        self.boss_phase = 1  # 1: 100%-70%, 2: 70%-30%, 3: 30%-0%
        self.phase_transition_timer = 0.0

        self.banner_text = ""
        self.banner_timer = 0.0
        self.banner_color = (255, 230, 80)

        self.barrier_active = False
        self.barrier_pulse = 0.0
        self.barrier_rect = pygame.Rect(16, 112, 16, 64)

        # Peligro ambiental: cascadas de lava desde el techo
        self.lava_shower = LavaShower(room)

        # Control del Jefe Cultista
        self.boss: Optional[Enemy] = None

        # Detectar posiciones de spawn de arena desde Tiled
        self.spawn_positions = self._extract_spawn_positions()

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

    def start_arena(self) -> None:
        self.state = "active"
        self.barrier_active = True
        self.room.camera.shake(4.0, 0.35)
        self.boss_phase = 1
        self.lava_shower.reset()

        # Generar Jefe Cultista en la esquina derecha protegido por su escudo
        pos_boss = self.spawn_positions.get("right", (464.0, 128.0))
        self.boss = self.spawn_enemy("cultist_priest", pos_boss[0], pos_boss[1], is_boss=True)
        if self.boss:
            self.boss.facing = "left"
            self.boss._max_health = 220.0
            self.boss.health = 220.0
            self.boss.attack_cooldown = 2.4
            self.boss.boss_phase = 1
            self.boss.shield_active = True
            self.boss.change_state("chase")

        # Generar esbirros de Fase 1
        self.spawn_minions_for_phase(1)

        self.banner_text = "¡SUMO SACERDOTE DEL VACÍO!"
        self.banner_color = (255, 100, 200)
        self.banner_timer = 3.0

    def spawn_minions_for_phase(self, phase: int) -> None:
        pos_left = self.spawn_positions["left"]
        pos_center = self.spawn_positions["center"]

        if phase == 1:
            # 3 esbirros: 1 pistolero y 2 esqueletos
            self.spawn_enemy("monster2", pos_left[0], pos_left[1])
            self.spawn_enemy("skeleton_sword", pos_left[0] + 48, pos_left[1])
            self.spawn_enemy("skeleton_sword", pos_center[0] - 24, pos_center[1])
        elif phase == 2:
            # 2 esbirros: 1 imp y 1 pistolero
            self.spawn_enemy("monster3", pos_left[0], pos_left[1])
            self.spawn_enemy("monster2", pos_center[0], pos_center[1])
        elif phase == 3:
            # 2 esbirros: 1 Root Golem y 1 imp
            self.spawn_enemy("big_monster", pos_left[0] + 32, pos_left[1])
            self.spawn_enemy("monster3", pos_center[0], pos_center[1])

    def spawn_enemy(
        self,
        enemy_type: str,
        x: float,
        y: float,
        is_boss: bool = False,
    ) -> Enemy:
        # Verificar si existe la definición en ENEMY_DEFS o BOSS_DEFS
        all_defs = {**entity_defs.ENEMY_DEFS, **entity_defs.BOSS_DEFS}
        if enemy_type not in all_defs:
            return None

        # Usar Boss para los jefes, Enemy para los enemigos regulares
        boss_types = set(entity_defs.BOSS_DEFS.keys())
        if is_boss or enemy_type in boss_types:
            enemy = Boss(
                x,
                y,
                enemy_type=enemy_type,
                floor_y=float(self.room.MAP_HEIGHT),
                map_w=float(self.room.MAP_WIDTH),
            )
        else:
            enemy = Enemy(
                x,
                y,
                enemy_type=enemy_type,
                floor_y=float(self.room.MAP_HEIGHT),
                map_w=float(self.room.MAP_WIDTH),
            )
        enemy.room = self.room
        enemy.player = self.room.player
        enemy.tilemap = self.room.tilemap
        enemy.active_collision_layers = self.room._get_enemy_collision_layers(enemy)
        enemy.on_hazard_hit = self.room._on_hazard_hit

        enemy.in_arena = True
        enemy.detect_range = 800.0

        if is_boss or enemy_type in boss_types:
            enemy.is_boss = True
            enemy._max_health = 220.0
            enemy.health = 220.0
            enemy.attack_cooldown = 2.4
            enemy.walk_speed = 0.0
            enemy.shield_active = True
        else:
            enemy.walk_speed *= 1.20
            enemy.attack_cooldown = max(0.5, enemy.attack_cooldown * 0.75)
            enemy._max_health = round(enemy._max_health * 1.05)
            enemy.health = enemy._max_health

        self.room.enemies.append(enemy)
        return enemy

    def on_arena_cleared(self) -> None:
        self.state = "cleared"
        self.barrier_active = False
        self.banner_text = "¡SUMO SACERDOTE DERROTADO!"
        self.banner_color = (100, 255, 140)
        self.banner_timer = 3.5
        self.room.camera.shake(4.0, 0.4)
        self.room.spawn_dust(self.barrier_rect.centerx, self.barrier_rect.bottom, count=16)
        self.room.respawn_queue.clear()

        # Destruir cualquier esbirro restante de forma definitiva
        for en in list(self.room.enemies):
            if not en.dead:
                en.dead = True
                en.change_state("death")

    def update(self, dt: float) -> None:
        # 1. Trigger de inicio al adentrarse en la sala
        if self.state == "inactive":
            if self.room.player.hitbox.centerx >= 72.0:
                self.start_arena()
            return

        if self.banner_timer > 0.0:
            self.banner_timer -= dt

        # 2. Lógica de combate activo
        if self.state == "active":
            self.barrier_pulse += dt * 4.0

            # Actualizar cascada de lava del techo
            self.lava_shower.update(dt)

            # Bloquear la salida físicamente
            player = self.room.player
            if player.hitbox.left < 36:
                player.x = 36.0
                player.hitbox.x = 36
                player.vx = max(0.0, player.vx)

            # Evitar respawn automático durante la arena
            self.room.respawn_queue.clear()

            was_transitioning = (self.phase_transition_timer > 0.0)
            if self.phase_transition_timer > 0.0:
                self.phase_transition_timer -= dt

            # Comprobar estado del jefe
            if self.boss is None or self.boss.dead or self.boss.health <= 0:
                self.on_arena_cleared()
                return

            # Contar esbirros activos (excluyendo al jefe)
            active_minions = [e for e in self.room.enemies if e != self.boss and not e.dead]

            # Si hay esbirros vivos o estamos en transición, el escudo del jefe está activo
            if len(active_minions) > 0 or self.phase_transition_timer > 0.0:
                self.boss.shield_active = True
            else:
                # Si todos los esbirros fueron derrotados, se rompe el escudo
                if self.boss.shield_active:
                    self.boss.shield_active = False
                    self.banner_text = "¡ESCUDO ROTO! ¡ATACA AL JEFE!"
                    self.banner_color = (255, 240, 90)
                    self.banner_timer = 2.0
                    self.room.camera.shake(3.5, 0.25)
                    self.room.spawn_dust(self.boss.hitbox.centerx, self.boss.hitbox.bottom, count=12)

            hp_pct = max(0.0, self.boss.health / self.boss._max_health)

            # Transición a Fase 2 (al bajar a 70% de vida o menos)
            if self.boss_phase == 1 and hp_pct <= 0.70:
                self.boss.health = self.boss._max_health * 0.70  # Límite de vida hasta fase 2
                self.boss_phase = 2
                self.boss.boss_phase = 2
                self.boss.shield_active = True
                self.boss.attack_cooldown = 3.0  # Descanso del jefe
                self.phase_transition_timer = 2.4
                self.boss.change_state("idle")
                self.banner_text = "¡FASE 2: ORBES DEL VACÍO!"
                self.banner_color = (255, 140, 60)
                self.banner_timer = 2.6
                self.room.camera.shake(5.0, 0.4)

                # Limpiar esbirros antiguos y spawnear los de fase 2
                for en in list(self.room.enemies):
                    if en != self.boss and not en.dead:
                        en.dead = True
                        en.change_state("death")
                self.spawn_minions_for_phase(2)

            # Transición a Fase 3 (al bajar a 30% de vida o menos)
            elif self.boss_phase == 2 and hp_pct <= 0.30:
                self.boss.health = self.boss._max_health * 0.30  # Límite de vida hasta fase 3
                self.boss_phase = 3
                self.boss.boss_phase = 3
                self.boss.shield_active = True
                self.boss.attack_cooldown = 3.0  # Descanso del jefe
                self.phase_transition_timer = 2.4
                self.boss.change_state("idle")
                self.banner_text = "¡FASE 3: DESATAR EL VACÍO!"
                self.banner_color = (255, 80, 80)
                self.banner_timer = 2.6
                self.room.camera.shake(6.0, 0.5)

                # Limpiar esbirros antiguos y spawnear los de fase 3
                for en in list(self.room.enemies):
                    if en != self.boss and not en.dead:
                        en.dead = True
                        en.change_state("death")
                self.spawn_minions_for_phase(3)

            if was_transitioning and self.phase_transition_timer <= 0.0:
                # El jefe vuelve a atacar después del tiempo de invulnerabilidad/transición
                if self.boss.state_name != "chase":
                    self.boss.change_state("chase")

    def render(self, surface: pygame.Surface, cam_x: float, cam_y: float) -> None:
        # Renderizar cascadas de lava del techo
        if self.state == "active":
            self.lava_shower.render(surface, cam_x, cam_y)

        if not self.barrier_active:
            return

        # Dibujar barrera mágica de energía
        bx = int(self.barrier_rect.x - cam_x)
        by = int(self.barrier_rect.y - cam_y)
        bw = self.barrier_rect.width
        bh = self.barrier_rect.height

        alpha = int(170 + 60 * math.sin(self.barrier_pulse))
        barrier_surf = pygame.Surface((bw, bh), pygame.SRCALPHA)

        # Relleno de energía
        pygame.draw.rect(barrier_surf, (180, 50, 220, alpha // 2), (0, 0, bw, bh))
        # Barras de reja brillante
        for y_offset in range(4, bh, 8):
            line_alpha = min(255, alpha + 30)
            pygame.draw.line(barrier_surf, (240, 120, 255, line_alpha), (2, y_offset), (bw - 2, y_offset), 2)
        # Borde exterior
        pygame.draw.rect(barrier_surf, (255, 200, 255, alpha), (0, 0, bw, bh), 2)

        surface.blit(barrier_surf, (bx, by))

    def render_hud(self, surface: pygame.Surface) -> None:
        if self.banner_timer > 0.0 and self.banner_text:
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

        # Barra de vida del Sumo Sacerdote Cultista
        if (
            self.boss is not None
            and not self.boss.dead
            and self.state == "active"
        ):
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

            # Título del jefe con estado de escudo o vulnerabilidad
            if self.boss.shield_active:
                status_text = f"SUMO SACERDOTE (FASE {self.boss_phase}/3) - ESCUDO ACTIVO"
                status_color = (220, 130, 255)
            else:
                status_text = f"SUMO SACERDOTE (FASE {self.boss_phase}/3) - ¡VULNERABLE!"
                status_color = (255, 240, 100)

            render_text(
                surface,
                status_text,
                settings.FONTS["hud"],
                settings.VIRTUAL_WIDTH // 2,
                by - 9,
                status_color,
                center=True,
                shadowed=True,
            )

            # Marco de la barra
            bg_rect = pygame.Rect(bx - 2, by - 2, bar_w + 4, bar_h + 4)
            pygame.draw.rect(surface, (15, 10, 22), bg_rect)

            # Si el escudo está activo, dibujar un marco exterior brillante pulsante
            if self.boss.shield_active:
                shield_border_col = (190, 80, 255)
                pygame.draw.rect(surface, shield_border_col, bg_rect, 1)
            else:
                pygame.draw.rect(surface, (100, 30, 80), bg_rect, 1)

            # Relleno de vida
            hp_pct = max(0.0, min(1.0, self.boss.health / self.boss._max_health))
            fill_w = int(bar_w * hp_pct)
            if fill_w > 0:
                pygame.draw.rect(surface, fill_col, (bx, by, fill_w, bar_h))
                pygame.draw.rect(surface, top_col, (bx, by, fill_w, 2))

            # Ticks de división de fases en la barra (70% y 30%)
            tick_70 = bx + int(bar_w * 0.70)
            tick_30 = bx + int(bar_w * 0.30)
            pygame.draw.line(surface, (255, 230, 140, 180), (tick_70, by), (tick_70, by + bar_h - 1), 1)
            pygame.draw.line(surface, (255, 230, 140, 180), (tick_30, by), (tick_30, by + bar_h - 1), 1)
