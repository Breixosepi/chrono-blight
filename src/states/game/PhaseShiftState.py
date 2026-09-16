"""
Chrono Blight - Phase Shift Transition State
"""
from typing import Any, Optional, Tuple, Dict
import pygame
from gale.state import BaseState
from gale.timer import Timer, After
from gale.text import render_text

import settings


class PhaseShiftState(BaseState):
    _OVERLAYS: Optional[Dict[str, Tuple[pygame.Surface, Tuple[int, int, int]]]] = None

    def enter(self, phase_color: str = "green", **params: Any) -> None:
        self._init_shared_overlays()
        
        config = self._OVERLAYS.get(phase_color, self._OVERLAYS["green"])
        self.overlay, self.label_color = config

        self.transition_timer: Optional[After] = Timer.after(0.35, self._finish_phase_shift)

    @classmethod
    def _init_shared_overlays(cls) -> None:
        if cls._OVERLAYS is None:
            red_surf = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
            red_surf.fill((220, 60, 60, 95))

            green_surf = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
            green_surf.fill((45, 190, 105, 95))

            cls._OVERLAYS = {
                "red": (red_surf, (255, 190, 190)),
                "green": (green_surf, (180, 255, 210)),
            }

    def _finish_phase_shift(self) -> None:
        self.transition_timer = None
        self.state_machine.pop()

    def exit(self) -> None:
        if hasattr(self, "transition_timer") and self.transition_timer is not None:
            self.transition_timer.remove()
            self.transition_timer = None

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(self.overlay, (0, 0))
        render_text(
            surface,
            "CAMBIO DE FASE",
            settings.FONTS["ui"],
            settings.VIRTUAL_WIDTH // 2,
            settings.VIRTUAL_HEIGHT // 2,
            self.label_color,
            center=True,
            shadowed=True,
        )