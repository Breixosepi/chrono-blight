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
    _RING_SURF: Optional[pygame.Surface] = None

    def enter(self, phase_color: str = "green", play_state: Any = None, **params: Any) -> None:
        self.play_state = play_state
        if phase_color == "green":
            settings.SOUNDS["phase_shift_past"].play()
        else:
            settings.SOUNDS["phase_shift_future"].play()
        self._init_shared_overlays()
        
        config = self._OVERLAYS.get(phase_color, self._OVERLAYS["green"])
        self.overlay, self.label_color = config

        self.elapsed = 0.0
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
        if cls._RING_SURF is None:
            cls._RING_SURF = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)

    def _finish_phase_shift(self) -> None:
        self.transition_timer = None
        self.state_machine.pop()

    def exit(self) -> None:
        if hasattr(self, "transition_timer") and self.transition_timer is not None:
            self.transition_timer.remove()
            self.transition_timer = None
        if self.play_state is not None and hasattr(self.play_state, "player"):
            player = self.play_state.player
            keys = pygame.key.get_pressed()
            from src import controls_manager
            left_k = controls_manager.CURRENT_KEYBINDS.get("move_left", pygame.K_a)
            right_k = controls_manager.CURRENT_KEYBINDS.get("move_right", pygame.K_d)
            is_left = bool(keys[left_k] or keys[pygame.K_LEFT])
            is_right = bool(keys[right_k] or keys[pygame.K_RIGHT])
            if is_left and not is_right:
                player.move_direction = -1
            elif is_right and not is_left:
                player.move_direction = 1
            elif not is_left and not is_right:
                player.move_direction = 0

    def on_input(self, input_id: str, input_data: Any) -> None:
        if self.play_state is not None:
            self.play_state.on_input(input_id, input_data)

    def update(self, dt: float) -> None:
        if self.play_state is not None:
            self.play_state.update(dt)
        self.elapsed += dt

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(self.overlay, (0, 0))
        
        max_time = 0.35
        progress = min(1.0, self.elapsed / max_time)
        radius = int(progress * settings.VIRTUAL_WIDTH * 0.7)
        alpha = int(255 * (1.0 - progress))
        
        if radius > 0 and alpha > 0 and self._RING_SURF is not None:
            self._RING_SURF.fill((0, 0, 0, 0))
            pygame.draw.circle(self._RING_SURF, (*self.label_color, alpha), (settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT // 2), radius, width=4)
            surface.blit(self._RING_SURF, (0, 0))