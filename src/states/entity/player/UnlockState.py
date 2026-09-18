from typing import Any, Optional
import pygame
import math
from gale.timer import Timer
from gale.ease_functions import ease_out_cubic
from src.states.entity.EntityBaseState import EntityBaseState
import settings

class UnlockState(EntityBaseState):
    has_gravity = False

    def __init__(self, entity: Any, state_machine: Any) -> None:
        super().__init__(entity, state_machine)
        self.timer: float = 0.0
        self.phase: int = 0
        self.target_y: float = 0.0
        self.start_y: float = 0.0
        self.form_to_unlock: str = ""
        self.unlock_text: str = ""
        
        self.flash_timer: float = 0.0
        self.flash_max: float = 0.4
        self.flash_color: tuple = (255, 255, 255)

    def enter(self, **params: Any) -> None:
        self.entity.vx = 0.0
        self.entity.vy = 0.0
        self.entity.change_animation("jump")
        self.form_to_unlock = params.get("form", "sword")
        
        if self.form_to_unlock == "sword":
            self.unlock_text = "!FORMA DESBLOQUEADA: CABALLERO!"
            self.flash_color = (255, 210, 80)
        elif self.form_to_unlock == "morph":
            self.unlock_text = "!FORMA DESBLOQUEADA: MORPH!"
            self.flash_color = (80, 255, 120)
        elif self.form_to_unlock == "victory":
            self.unlock_text = "!VICTORIA!"
            self.flash_color = (255, 215, 80)
        else:
            self.unlock_text = "!ESTADISTICAS MEJORADAS! (+30 HP / +20 MP)"
            self.flash_color = (255, 255, 255)
            
        self.start_y = float(self.entity.y)
        self.target_y = self._calculate_safe_levitation_target()
        self.phase = 0
        self.timer = 0.0
        self.flash_timer = 0.0
        self.flash_max = 1.0
        settings.SOUNDS["unlock-state"].play()

    def _get_room(self) -> Any:
        return getattr(self.entity, "room", None) or getattr(getattr(self.entity, "tilemap", None), "room", None)

    def _calculate_safe_levitation_target(self) -> float:
        """
        Calculates a safe levitation Y coordinate so the player never:
          - Escapes above the ceiling of the room into solid tiles or out-of-bounds.
          - Flies off the visible top of the screen/camera viewport.
        """
        room = self._get_room()
        tilemap = getattr(self.entity, "tilemap", None)
        collision_layers = getattr(self.entity, "active_collision_layers", None)

        # 1. Screen / Camera top boundary
        cam_top = 0.0
        if room and hasattr(room, "camera"):
            cam_top = float(getattr(room.camera, "offset", (0.0, 0.0))[1])
        min_screen_y = cam_top + 28.0

        # 2. Tilemap Ceiling boundary
        ceiling_bottom = 0.0
        if tilemap and collision_layers:
            from gale.tilemap.collision import CollisionType
            from src.world.systems.tile_collision import collision_type_in_layers

            tile_h = tilemap.tile_height
            tile_w = tilemap.tile_width
            start_row = max(0, min(tilemap.rows - 1, int(self.entity.y // tile_h)))
            col_left = max(0, int(self.entity.hitbox.left // tile_w))
            col_right = min(tilemap.cols - 1, int((self.entity.hitbox.right - 1) // tile_w))

            for row in range(start_row, -1, -1):
                is_solid_row = False
                for col in range(col_left, col_right + 1):
                    if collision_type_in_layers(tilemap, collision_layers, row, col) == CollisionType.SOLID:
                        ceiling_bottom = max(ceiling_bottom, float((row + 1) * tile_h))
                        is_solid_row = True
                if is_solid_row:
                    break

        min_ceiling_y = ceiling_bottom + 6.0  # 6px clearance beneath solid ceiling
        min_safe_y = max(min_ceiling_y, min_screen_y, 24.0)

        # Standard levitation rise is 40px
        desired_y = self.start_y - 40.0
        if desired_y < min_safe_y:
            return max(min_safe_y, min(self.start_y, min_safe_y))
        return desired_y

    def update(self, dt: float) -> None:
        self.timer += dt
        self.entity.invulnerable_timer = max(self.entity.invulnerable_timer, 1.0)
        self.entity.vx = 0.0
        room = self._get_room()

        if self.phase == 0:
            progress = min(1.0, self.timer / 1.1)
            ease = ease_out_cubic(progress)
            self.entity.y = self.start_y + (self.target_y - self.start_y) * ease
            self.entity.hitbox.y = int(round(self.entity.y))

            if self.timer >= 1.1:
                self.entity.y = self.target_y
                self.entity.hitbox.y = int(round(self.entity.y))
                self.phase = 1
                self.timer = 0.0
                self.flash_timer = self.flash_max
                if room and hasattr(room, "spawn_dust"):
                    room.spawn_dust(self.entity.hitbox.centerx, self.entity.hitbox.centery, 24, self.flash_color)

        elif self.phase == 1:
            if self.flash_timer > 0.0:
                self.flash_timer = max(0.0, self.flash_timer - dt)

            if self.timer >= 1.1:
                self.phase = 2
                self.timer = 0.0
                self.entity.change_animation("fall")

        elif self.phase == 2:
            self.entity.vy = 180.0
            landed = False

            tilemap = getattr(self.entity, "tilemap", None)
            collision_layers = getattr(self.entity, "active_collision_layers", None)
            if tilemap and collision_layers:
                from src.world.systems.tile_collision import move_and_collide_layers
                nx, ny, cx, cy = move_and_collide_layers(
                    tilemap,
                    collision_layers,
                    self.entity.x,
                    self.entity.y,
                    float(self.entity.width),
                    float(self.entity.height),
                    0.0,
                    self.entity.vy * dt,
                )
                self.entity.x = nx
                self.entity.y = ny
                self.entity.hitbox.x = int(round(nx))
                self.entity.hitbox.y = int(round(ny))
                if cy:
                    landed = True
            else:
                self.entity.y += self.entity.vy * dt
                self.entity.hitbox.y = int(round(self.entity.y))

            if not landed and self.entity.hitbox.bottom >= int(self.entity.floor_y):
                self.entity.hitbox.bottom = int(self.entity.floor_y)
                self.entity.y = float(self.entity.hitbox.y)
                landed = True

            if landed:
                self.entity.vy = 0.0
                self.entity.on_ground = True
                self.phase = 3
                self.timer = 0.0
                self.entity.change_animation("idle")
                self.entity.on_land()
                
                if self.form_to_unlock in ("sword", "morph"):
                    if hasattr(self.entity, "unlocked_skins"):
                        self.entity.unlocked_skins.add(self.form_to_unlock)
                    if self.form_to_unlock not in self.entity.available_skins:
                        self.entity.available_skins.append(self.form_to_unlock)
                    self.entity.change_skin(self.form_to_unlock)
                elif self.form_to_unlock == "stats":
                    if hasattr(self.entity, "apply_permanent_stat_boost"):
                        self.entity.apply_permanent_stat_boost(30.0, 20.0)
                
                if room and hasattr(room, "_spawn_popup"):
                    room._spawn_popup(
                        self.unlock_text,
                        self.entity.hitbox.centerx,
                        self.entity.hitbox.top - 20,
                        3.5,
                        self.flash_color
                    )
                if room and hasattr(room, "spawn_dust"):
                    room.spawn_dust(self.entity.hitbox.centerx, self.entity.hitbox.bottom, 16, self.flash_color)
                
        elif self.phase == 3:
            if self.timer >= 2.2:
                self.change_state("idle")
                
                if room:
                    if getattr(room, "arena", None):
                        room.arena.on_unlock_finished()
                    else:
                        play_state = getattr(room, "play_state", None)
                        if play_state and getattr(play_state, "waiting_for_unlock", False):
                            play_state.waiting_for_unlock = False
                            play_state.can_exit_room = True

    def render(self, surface: pygame.Surface, camera_x: float = 0.0, camera_y: float = 0.0) -> None:
        if self.flash_timer > 0.0:
            ratio = self.flash_timer / self.flash_max
            inv_ratio = 1.0 - ratio
            cx = int(self.entity.hitbox.centerx - camera_x)
            cy = int(self.entity.hitbox.centery - camera_y)
            
            glow_surf = pygame.Surface((160, 160), pygame.SRCALPHA)
            alpha_glow = int(160 * ratio)
            radius_glow = int(20 + 45 * inv_ratio)
            pygame.draw.circle(glow_surf, (*self.flash_color, alpha_glow), (80, 80), radius_glow)
            surface.blit(glow_surf, (cx - 80, cy - 80))
            
            ring_surf = pygame.Surface((180, 180), pygame.SRCALPHA)
            alpha_ring = int(230 * ratio)
            ring_radius = int(12 + 65 * inv_ratio)
            pygame.draw.circle(ring_surf, (*self.flash_color, alpha_ring), (90, 90), ring_radius, 4)
            surface.blit(ring_surf, (cx - 90, cy - 90))

    def render_banner(self, surface: pygame.Surface) -> None:
        if self.phase == 3:
            from gale.text import render_text
            bw = 280
            bh = 26
            bx = (settings.VIRTUAL_WIDTH - bw) // 2
            by = 22
            banner_bg = pygame.Surface((bw, bh), pygame.SRCALPHA)
            banner_bg.fill((12, 16, 24, 225))
            pygame.draw.rect(banner_bg, (*self.flash_color, 240), (0, 0, bw, bh), 1)
            surface.blit(banner_bg, (bx, by))
            
            render_text(
                surface,
                self.unlock_text,
                settings.FONTS["hud"],
                settings.VIRTUAL_WIDTH // 2,
                by + (bh // 2),
                self.flash_color,
                center=True,
                shadowed=True,
            )
