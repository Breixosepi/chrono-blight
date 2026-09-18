from typing import Any
import pygame
from gale.timer import Timer

import settings


class Elevator:
    def __init__(
        self,
        room: Any,
        x: float,
        y: float,
        dest_map: str,
        start_state: str = "hidden",
        width: int = 80,
        height: int = 80,
    ):
        self.room = room
        self.start_y = y
        self.x = x
        self.y = y
        
        self.width = width
        self.height = height
        self.hitbox = pygame.Rect(int(x), int(y), self.width, self.height)
        
        self.dest_map = dest_map
        self.state = start_state
        self._timer_handle = None
        
        self.descend_speed = 90.0
        self.ascend_speed = 140.0
        
        self.tex_open = settings.TEXTURES.get("elevator_open")
        self.tex_closed = settings.TEXTURES.get("elevator_closed")
        
        if self.state in ("open", "arriving_open"):
            self.image = self.tex_open
        else:
            self.image = self.tex_closed
            
        if self.state == "descending":
            self.y = -float(self.height)
            self.hitbox.y = int(self.y)
        elif self.state == "arriving":
            cam_y = 0.0
            if hasattr(self.room, "camera"):
                cam_y = float(getattr(self.room.camera, "offset", (0.0, 0.0))[1])
            target_y = self.start_y - self.height
            self.y = min(target_y - 60.0, cam_y - float(self.height) - 10.0)
            self.hitbox.y = int(self.y)
            if hasattr(self.room, "player"):
                self._center_player(self.room.player)
                self.room.player.hidden = True
                self.room.player.active = False

    def _center_player(self, player: Any) -> None:
        player.x = self.x + (self.width // 2) - (player.hitbox.width // 2)
        player.y = self.y + self.height - player.hitbox.height
        player.hitbox.x = int(player.x)
        player.hitbox.y = int(player.y)

    def activate(self) -> None:
        if self.state in ("hidden", "hidden_permanently"):
            self.state = "descending"
            cam_y = 0.0
            if hasattr(self.room, "camera"):
                cam_y = float(getattr(self.room.camera, "offset", (0.0, 0.0))[1])
            self.y = max(-float(self.height), cam_y - float(self.height) - 10.0)
            self.hitbox.y = int(self.y)
            self.image = self.tex_closed
            if hasattr(self.room, "camera"):
                self.room.camera.shake(4.0, 1.2)
            if "rock-crack" in settings.SOUNDS:
                settings.SOUNDS["rock-crack"].play()
            if "close" in settings.SOUNDS:
                settings.SOUNDS["close"].play()

    def _finish_arriving_open(self) -> None:
        if self.state == "arriving_open":
            self.state = "departing"
            self.image = self.tex_closed
            settings.SOUNDS["open"].play()
            player = self.room.player
            player.state_machine.change("idle")
            player.active = True
            player.hidden = False

    def update(self, dt: float) -> None:
        if self.state in ("hidden", "hidden_permanently"):
            return
            
        if self.state == "descending":
            self.y += self.descend_speed * dt
            target_y = self.start_y - self.height
            if self.y >= target_y:
                self.y = target_y
                self.state = "open"
                self.image = self.tex_open
                if "rock-smash" in settings.SOUNDS:
                    settings.SOUNDS["rock-smash"].play()
                if "open" in settings.SOUNDS:
                    settings.SOUNDS["open"].play()
                if hasattr(self.room, "camera"):
                    self.room.camera.shake(3.0, 0.3)
                if hasattr(self.room, "spawn_dust"):
                    self.room.spawn_dust(self.hitbox.centerx, self.start_y, count=16)
                    
        elif self.state == "arriving":
            self.y += self.descend_speed * dt
            target_y = self.start_y - self.height
            player = self.room.player
            
            self._center_player(player)
            player.vy = 0.0
            player.vx = 0.0
            player.hidden = True
            player.active = False
            
            if self.y >= target_y:
                self.y = target_y
                self.state = "arriving_open"
                self.image = self.tex_open
                if hasattr(self.room, "camera"):
                    self.room.camera.shake(3.0, 0.25)
                if hasattr(self.room, "spawn_dust"):
                    self.room.spawn_dust(self.hitbox.centerx, self.start_y, count=16)
                player.hidden = False
                player.active = False
                self._center_player(player)
                self._timer_handle = Timer.after(0.8, self._finish_arriving_open)
                
        elif self.state == "arriving_open":
            player = self.room.player
            self._center_player(player)
            player.hidden = False
            player.active = False
                
        elif self.state == "departing":
            self.y -= self.ascend_speed * dt
            if hasattr(self.room, "camera") and self.y + self.height < self.room.camera.offset[1]:
                self.state = "hidden_permanently"
                
        elif self.state == "open":
            player = self.room.player
            dist_x = abs(self.hitbox.centerx - player.hitbox.centerx)
            dist_y = abs(self.hitbox.centery - player.hitbox.centery)
            
            from src.controls_manager import is_up_key_pressed
            keys = pygame.key.get_pressed()
            if dist_x < 30 and dist_y < 40 and is_up_key_pressed(keys):
                self.state = "ascending"
                self.image = self.tex_closed
                settings.SOUNDS["close"].play()
                player.state_machine.change("idle")
                player.vy = 0
                player.vx = 0
                self._center_player(player)
                player.active = False
                player.hidden = True
                
        elif self.state == "ascending":
            self.y -= self.ascend_speed * dt
            player = self.room.player
            self._center_player(player)
            player.active = False
            player.hidden = True
            
            if hasattr(self.room, "camera") and self.y + self.height < self.room.camera.offset[1]:
                if not self.room.play_state.in_transition:
                    player.arriving_via_elevator = True
                    player.hidden = True
                    player.active = False
                    self.room.play_state.change_room(self.dest_map, self.x, self.start_y)
                    
        self.hitbox.x = int(self.x)
        self.hitbox.y = int(self.y)

    def render(self, surface: pygame.Surface, camera_x: float, camera_y: float) -> None:
        if self.state in ("hidden", "hidden_permanently") or not self.image:
            return
            
        draw_x = int(self.x - camera_x)
        draw_y = int(self.y - camera_y)
        
        tex_w = self.image.get_width()
        offset_x = (self.width - tex_w) // 2
        
        rope_tex = settings.TEXTURES.get("elevator_rope")
        if rope_tex:
            rope_w = rope_tex.get_width()
            rope_h = rope_tex.get_height()
            rope_x = draw_x + offset_x + (tex_w // 2) - (rope_w // 2)
            
            curr_y = draw_y - rope_h
            while curr_y > -rope_h:
                surface.blit(rope_tex, (rope_x, curr_y))
                curr_y -= rope_h
                
        surface.blit(self.image, (draw_x + offset_x, draw_y))

        if self.state == "open" and hasattr(self.room, "player") and not self.room.player.is_dead():
            player = self.room.player
            dist_x = abs(self.hitbox.centerx - player.hitbox.centerx)
            dist_y = abs(self.hitbox.centery - player.hitbox.centery)
            if dist_x < 30 and dist_y < 40 and not getattr(player, "hidden", False):
                from src import controls_manager
                up_name = controls_manager.get_key_name(controls_manager.CURRENT_KEYBINDS.get("up", pygame.K_w))
                prompt_str = f"[{up_name}] SUBIR"
                import gale.text
                gale.text.render_text(
                    surface,
                    prompt_str,
                    settings.FONTS["hud_small"],
                    draw_x + self.width // 2,
                    draw_y - 12,
                    (255, 230, 90),
                    center=True,
                    shadowed=True,
                )