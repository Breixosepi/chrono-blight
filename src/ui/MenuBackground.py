"""
Chrono Blight - Shared Menu Background Manager
"""
import pygame
import settings


class MenuBackground:
    CYCLE_TIME: float = 20.0  
    CROSSFADE_TIME: float = 1.5 

    def __init__(self) -> None:
        self.timer: float = 0.0
        self._fade_surf: pygame.Surface = pygame.Surface(
            (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT)
        )
        
        self._dark_overlay: pygame.Surface = pygame.Surface(
            (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA
        )
        self._dark_overlay.fill((14, 10, 20, 130))

    def update(self, dt: float) -> None:
        period = self.CYCLE_TIME * 2.0
        self.timer = (self.timer + dt) % period

    def render(self, surface: pygame.Surface) -> None:
        t = self.timer
        period = self.CYCLE_TIME * 2.0

        past_tex = settings.TEXTURES.get("gothic_castle_past")
        future_tex = settings.TEXTURES.get("gothic_castle_future")

        if not past_tex or not future_tex:
            surface.fill((16, 12, 24))
            return

        if t < (self.CYCLE_TIME - self.CROSSFADE_TIME):
            surface.blit(past_tex, (0, 0))

        elif t < self.CYCLE_TIME:
            surface.blit(past_tex, (0, 0))
            progress = (t - (self.CYCLE_TIME - self.CROSSFADE_TIME)) / self.CROSSFADE_TIME
            alpha = int(max(0.0, min(1.0, progress)) * 255)
            self._fade_surf.blit(future_tex, (0, 0))
            self._fade_surf.set_alpha(alpha)
            surface.blit(self._fade_surf, (0, 0))

        elif t < (period - self.CROSSFADE_TIME):
            surface.blit(future_tex, (0, 0))

        else:
            surface.blit(future_tex, (0, 0))
            progress = (t - (period - self.CROSSFADE_TIME)) / self.CROSSFADE_TIME
            alpha = int(max(0.0, min(1.0, progress)) * 255)
            self._fade_surf.blit(past_tex, (0, 0))
            self._fade_surf.set_alpha(alpha)
            surface.blit(self._fade_surf, (0, 0))

        surface.blit(self._dark_overlay, (0, 0))

menu_background = MenuBackground()