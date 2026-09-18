"""
Chrono Blight - Title Screen State with Main Menu
"""
from typing import Any
import pygame
from gale.state import BaseState
from gale.input_handler import InputData
from gale.text import render_text

import settings
from src.states.game.SlotSelectState import SlotSelectState
from src.ui.MenuBackground import menu_background


class TitleState(BaseState):
    MENU_START_Y: int = 86
    MENU_GAP: int = 18

    def enter(self, **params: Any) -> None:
        for name in list(settings.MUSIC_CHANNELS.keys()):
            if name != "intro":
                settings.stop_music(name)

        if "lava" in settings.SOUNDS:
            settings.SOUNDS["lava"].stop()
        if "saw-hazard" in settings.SOUNDS:
            settings.SOUNDS["saw-hazard"].stop()
        if "lava-shower" in settings.SOUNDS:
            settings.SOUNDS["lava-shower"].stop()

        # Only start intro if it isn't already playing (avoids restart on back-press)
        ch = settings.MUSIC_CHANNELS.get("intro")
        if ch is None or not ch.get_busy():
            settings.play_music("intro")
        self.options = ["NUEVA PARTIDA", "CARGAR PARTIDA", "SALIR"]
        self.selected_index = 0

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if not input_data.pressed:
            return

        if input_id in ("up"):
            self.selected_index = (self.selected_index - 1) % len(self.options)
            settings.SOUNDS["change"].play()
        elif input_id in ("down"):
            self.selected_index = (self.selected_index + 1) % len(self.options)
            settings.SOUNDS["change"].play()
        elif input_id in ("enter"):
            settings.SOUNDS["enter"].play()
            self._confirm_selection()

    def _open_slot_select(self, mode: str) -> None:
        self.state_machine.pop()
        slot_state = SlotSelectState(self.state_machine)
        self.state_machine.push(slot_state, mode=mode)

    def _confirm_selection(self) -> None:
        choice = self.options[self.selected_index]
        if choice == "NUEVA PARTIDA":
            self._open_slot_select(mode="new")
        elif choice == "CARGAR PARTIDA":
            self._open_slot_select(mode="load")
        elif choice == "SALIR":
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def update(self, dt: float) -> None:
        menu_background.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        menu_background.render(surface)

        render_text(
            surface,
            settings.TITLE,
            settings.FONTS["main-title"],
            settings.VIRTUAL_WIDTH // 2,
            32,
            (235, 190, 70),
            center=True,
            shadowed=True,
        )

        render_text(
            surface,
            "TEMPORAL HACK / SLASH",
            settings.FONTS["hud"],
            settings.VIRTUAL_WIDTH // 2,
            52,
            (140, 160, 210),
            center=True,
            shadowed=True,
        )

        for i, opt in enumerate(self.options):
            is_selected = (i == self.selected_index)
            color = (255, 230, 90) if is_selected else (160, 150, 175)
            prefix = "> " if is_selected else "  "

            render_text(
                surface,
                f"{prefix}{opt}",
                settings.FONTS["ui"],
                settings.VIRTUAL_WIDTH // 2,
                self.MENU_START_Y + i * self.MENU_GAP,
                color,
                center=True,
                shadowed=True,
            )

        render_text(
            surface,
            "[ARRIBA/ABAJO] Navegar  [ENTER] Seleccionar",
            settings.FONTS["hud"],
            settings.VIRTUAL_WIDTH // 2,
            settings.VIRTUAL_HEIGHT - 12,
            (110, 100, 125),
            center=True,
            shadowed=True,
        )