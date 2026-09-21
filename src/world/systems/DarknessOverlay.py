"""
Chrono Blight - Darkness Overlay
Manages sensory deprivation with vision halos for the final boss battle.
"""
from typing import List, Tuple, Optional, TYPE_CHECKING
import pygame

import settings

if TYPE_CHECKING:
    from src.entities.Player import Player
    from src.entities.Boss import Boss
    from src.world.objects.LightMonolith import LightMonolith


class DarknessOverlay:
    def __init__(self) -> None:
        self.current_alpha: float = 0.0
        self.target_alpha: float = 0.0
        self._tween_timer = None
        self._surface = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
        self._halo_cache: dict[tuple[int, int], pygame.Surface] = {}

    def set_target_darkness(self, alpha_normalized: float, speed: float = 1.8) -> None:
        self.target_alpha = max(0.0, min(1.0, alpha_normalized))
        
        from gale.timer import Timer
        
        if self._tween_timer:
            self._tween_timer.remove()
            self._tween_timer = None
            
        duration = abs(self.target_alpha - self.current_alpha) / speed if speed > 0 else 0
        if duration > 0:
            self._tween_timer = Timer.tween(duration, [(self, {"current_alpha": self.target_alpha})])
        else:
            self.current_alpha = self.target_alpha

    def update(self, dt: float) -> None:
        pass

    def render(
        self,
        target_surface: pygame.Surface,
        camera_x: float,
        camera_y: float,
        player: Optional["Player"] = None,
        boss: Optional["Boss"] = None,
        monoliths: Optional[List["LightMonolith"]] = None,
    ) -> None:
        if self.current_alpha <= 0.01:
            return

        alpha_byte = int(self.current_alpha * 255)
        self._surface.fill((4, 3, 7, alpha_byte))

        is_phase_2 = (boss is not None and getattr(boss, "boss_phase", 1) == 2)

        if player is not None and not player.is_dead():
            px = int(player.hitbox.centerx - camera_x)
            py = int(player.hitbox.centery - camera_y)
            if is_phase_2:
                self._carve_halo(px, py, radius=36, core_radius=20)
            else:
                self._carve_halo(px, py, radius=52, core_radius=30)

        if monoliths:
            for m in monoliths:
                mx = int(m.hitbox.centerx - camera_x)
                my = int(m.hitbox.centery - camera_y)
                is_act = getattr(m, "is_activated", False)
                radius = 80 if is_act else 18
                core_radius = 44 if is_act else 7
                if -radius <= mx <= settings.VIRTUAL_WIDTH + radius and -radius <= (my + 10) <= settings.VIRTUAL_HEIGHT + radius:
                    self._carve_halo(mx, my + 10, radius=radius, core_radius=core_radius)

        if boss is not None and not boss.dead:
            bx = int(boss.hitbox.centerx - camera_x)
            by = int(boss.hitbox.centery - camera_y)
            if is_phase_2:
                if -20 <= bx <= settings.VIRTUAL_WIDTH + 20 and -20 <= (by - 14) <= settings.VIRTUAL_HEIGHT + 20:
                    self._carve_halo(bx, by - 14, radius=18, core_radius=7)
            else:
                if -50 <= bx <= settings.VIRTUAL_WIDTH + 50 and -50 <= by <= settings.VIRTUAL_HEIGHT + 50:
                    self._carve_halo(bx, by, radius=50, core_radius=28)

            for wb in getattr(boss, "wind_blades", []):
                wx = int(wb["x"] - camera_x)
                wy = int(wb["y"] - camera_y)
                if -22 <= wx <= settings.VIRTUAL_WIDTH + 22 and -22 <= wy <= settings.VIRTUAL_HEIGHT + 22:
                    self._carve_halo(wx, wy, radius=22, core_radius=11)

            for ds in getattr(boss, "dimensional_slashes", []):
                dx = int(ds["x"] - camera_x)
                dy = int(ds["y"] - camera_y)
                if -30 <= dx <= settings.VIRTUAL_WIDTH + 30 and -30 <= dy <= settings.VIRTUAL_HEIGHT + 30:
                    self._carve_halo(dx, dy, radius=30, core_radius=15)

        target_surface.blit(self._surface, (0, 0))

    def _carve_halo(self, cx: int, cy: int, radius: int, core_radius: int) -> None:
        if (
            cx + radius < 0
            or cx - radius > settings.VIRTUAL_WIDTH
            or cy + radius < 0
            or cy - radius > settings.VIRTUAL_HEIGHT
        ):
            return

        key = (radius, core_radius)
        if key not in self._halo_cache:
            mask = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            mask.fill((255, 255, 255, 255)) 
            pygame.draw.circle(mask, (255, 255, 255, 120), (radius, radius), radius)
            pygame.draw.circle(mask, (255, 255, 255, 0), (radius, radius), core_radius)
            self._halo_cache[key] = mask

        self._surface.blit(self._halo_cache[key], (cx - radius, cy - radius), special_flags=pygame.BLEND_RGBA_MULT)
