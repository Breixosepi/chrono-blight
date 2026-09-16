"""
Chrono Blight - Phase Shift Transition State
"""
from typing import Any, Optional
import pygame
from gale.state import BaseState
from gale.timer import Timer, After
from gale.text import render_text

import settings


class PhaseShiftState(BaseState):
    def enter(self, phase_color: str = "blue", **params: Any) -> None:
        self.overlay = pygame.Surface(
            (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA
        )
        if phase_color == "red":
            self.overlay.fill((220, 60, 60, 95))
            self.label_color = (255, 190, 190)
        else:
            self.overlay.fill((50, 160, 255, 95))
            self.label_color = (190, 230, 255)

        transition_duration = 0.35
        self.transition_timer: Optional[After] = Timer.after(
            transition_duration, self._finish_phase_shift
        )

    def _finish_phase_shift(self) -> None:
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