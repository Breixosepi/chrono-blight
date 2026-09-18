from typing import Any, List, Optional
import pygame
from gale.animation import Animation
from gale.timer import Timer, After

import settings
from src.entities.Player import Player


class Altar:
    _SCALED_FRAMES: Optional[List[pygame.Surface]] = None
    _ARROW_FRAMES: Optional[List[pygame.Surface]] = None
    _SAVE_FRAMES: Optional[List[pygame.Surface]] = None

    def __init__(self, x: float, y: float, room: Any, obj_height: float = 16.0) -> None:
        self.width = 48
        self.height = 96
        self.room = room

        self.x = x - 16.0
        self.y = y + obj_height - self.height

        self._init_shared_surfaces()

        self.anim_obelisk = Animation(self._SCALED_FRAMES, 0.18, loops=1)
        self.anim_arrow = Animation(self._ARROW_FRAMES, 0.16)
        self.anim_save = Animation(self._SAVE_FRAMES, 0.08)

        self.is_animating = False
        self.is_saving = False
        self.show_prompt = False
        self._save_timer: Optional[After] = None

        self.hitbox = pygame.Rect(int(self.x + 8), int(self.y + self.height - 32), self.width - 16, 32)
        self.interaction_rect = pygame.Rect(int(self.x - 20), int(self.y), self.width + 40, self.height)

    @classmethod
    def _init_shared_surfaces(cls) -> None:
        if cls._SCALED_FRAMES is None:
            obelisk_tex = settings.TEXTURES["obelisk"]
            obelisk_rects = settings.FRAMES["obelisk"]
            cls._SCALED_FRAMES = [
                pygame.transform.scale(obelisk_tex.subsurface(r), (48, 96))
                for r in obelisk_rects
            ]

        if cls._ARROW_FRAMES is None:
            kb_tex = settings.TEXTURES["keyboard_ui"]
            cols = kb_tex.get_width() // 16
            start_idx = (192 // 16) * cols + (192 // 16)
            cls._ARROW_FRAMES = [
                kb_tex.subsurface(settings.FRAMES["keyboard_ui"][start_idx + i])
                for i in range(4)
            ]

        if cls._SAVE_FRAMES is None:
            save_tex = settings.TEXTURES["save_icon"]
            save_rects = settings.FRAMES["save_icon"]
            cls._SAVE_FRAMES = [save_tex.subsurface(r) for r in save_rects]

    def update(self, dt: float, player: Player) -> None:
        if self.is_animating:
            self.anim_obelisk.update(dt)
            if self.anim_obelisk.times_played > 0:
                self.is_animating = False
                self.anim_obelisk.reset()

        self.show_prompt = self.interaction_rect.colliderect(player.hitbox)
        if self.show_prompt:
            self.anim_arrow.update(dt)
            if player.is_looking_up and not self.is_saving:
                self.interact(player)

        if self.is_saving:
            self.anim_save.update(dt)

    def interact(self, player: Player) -> None:
        settings.SOUNDS["save"].play()
        self.is_animating = True
        self.is_saving = True
        self.anim_obelisk.reset()

        player.restore_all_forms()

        if hasattr(self.room, "_spawn_popup"):
            self.room._spawn_popup("¡FORMAS RESTAURADAS!", player.hitbox.centerx, player.hitbox.top - 20, 2.0, (120, 255, 180))

        play_state = getattr(self.room, "play_state", None)
        if play_state and hasattr(play_state, "save_game_checkpoint"):
            play_state.save_game_checkpoint(spawn_pos=(self.hitbox.centerx, self.hitbox.top - 20))

        if self._save_timer:
            self._save_timer.remove()
        self._save_timer = Timer.after(2.4, self._finish_saving)

    def _finish_saving(self) -> None:
        self.is_saving = False
        self._save_timer = None

    def render(self, surface: pygame.Surface, camera_x: float, camera_y: float) -> None:
        frame = self.anim_obelisk.get_current_frame() if self.is_animating else self._SCALED_FRAMES[0]
        surface.blit(frame, (int(self.x - camera_x), int(self.y - camera_y)))

        if self.show_prompt and not self.is_saving and hasattr(self.room, "player"):
            arrow_frame = self.anim_arrow.get_current_frame()
            prompt_x = self.room.player.hitbox.centerx - 8 - camera_x
            prompt_y = self.room.player.hitbox.top - 18 - camera_y
            surface.blit(arrow_frame, (int(prompt_x), int(prompt_y)))

    def render_ui(self, surface: pygame.Surface) -> None:
        if self.is_saving:
            icon_frame = self.anim_save.get_current_frame()
            icon_rect = icon_frame.get_rect(bottomright=(settings.VIRTUAL_WIDTH - 10, settings.VIRTUAL_HEIGHT - 10))
            surface.blit(icon_frame, icon_rect)