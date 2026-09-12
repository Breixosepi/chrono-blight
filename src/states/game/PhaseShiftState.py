"""
Chrono Blight - Phase Shift Transition State
"""

from typing import Any
import pygame

from gale.state import BaseState
from gale.text import render_text

import settings


class PhaseShiftState(BaseState):

    def enter(self, phase_color: str = "blue", **params: Any) -> None:
        self.timer: float = 0.35
        self.overlay = pygame.Surface(
            (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA
        )
        if phase_color == "red":
            self.overlay.fill((220, 60, 60, 95))
            self.label_color = (255, 190, 190)
        else:
            self.overlay.fill((50, 160, 255, 95))
            self.label_color = (190, 230, 255)

    def update(self, dt: float) -> None:
        self.timer -= dt
        if self.timer <= 0.0:
            self.state_machine.pop()

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
