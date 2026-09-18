from typing import Any
import pygame
from gale.state import BaseState
from gale.input_handler import InputData
from gale.text import render_text
from src.states.game.TitleState import TitleState
import settings


class VictoryState(BaseState):
    def __init__(self, state_machine: Any, play_state: Any = None, **kwargs: Any) -> None:
        super().__init__(state_machine)
        self.play_state = play_state
        self.timer: float = 0.0
        self.time_str: str = "00m 00s"
        self.exploration_pct: int = 100

    def enter(self, play_state: Any = None, **params: Any) -> None:
        settings.stop_all_music()
        if "arena-cleared" in settings.SOUNDS:
            settings.SOUNDS["arena-cleared"].play()

        if play_state is not None:
            self.play_state = play_state

        self.timer = 0.0
        self.overlay = pygame.Surface(
            (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA
        )
        self.overlay.fill((8, 6, 16, 235))

        playtime_sec = int(getattr(self.play_state, "playtime", 0.0)) if self.play_state else 0
        hours = playtime_sec // 3600
        mins = (playtime_sec % 3600) // 60
        secs = playtime_sec % 60
        if hours > 0:
            self.time_str = f"{hours}h {mins:02d}m {secs:02d}s"
        else:
            self.time_str = f"{mins:02d}m {secs:02d}s"

        visited = getattr(self.play_state, "visited_rooms", set()) if self.play_state else set()
        self.exploration_pct = min(100, int((len(visited) / 8.0) * 100))

    def update(self, dt: float) -> None:
        self.timer += dt

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if not input_data.pressed:
            return
        if self.timer < 1.0:
            return
        if input_id in ("enter", "jump", "attack", "special", "back", "pause"):
            if "enter" in settings.SOUNDS:
                settings.SOUNDS["enter"].play()
            self._reset_to_title()

    def _reset_to_title(self) -> None:
        settings.stop_all_music()
        while len(self.state_machine.states) > 0:
            self.state_machine.pop()
        self.state_machine.push(TitleState(self.state_machine))

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(self.overlay, (0, 0))

        card_w, card_h = 240, 140
        card_x = (settings.VIRTUAL_WIDTH - card_w) // 2
        card_y = (settings.VIRTUAL_HEIGHT - card_h) // 2

        card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        card_surf.fill((22, 16, 34, 230))
        pygame.draw.rect(card_surf, (255, 215, 80), (0, 0, card_w, card_h), width=1, border_radius=6)
        surface.blit(card_surf, (card_x, card_y))

        render_text(
            surface,
            "¡VICTORIA!",
            settings.FONTS["title"],
            settings.VIRTUAL_WIDTH // 2,
            card_y + 12,
            (255, 215, 80),
            center=True,
            shadowed=True,
        )

        render_text(
            surface,
            "Has derrotado a The Harvester",
            settings.FONTS["hud"],
            settings.VIRTUAL_WIDTH // 2,
            card_y + 36,
            (210, 200, 230),
            center=True,
            shadowed=True,
        )

        render_text(
            surface,
            "y restaurado la linea temporal.",
            settings.FONTS["hud"],
            settings.VIRTUAL_WIDTH // 2,
            card_y + 48,
            (170, 160, 190),
            center=True,
            shadowed=True,
        )

        pygame.draw.line(
            surface,
            (75, 65, 95),
            (card_x + 20, card_y + 64),
            (card_x + card_w - 20, card_y + 64),
            1,
        )

        render_text(
            surface,
            f"Tiempo de juego: {self.time_str}",
            settings.FONTS["hud"],
            card_x + 25,
            card_y + 72,
            (240, 230, 200),
            shadowed=True,
        )

        render_text(
            surface,
            f"Exploracion total: {self.exploration_pct}%",
            settings.FONTS["hud"],
            card_x + 25,
            card_y + 86,
            (130, 230, 170),
            shadowed=True,
        )

        blink = int(self.timer * 3) % 2 == 0
        prompt_col = (255, 230, 100) if blink else (180, 160, 90)
        render_text(
            surface,
            "[ENTER] Volver al Menu Principal",
            settings.FONTS["hud"],
            settings.VIRTUAL_WIDTH // 2,
            card_y + 116,
            prompt_col,
            center=True,
            shadowed=True,
        )

