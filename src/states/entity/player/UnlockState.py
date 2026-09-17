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
            self.unlock_text = "¡FORMA DESBLOQUEADA: CABALLERO!"
            self.flash_color = (255, 210, 80)
        elif self.form_to_unlock == "morph":
            self.unlock_text = "¡FORMA DESBLOQUEADA: MORPH!"
            self.flash_color = (80, 255, 120)
        else:
            self.unlock_text = "¡ESTADÍSTICAS MEJORADAS!"
            self.flash_color = (255, 255, 255)
            
        self.start_y = float(self.entity.y)
        self.phase = 0
        self.timer = 0.0
        self.flash_timer = 0.0
        self.flash_max = 1.0

    def _get_room(self) -> Any:
        return getattr(self.entity, "room", None) or getattr(getattr(self.entity, "tilemap", None), "room", None)

    def update(self, dt: float) -> None:
        self.timer += dt
        self.entity.invulnerable_timer = max(self.entity.invulnerable_timer, 1.0)
        self.entity.vx = 0.0
        room = self._get_room()
        
        if self.phase == 0:
            progress = min(1.0, self.timer / 1.1)
            ease = ease_out_cubic(progress)
            self.entity.y = self.start_y - (45.0 * ease)
            self.entity.hitbox.y = int(self.entity.y)
            
            if self.timer >= 1.1:
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
            self.entity.y += self.entity.vy * dt
            self.entity.hitbox.y = int(self.entity.y)
            
            landed = False
            if hasattr(self.entity, "tilemap") and getattr(self.entity, "active_collision_layers", None):
                from src.world.tile_collision import check_on_ground
                if check_on_ground(self.entity.tilemap, self.entity.active_collision_layers, self.entity.x, self.entity.y, float(self.entity.width), float(self.entity.height)):
                    landed = True
            
            if not landed and self.entity.y >= self.start_y:
                self.entity.y = self.start_y
                self.entity.hitbox.y = int(self.entity.y)
                landed = True
            elif not landed and self.entity.hitbox.bottom >= self.entity.floor_y:
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
