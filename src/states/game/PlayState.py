"""
Chrono Blight - Play State
"""
from typing import Any
import pygame
from gale.state import BaseState
from gale.timer import Timer
from gale.input_handler import InputData

import settings
from src.world.Room import Room
from src.ui.HUD import HUD
from src.world.room_connections import DEFAULT_START_ROOM, DEFAULT_START_SPAWN
from src.states.game.PauseState import PauseState
from src.states.game.PhaseShiftState import PhaseShiftState
from src.states.game.GameOverState import GameOverState


class PlayState(BaseState):
    def enter(self, **params: Any) -> None:
        start_room_name = params.get("map_name", DEFAULT_START_ROOM)
        spawn_coordinates = params.get("spawn_point", DEFAULT_START_SPAWN)
        spawn_x, spawn_y = spawn_coordinates
        self.room = Room(map_name=start_room_name, spawn_x=spawn_x, spawn_y=spawn_y)
        self.room.play_state = self
        self.player = self.room.player
        
        self.current_slot: str = params.get("slot", "slot_1")
        self.cleared_events: set[str] = set()

        if "save_data" in params:
            save_data = params["save_data"]
            self.player.health = save_data.get("player_health", self.player.MAX_HEALTH)
            self.player.skin = save_data.get("player_skin", "sword")
            self.cleared_events = set(save_data.get("cleared_events", []))
            
        self.room._check_cleared_events()
        self.hud = HUD()

        self.in_transition: bool = False
        self.can_exit_room: bool = True
        self.fade_alpha: float = 0.0
        self.fade_surface = pygame.Surface(
            (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA
        )

    def change_room(self, target_room_name: str, target_spawn_x: float, target_spawn_y: float) -> None:
        if self.in_transition:
            return

        if self.room.map_name in ("subida", "subida_past", "subida_future"):
            self.cleared_events.add("subida_cleared")

        self.in_transition = True
        self._halt_player()

        fade_duration = 0.2
        Timer.tween(
            fade_duration,
            [(self, {"fade_alpha": 255.0})],
            ease_function_name="linear",
            on_finish=lambda: self._on_room_faded_out(
                target_room_name, target_spawn_x, target_spawn_y
            ),
        )

    def _halt_player(self) -> None:
        self.player.move_direction = 0
        self.player.vx = 0.0
        self.player.vy = 0.0
        self.player.change_state("idle")

    def _on_room_faded_out(self, target_room_name: str, target_spawn_x: float, target_spawn_y: float) -> None:
        self.room = Room(
            map_name=target_room_name,
            spawn_x=target_spawn_x,
            spawn_y=target_spawn_y,
            player=self.player,
        )
        self.room.play_state = self
        self.room._check_cleared_events()
        self._halt_player()

        fade_duration = 0.2
        Timer.tween(
            fade_duration,
            [(self, {"fade_alpha": 0.0})],
            ease_function_name="linear",
            on_finish=self._on_transition_finished,
        )

    def _on_transition_finished(self) -> None:
        self.in_transition = False
        self.can_exit_room = False
        room_exit_cooldown_seconds = 0.4
        Timer.after(room_exit_cooldown_seconds, self._enable_room_exit)

    def _enable_room_exit(self) -> None:
        self.can_exit_room = True

    def update(self, dt: float) -> None:
        if self.player.is_dead() and self.player.is_animation_finished():
            self.state_machine.push(GameOverState(self.state_machine))
            return

        if self.in_transition:
            return

        self.room.update(dt)

        if self.can_exit_room:
            exit_info = self.room.check_room_exits()
            if exit_info is not None:
                target_room_name, target_x, target_y = exit_info
                self.change_room(target_room_name, target_x, target_y)

    def on_input(self, input_id: str, input_data: InputData) -> None:

        if self.in_transition:
            return

        if input_id == "pause" and input_data.pressed:
            self.state_machine.push(PauseState(self.state_machine))
        elif input_id == "phase_shift" and input_data.pressed:
            arena_is_active = (self.room.arena is not None and self.room.arena.state == "active")
            if self.room.map_name == "sala_future" or arena_is_active:
                return
            if self.player.toggle_phase():
                self.state_machine.push(PhaseShiftState(self.state_machine),phase_color=self.player.phase_color,)
        elif input_id == "prev_form" and input_data.pressed:
            self.player.cycle_skin(-1)
        elif input_id in ("next_form", "toggle_morph") and input_data.pressed:
            self.player.cycle_skin(1)
        else:
            self.player.on_input(input_id, input_data)

    def render(self, surface: pygame.Surface) -> None:
        self.room.render(surface)
        camera_x, camera_y = self.room.camera_offset
        self.player.render(surface, camera_x, camera_y)
        self.hud.render(surface, self.player, camera_x, camera_y)

        if self.fade_alpha > 0.0:
            clamped_alpha = int(max(0.0, min(255.0, self.fade_alpha)))
            self.fade_surface.fill((0, 0, 0, clamped_alpha))
            surface.blit(self.fade_surface, (0, 0))