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
        settings.stop_music("intro")   # ensure intro isn't still playing
        settings.play_music("ambient")
        start_room_name = params.get("map_name", DEFAULT_START_ROOM)
        spawn_coordinates = params.get("spawn_point", DEFAULT_START_SPAWN)
        spawn_x, spawn_y = spawn_coordinates
        self.room = Room(map_name=start_room_name, spawn_x=spawn_x, spawn_y=spawn_y)
        self.room.play_state = self
        self.player = self.room.player
        
        self.current_slot: str = params.get("slot", "slot_1")
        self.cleared_events: set[str] = set()
        self.visited_rooms: set[str] = {"middle"}

        if "save_data" in params:
            save_data = params["save_data"]
            self.cleared_events = set(save_data.get("cleared_events", []))
            self.visited_rooms.update(save_data.get("visited_rooms", []))
            self.player.sync_progression(self.cleared_events)
            
            self.player.skin = save_data.get("player_skin", "mage")
            self.player.health = save_data.get("player_health", self.player.MAX_HEALTH)
            
        self.visited_rooms.add(self.room.map_name)
        self.room._check_cleared_events()
        self.hud = HUD()

        self.in_transition: bool = False
        self.waiting_for_unlock: bool = False
        self.can_exit_room: bool = True
        self.fade_alpha: float = 0.0
        self.fade_surface = pygame.Surface(
            (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA
        )

    def save_game_checkpoint(self, spawn_pos: Any = None) -> None:
        """Centralized save handler for checkpoints, altars and world events."""
        from gale.save import SaveManager
        sx = float(spawn_pos[0]) if spawn_pos else self.player.hitbox.centerx
        sy = float(spawn_pos[1]) if spawn_pos else (self.player.hitbox.top - 20)
        save_data = {
            "room": self.room.map_name,
            "spawn_x": sx,
            "spawn_y": sy,
            "player_health": self.player.health,
            "player_max_health": self.player.MAX_HEALTH,
            "player_skin": self.player.skin,
            "cleared_events": list(self.cleared_events),
            "visited_rooms": list(self.visited_rooms),
        }
        metadata = {
            "room_name": self.room.map_name,
            "health": self.player.health,
            "skin": self.player.skin,
        }
        SaveManager().save(self.current_slot, save_data, metadata=metadata)

    def change_room(self, target_room_name: str, target_spawn_x: float, target_spawn_y: float) -> None:
        if self.in_transition:
            return

        if "lava" in settings.SOUNDS:
            settings.SOUNDS["lava"].stop()

        if self.room.map_name in ("subida", "subida_past", "subida_future"):
            if "subida_cleared" not in self.cleared_events:
                self.cleared_events.add("subida_cleared")

        self.in_transition = True
        self._halt_player()

        self._start_fade_out(target_room_name, target_spawn_x, target_spawn_y)

    def _start_fade_out(self, target_room_name: str, target_spawn_x: float, target_spawn_y: float) -> None:
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
        if "lava" in settings.SOUNDS:
            settings.SOUNDS["lava"].stop()
        self.visited_rooms.add(target_room_name)
        self.room = Room(
            map_name=target_room_name,
            spawn_x=target_spawn_x,
            spawn_y=target_spawn_y,
            player=self.player,
        )
        self.room.play_state = self
        self.room._check_cleared_events()
        if getattr(self.player, "active", True):
            self._halt_player()

        if target_room_name == "esquina_1" and "subida_cleared" in self.cleared_events and "morph" not in self.player.available_skins:
            self.waiting_for_unlock = True
            self.player.x = 200.0
            self.player.y = 120.0
            self.player.hitbox.topleft = (int(self.player.x), int(self.player.y))
            self.player.on_ground = True
            self.player.change_state("unlock", form="morph")

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

    def respawn_at_checkpoint(self) -> None:
        if "lava" in settings.SOUNDS:
            settings.SOUNDS["lava"].stop()
        from gale.save import SaveManager
        save_data = SaveManager().load(self.current_slot)
        if not save_data:
            target_room = "middle"
            target_x, target_y = 64.0, 208.0
        else:
            target_room = save_data.get("room", "middle")
            target_x = float(save_data.get("spawn_x", 64.0))
            target_y = float(save_data.get("spawn_y", 208.0))
            self.cleared_events = set(save_data.get("cleared_events", []))
            self.visited_rooms.update(save_data.get("visited_rooms", []))

        self.visited_rooms.add(target_room)
        self.room = Room(
            map_name=target_room,
            spawn_x=target_x,
            spawn_y=target_y,
            player=self.player,
        )
        self.room.play_state = self
        self.player.restore_all_forms()
        self.player.sync_progression(self.cleared_events)
        self.player.state_machine.change("idle")
        self.player.vx = 0.0
        self.player.vy = 0.0
        self.room._check_cleared_events()
        self.in_transition = False
        self.waiting_for_unlock = False

    def update(self, dt: float) -> None:
        if self.player.is_dead() and self.player.is_animation_finished():
            self.state_machine.push(GameOverState(self.state_machine), play_state=self)
            return

        if self.in_transition and not self.waiting_for_unlock:
            return

        self.room.update(dt)

        if self.can_exit_room and not self.in_transition:
            exit_info = self.room.check_room_exits()
            if exit_info is not None:
                target_room_name, target_x, target_y = exit_info
                self.change_room(target_room_name, target_x, target_y)

    def on_input(self, input_id: str, input_data: InputData) -> None:

        if self.in_transition:
            return

        if input_id == "pause" and input_data.pressed:
            self.state_machine.push(PauseState(self.state_machine), play_state=self)
        elif input_id == "map" and input_data.pressed:
            from src.states.game.MapState import MapState
            self.state_machine.push(MapState(self.state_machine), play_state=self)
        elif not getattr(self.player, "active", True):
            return
        elif input_id == "phase_shift" and input_data.pressed:
            if self.room.map_name == "sala_future":
                return
            if self.player.toggle_phase():
                self.state_machine.push(PhaseShiftState(self.state_machine), phase_color=self.player.phase_color)
        elif input_id == "prev_form" and input_data.pressed:
            self.player.cycle_skin(-1)
        elif input_id in ("next_form", "toggle_morph") and input_data.pressed:
            self.player.cycle_skin(1)
        else:
            self.player.on_input(input_id, input_data)

    def render(self, surface: pygame.Surface) -> None:
        self.room.render(surface)
        camera_x, camera_y = self.room.camera_offset
        self.hud.render(surface, self.player, camera_x, camera_y)

        if self.fade_alpha > 0.0:
            clamped_alpha = int(max(0.0, min(255.0, self.fade_alpha)))
            self.fade_surface.fill((0, 0, 0, clamped_alpha))
            surface.blit(self.fade_surface, (0, 0))