from typing import Any
import pygame
from gale.timer import Timer
from gale.save import SaveManager

import settings
from src.entities.Player import Player

class Altar:
    def __init__(self, x: float, y: float, room: Any, obj_height: float = 16.0):
        self.width = 48
        self.height = 96
        
        self.x = x - 16
        self.y = y + obj_height - self.height
        self.room = room
        
        obelisk_tex = settings.TEXTURES["obelisk"]
        obelisk_rects = settings.FRAMES["obelisk"]
        self.frames = [
            pygame.transform.scale(obelisk_tex.subsurface(r), (self.width, self.height))
            for r in obelisk_rects
        ]
        
        self.frame_index = 0.0
        self.is_animating = False
        
        self.hitbox = pygame.Rect(int(self.x + 8), int(self.y + self.height - 32), self.width - 16, 32)
        self.interaction_rect = pygame.Rect(int(self.x - 20), int(self.y), self.width + 40, self.height)
        
        kb_tex = settings.TEXTURES["keyboard_ui"]
        arrow_rects = [pygame.Rect(192 + i * 16, 192, 16, 16) for i in range(4)]
        self.arrow_frames = [kb_tex.subsurface(r) for r in arrow_rects]
        self.arrow_index = 0.0
        self.show_prompt = False

        save_icon_tex = settings.TEXTURES["save_icon"]
        save_icon_rects = settings.FRAMES["save_icon"]
        self.save_icon_frames = [save_icon_tex.subsurface(r) for r in save_icon_rects]
        self.save_icon_index = 0.0
        self.is_saving = False

    def update(self, dt: float, player: Player) -> None:
        if self.is_animating:
            self.frame_index += 10.0 * dt
            if self.frame_index >= len(self.frames):
                self.frame_index = 0.0
                self.is_animating = False
        else:
            self.frame_index = 0.0

        self.show_prompt = self.interaction_rect.colliderect(player.hitbox)

        if self.show_prompt:
            self.arrow_index += 6.0 * dt
            if self.arrow_index >= len(self.arrow_frames):
                self.arrow_index = 0.0

            if player.is_looking_up and not self.is_saving:
                self.interact(player)

        if self.is_saving:
            self.save_icon_index += 12.0 * dt
            if self.save_icon_index >= len(self.save_icon_frames):
                self.save_icon_index = 0.0

    def interact(self, player: Player) -> None:
        self.is_animating = True
        self.frame_index = 0.0
        self.is_saving = True
        
        player.available_skins = ["mage", "morph", "sword"]
        for form_key, stats in player.form_stats.items():
            stats["health"] = stats["max_health"]
            stats["mana"] = stats["max_mana"]
        player.health = player.MAX_HEALTH
        
        play_state = getattr(self.room, "play_state", None)
        slot = getattr(play_state, "current_slot", "slot_1") if play_state else "slot_1"
        cleared = list(getattr(play_state, "cleared_events", [])) if play_state else []
        
        save_data = {
            "room": self.room.map_name,
            "spawn_x": self.hitbox.centerx,
            "spawn_y": self.hitbox.top - 20,
            "player_health": player.health,
            "player_max_health": player.MAX_HEALTH,
            "player_skin": player.skin,
            "cleared_events": cleared,
        }
        
        metadata = {
            "room_name": self.room.map_name,
            "health": player.health,
            "skin": player.skin,
        }
        
        manager = SaveManager()
        manager.save(slot, save_data, metadata=metadata)
        
        Timer.after(2.0, self._finish_saving)

    def _finish_saving(self) -> None:
        self.is_saving = False

    def render(self, surface: pygame.Surface, camera_x: float, camera_y: float) -> None:
        frame = self.frames[int(self.frame_index)]
        surface.blit(frame, (int(self.x - camera_x), int(self.y - camera_y)))

        if self.show_prompt and not self.is_saving and hasattr(self.room, "player"):
            arrow_frame = self.arrow_frames[int(self.arrow_index)]
            prompt_x = self.room.player.hitbox.centerx - 8 - camera_x
            prompt_y = self.room.player.hitbox.top - 18 - camera_y
            surface.blit(arrow_frame, (int(prompt_x), int(prompt_y)))

    def render_ui(self, surface: pygame.Surface) -> None:
        if self.is_saving:
            icon_frame = self.save_icon_frames[int(self.save_icon_index)]
            icon_rect = icon_frame.get_rect(bottomright=(settings.VIRTUAL_WIDTH - 10, settings.VIRTUAL_HEIGHT - 10))
            surface.blit(icon_frame, icon_rect)

