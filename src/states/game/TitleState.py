"""
Chrono Blight - Title Screen State
"""
from typing import Any, Optional
import pygame
from gale.state import BaseState
from gale.input_handler import InputData
from gale.text import render_text
from gale.timer import Timer, Every

import settings


class TitleState(BaseState):
    def enter(self, **params: Any) -> None:
        self.show_prompt: bool = True
        self.blink_timer: Optional[Every] = Timer.every(0.4, self._toggle_prompt)

    def _toggle_prompt(self) -> None:
        self.show_prompt = not self.show_prompt

    def exit(self) -> None:
        if hasattr(self, "blink_timer") and self.blink_timer is not None:
            self.blink_timer.remove()
            self.blink_timer = None

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "enter" and input_data.pressed:
            from src.states.game.PlayState import PlayState
            self.state_machine.pop()
            self.state_machine.push(PlayState(self.state_machine))

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((16, 12, 24))

        render_text(
            surface,
            settings.TITLE,
            settings.FONTS["title"],
            settings.VIRTUAL_WIDTH // 2,
            38,
            (235, 190, 70),
            center=True,
            shadowed=True,
        )

        render_text(
            surface,
            "TEMPORAL HACK / SLASH",
            settings.FONTS["hud"],
            settings.VIRTUAL_WIDTH // 2,
            58,
            (140, 160, 210),
            center=True,
            shadowed=True,
        )

        if self.show_prompt:
            render_text(
                surface,
                "Presiona ENTER para iniciar",
                settings.FONTS["ui"],
                settings.VIRTUAL_WIDTH // 2,
                92,
                (255, 255, 255),
                center=True,
                shadowed=True,
            )

        render_text(
            surface,
            "Mover: Flechas | Saltar: Espacio | Atacar: Z",
            settings.FONTS["hud"],
            settings.VIRTUAL_WIDTH // 2,
            140,
            (170, 175, 190),
            center=True,
            shadowed=True,
        )

        render_text(
            surface,
            "Habilidad: X | Fase: Shift | Formas: Q / E | Pausa: P",
            settings.FONTS["hud"],
            settings.VIRTUAL_WIDTH // 2,
            156,
            (170, 175, 190),
            center=True,
            shadowed=True,
        )