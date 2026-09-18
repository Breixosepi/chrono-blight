"""
Chrono Blight - Game Over State
"""
from typing import Any
import pygame
from gale.state import BaseState
from gale.input_handler import InputData
from gale.text import render_text
from src.states.game.SlotSelectState import SlotSelectState
from src.states.game.TitleState import TitleState

import settings

class GameOverState(BaseState):
    def __init__(self, state_machine: Any, play_state: Any = None, **kwargs: Any) -> None:
        super().__init__(state_machine)
        self.play_state = play_state

    def enter(self, play_state: Any = None, **params: Any) -> None:
        settings.stop_all_music()
        settings.play_music("game-over")
        if play_state is not None:
            self.play_state = play_state
        self.selected_index: int = 0
        self.options = [
            "Cargar partida",
            "Volver al menu principal",
        ]
        self.overlay = pygame.Surface(
            (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA
        )
        self.overlay.fill((20, 4, 4, 220))

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if not input_data.pressed:
            return

        if input_id in ("up", "move_up"):
            self.selected_index = (self.selected_index - 1) % len(self.options)
            settings.SOUNDS["change"].play()
        elif input_id in ("down", "move_down"):
            self.selected_index = (self.selected_index + 1) % len(self.options)
            settings.SOUNDS["change"].play()
        elif input_id in ("enter", "jump", "attack", "special"):
            settings.SOUNDS["enter"].play()
            self._select_option()

    def _select_option(self) -> None:
        if self.selected_index == 0:
            self.state_machine.push(
                SlotSelectState(self.state_machine),
                mode="load",
                from_game_over=True,
            )
        else:
            settings.stop_music("game-over")
            self._reset_to_title()

    def _reset_to_title(self) -> None:
        settings.stop_all_music()
        while len(self.state_machine.states) > 0:
            self.state_machine.pop()
            
        self.state_machine.push(TitleState(self.state_machine))

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(self.overlay, (0, 0))

        # Title
        render_text(
            surface,
            "HAS CAIDO",
            settings.FONTS["title"],
            settings.VIRTUAL_WIDTH // 2,
            settings.VIRTUAL_HEIGHT // 2 - 36,
            (235, 45, 45),
            center=True,
            shadowed=True,
        )

        # Options
        for i, option in enumerate(self.options):
            y_pos = settings.VIRTUAL_HEIGHT // 2 + 2 + (i * 22)
            is_selected = (i == self.selected_index)
            color = (255, 215, 60) if is_selected else (160, 160, 160)
            prefix = "> " if is_selected else "  "
            suffix = " <" if is_selected else "  "
            text_str = f"{prefix}{option}{suffix}"

            render_text(
                surface,
                text_str,
                settings.FONTS["hud"],
                settings.VIRTUAL_WIDTH // 2,
                y_pos,
                color,
                center=True,
                shadowed=True,
            )

        # Controls hint
        render_text(
            surface,
            "[ARRIBA/ABAJO] Elegir   [ENTER] Confirmar",
            settings.FONTS["hud"],
            settings.VIRTUAL_WIDTH // 2,
            settings.VIRTUAL_HEIGHT - 18,
            (140, 140, 140),
            center=True,
            shadowed=True,
        )