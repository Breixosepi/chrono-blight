from typing import Any
import pygame

from gale.state import BaseState


class PhaseShiftState(BaseState):

    def enter(self, **params: Any) -> None:
        self.timer = 0.5  

    def update(self, dt: float) -> None:
        self.timer -= dt
        if self.timer <= 0:
            self.state_machine.pop()

    def render(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
        overlay.fill((0, 150, 255, 120))
        surface.blit(overlay, (0, 0))

        font = pygame.font.Font(None, 48)
        text = font.render(">>> PHASE SHIFTING... <<<", True, (255, 255, 255))
        surface.blit(text, (surface.get_width() // 2 - 180, surface.get_height() // 2 + 40))

