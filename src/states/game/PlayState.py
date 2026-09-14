"""
Chrono Blight - Play State
"""

from typing import Any
import pygame

from gale.state import BaseState
from gale.input_handler import InputData

from src.world.Room import Room
from src.ui.HUD import HUD
from src.states.game.PauseState import PauseState
from src.states.game.PhaseShiftState import PhaseShiftState
from src.states.game.GameOverState import GameOverState
import settings


class PlayState(BaseState):

    def enter(self, **params: Any) -> None:
        from src.world.room_connections import DEFAULT_START_ROOM, DEFAULT_START_SPAWN

        start_room = params.get("map_name", DEFAULT_START_ROOM)
        spawn_x, spawn_y = params.get("spawn_point", DEFAULT_START_SPAWN)

        self.room = Room(map_name=start_room, spawn_x=spawn_x, spawn_y=spawn_y)
        self.player = self.room.player
        self.hud = HUD()

        self.in_transition: bool = False
        self.exit_cooldown: float = 0.0
        self.fade_alpha: float = 0.0
        self.fade_surface = pygame.Surface(
            (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA
        )

    def exit(self) -> None:
        pass

    def change_room(self, target_room: str, target_spawn_x: float, target_spawn_y: float) -> None:
        if self.in_transition:
            return

        self.in_transition = True
        self.player.move_direction = 0
        self.player.vx = 0.0
        self.player.vy = 0.0
        self.player.change_state("idle")

        from gale.timer import Timer
        Timer.tween(
            0.2,
            [(self, {"fade_alpha": 255.0})],
            ease_function_name="linear",
            on_finish=lambda: self._on_room_faded_out(target_room, target_spawn_x, target_spawn_y),
        )

    def _on_room_faded_out(self, target_room: str, target_spawn_x: float, target_spawn_y: float) -> None:
        self.room = Room(
            map_name=target_room,
            spawn_x=target_spawn_x,
            spawn_y=target_spawn_y,
            player=self.player,
        )
        self.player.move_direction = 0
        self.player.vx = 0.0
        self.player.vy = 0.0
        self.player.change_state("idle")

        from gale.timer import Timer
        Timer.tween(
            0.2,
            [(self, {"fade_alpha": 0.0})],
            ease_function_name="linear",
            on_finish=self._on_transition_finished,
        )

    def _on_transition_finished(self) -> None:
        self.in_transition = False
        self.exit_cooldown = 0.4

    def update(self, dt: float) -> None:
        if self.player.is_dead() and self.player.is_animation_finished():
            self.state_machine.push(GameOverState(self.state_machine))
            return

        if self.in_transition:
            return

        self.room.update(dt)

        if self.exit_cooldown > 0.0:
            self.exit_cooldown = max(0.0, self.exit_cooldown - dt)
        else:
            exit_info = self.room.check_room_exits()
            if exit_info is not None:
                target_room, target_x, target_y = exit_info
                self.change_room(target_room, target_x, target_y)

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if self.in_transition:
            return

        if input_id == "pause" and input_data.pressed:
            self.state_machine.push(PauseState(self.state_machine))

        elif input_id == "phase_shift" and input_data.pressed:
            if self.player.toggle_phase():
                self.state_machine.push(
                    PhaseShiftState(self.state_machine), phase_color=self.player.phase_color
                )

        elif input_id == "prev_form" and input_data.pressed:
            self.player.cycle_skin(-1)

        elif input_id in ("next_form", "toggle_morph") and input_data.pressed:
            self.player.cycle_skin(1)

        else:
            self.player.on_input(input_id, input_data)

    def render(self, surface: pygame.Surface) -> None:
        self.room.render(surface)

        cam_x, cam_y = self.room.camera_offset
        self.hud.render(surface, self.player, cam_x, cam_y)

        if self.fade_alpha > 0.0:
            self.fade_surface.fill((0, 0, 0, int(max(0.0, min(255.0, self.fade_alpha)))))
            surface.blit(self.fade_surface, (0, 0))
