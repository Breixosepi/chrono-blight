"""
Chrono Blight - Heads-Up Display (HUD)
Diseño Micro-Slim con Cristal Cronológico, Cooldown Radial y Transparencia Inteligente.
"""

import math
from typing import TYPE_CHECKING
import pygame
import settings

if TYPE_CHECKING:
    from src.entities.Player import Player

_FACE_CENTERS: dict[str, tuple[int, int]] = {
    "sword": (34, 34),
    "morph": (33, 34),
    "mage":  (33, 30),
}


class HUD:

    def __init__(self) -> None:
        self.width: int = 88
        self.height: int = 36
        self.avatar_size: int = 18
        self._avatar_cache: dict[tuple[str, str], pygame.Surface] = {}

    def _get_avatar(self, skin: str, color: str) -> pygame.Surface:
        key = (skin, color)
        if key in self._avatar_cache:
            return self._avatar_cache[key]

        texture_key = f"{skin}_{color}"
        texture = settings.TEXTURES.get(texture_key)
        frame0_key = f"{skin}_red"
        frames = settings.FRAMES.get(frame0_key)

        if not texture or not frames:
            surf = pygame.Surface((self.avatar_size, self.avatar_size), pygame.SRCALPHA)
            pygame.draw.circle( surf, (60, 60, 80), (self.avatar_size // 2, self.avatar_size // 2), self.avatar_size // 2, )
            return surf

        frame0: pygame.Rect = frames[0]
        cx, cy = _FACE_CENTERS.get(skin, (33, 32))
        half = 7

        src_rect = pygame.Rect(frame0.x + cx - half, frame0.y + cy - half, half * 2, half * 2)
        face_sub = texture.subsurface(src_rect)
        scaled_face = pygame.transform.scale(face_sub, (self.avatar_size, self.avatar_size))

        avatar = pygame.Surface((self.avatar_size, self.avatar_size), pygame.SRCALPHA)

        bg_circle_col = {
            "mage": (32, 24, 42, 255),
            "sword": (42, 38, 22, 255),
            "morph": (20, 36, 26, 255),
        }.get(skin, (24, 26, 34, 255))

        pygame.draw.circle( avatar, bg_circle_col, (self.avatar_size // 2, self.avatar_size // 2), self.avatar_size // 2, )
        avatar.blit(scaled_face, (0, 0))

        mask = pygame.Surface((self.avatar_size, self.avatar_size), pygame.SRCALPHA)
        pygame.draw.circle( mask, (255, 255, 255, 255), (self.avatar_size // 2, self.avatar_size // 2), self.avatar_size // 2, )
        avatar.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)

        self._avatar_cache[key] = avatar
        return avatar

    def _draw_form_cooldown_ring(
        self,
        surf: pygame.Surface,
        cx: int,
        cy: int,
        radius: int,
        active_color: tuple[int, int, int],
        cooldown_timer: float,
        cooldown_max: float,
    ) -> None:
        if cooldown_timer <= 0.0 or cooldown_max <= 0.0:
            pygame.draw.circle(surf, active_color, (cx, cy), radius, 1)
            return

        cd_ratio = cooldown_timer / cooldown_max
        progress = max(0.0, min(1.0, 1.0 - cd_ratio))

        pygame.draw.circle(surf, (42, 44, 58), (cx, cy), radius, 1)

        max_deg = int(progress * 360)
        arc_color = (255, 220, 90) 

        for deg in range(0, max_deg + 1, 3):
            rad = math.radians(deg) - math.pi / 2.0
            px = int(round(cx + radius * math.cos(rad)))
            py = int(round(cy + radius * math.sin(rad)))
            surf.set_at((px, py), arc_color)

        if max_deg > 0:
            tip_rad = math.radians(max_deg) - math.pi / 2.0
            tip_x = int(round(cx + radius * math.cos(tip_rad)))
            tip_y = int(round(cy + radius * math.sin(tip_rad)))
            surf.set_at((tip_x, tip_y), (255, 255, 255))

    def _draw_chrono_crystal( self, surf: pygame.Surface, cx: int, cy: int, phase_color: str, cooldown_timer: float, cooldown_max: float, ) -> None:
        pts = [(cx, cy - 4), (cx + 5, cy), (cx, cy + 4), (cx - 5, cy)]

        if phase_color == "red":
            fill_col = (235, 55, 65)
            border_col = (255, 185, 195)
        else:
            fill_col = (45, 215, 110)
            border_col = (185, 255, 205)

        if cooldown_timer > 0.0 and cooldown_max > 0.0:
            cd_ratio = cooldown_timer / cooldown_max
            pygame.draw.polygon(surf, (38, 40, 48), pts)
            pygame.draw.polygon(surf, (75, 78, 90), pts, 1)

            fill_h = int(9 * (1.0 - cd_ratio))
            if fill_h > 0:
                clip_rect = pygame.Rect(cx - 5, cy + 4 - fill_h, 11, fill_h)
                surf.set_clip(clip_rect)
                pygame.draw.polygon(surf, fill_col, pts)
                surf.set_clip(None)
        else:
            pygame.draw.polygon(surf, fill_col, pts)
            pygame.draw.polygon(surf, border_col, pts, 1)
            pygame.draw.line(surf, (255, 255, 255), (cx, cy - 2), (cx + 2, cy))

    def render( self, surface: pygame.Surface, player: "Player", cam_x: float = 0.0, cam_y: float = 0.0, ) -> None:
        base_x = 4
        base_y = 4
        font = settings.FONTS.get("hud_small")
        font_number = settings.FONTS.get("hud")
        if not font:
            return

        form_colors = {
            "mage":  (185, 115, 245),  # Purple
            "morph": (70, 215, 120),   # Green
            "sword": (245, 195, 65),   # Golden
        }
        active_color = form_colors.get(player.skin, (220, 220, 220))

        #HUD
        hud_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        hud_surf.fill((14, 15, 22, 225))
        pygame.draw.rect(hud_surf, active_color, pygame.Rect(0, 0, self.width, self.height), 1, border_radius=2)

        # avatar circle
        av_x = 4
        av_y = 4
        avatar = self._get_avatar(player.skin, player.phase_color)
        hud_surf.blit(avatar, (av_x, av_y))

        # form changes
        radius = self.avatar_size // 2
        center_x = av_x + radius
        center_y = av_y + radius
        skin_cd = getattr(player, "skin_cooldown_timer", 0.0)
        skin_max = getattr(player, "skin_cooldown_max", 5.0)
        self._draw_form_cooldown_ring(hud_surf, center_x, center_y, radius, active_color, skin_cd, skin_max)

        #fase change
        crystal_cx = av_x + radius
        crystal_cy = 27
        phase_cd = getattr(player, "phase_cooldown_timer", 0.0)
        phase_max = getattr(player, "phase_cooldown_max", 2.0)
        self._draw_chrono_crystal(hud_surf, crystal_cx, crystal_cy, player.phase_color, phase_cd, phase_max)

        # HP and MP
        tx = 25
        right_margin = self.width - 4
        bar_x = tx + 12
        bar_w = 26
        bar_h = 3

        # HP 
        row_hp_y = 0
        hp_lbl = font.render("HP", False, (240, 95, 95))
        hud_surf.blit(hp_lbl, (tx, row_hp_y))

        hp_num_surf = font_number.render(f"{int(player.health)}", False, (225, 225, 225))
        hud_surf.blit(hp_num_surf, (right_margin - hp_num_surf.get_width(), row_hp_y - 2))

        hp_bar_y = row_hp_y + 8
        pygame.draw.rect(hud_surf, (28, 12, 14), pygame.Rect(bar_x, hp_bar_y, bar_w, bar_h))
        hp_ratio = max(0.0, min(1.0, player.health / player.MAX_HEALTH)) if player.MAX_HEALTH > 0 else 0.0
        fill_hp = int(bar_w * hp_ratio)
        if fill_hp > 0:
            pygame.draw.rect(hud_surf, (215, 45, 55), pygame.Rect(bar_x, hp_bar_y, fill_hp, bar_h))
            pygame.draw.line(hud_surf, (255, 120, 130), (bar_x, hp_bar_y), (bar_x + fill_hp - 1, hp_bar_y))
        pygame.draw.rect(hud_surf, (70, 35, 40), pygame.Rect(bar_x, hp_bar_y, bar_w, bar_h), 1)

        # MP 
        row_mp_y = 10
        mp_lbl = font.render("MP", False, (75, 165, 245))
        hud_surf.blit(mp_lbl, (tx, row_mp_y))

        mp_num_surf = font_number.render(f"{int(player.mana)}", False, (205, 225, 245))
        hud_surf.blit(mp_num_surf, (right_margin - mp_num_surf.get_width(), row_mp_y - 1))

        mp_bar_y = row_mp_y + 8
        pygame.draw.rect(hud_surf, (12, 20, 32), pygame.Rect(bar_x, mp_bar_y, bar_w, bar_h))
        mp_ratio = max(0.0, min(1.0, player.mana / player.MAX_MANA)) if player.MAX_MANA > 0 else 0.0
        fill_mp = int(bar_w * mp_ratio)
        if fill_mp > 0:
            pygame.draw.rect(hud_surf, (45, 135, 235), pygame.Rect(bar_x, mp_bar_y, fill_mp, bar_h))
            pygame.draw.line(hud_surf, (130, 205, 255), (bar_x, mp_bar_y), (bar_x + fill_mp - 1, mp_bar_y))
        pygame.draw.rect(hud_surf, (30, 60, 90), pygame.Rect(bar_x, mp_bar_y, bar_w, bar_h), 1)

        # DYNAMIC FORMS
        row_forms_y = 20
        skin_cd = getattr(player, "skin_cooldown_timer", 0.0)
        
        unlocked = []
        for label, form_key in [("MAG", "mage"), ("SWD", "sword"), ("MOR", "morph")]:
            if form_key in player.available_skins:
                unlocked.append((label, form_key))
                
        n = len(unlocked)
        # Center of the forms area is roughly x=54 (from 24 to 84)
        if n == 1:
            positions = [54]
        elif n == 2:
            positions = [38, 70]
        else:
            positions = [31, 54, 77]
            
        for i, (label, form_key) in enumerate(unlocked):
            fx = positions[i]
            if form_key == player.skin:
                col = form_colors[form_key]
            else:
                col = (85, 90, 105) if skin_cd > 0.0 else (120, 125, 140)

            f_surf = font.render(label, False, col)
            f_rect = f_surf.get_rect(midtop=(fx, row_forms_y))
            hud_surf.blit(f_surf, f_rect)

        player_screen_x = player.x - cam_x
        player_screen_y = player.y - cam_y
        is_behind_hud = (player_screen_x < base_x + self.width + 12) and (player_screen_y < base_y + self.height + 12)

        has_banner = False
        if player.state_name == "unlock":
            has_banner = True
        room = getattr(player, "room", None)
        if room:
            if getattr(room, "arena", None) and getattr(room.arena, "banner_text", None):
                has_banner = True
            for p in getattr(room, "damage_popups", []):
                popup_sx = p["x"] - cam_x
                popup_sy = p["y"] - cam_y
                if (popup_sx < base_x + self.width + 16) and (popup_sy < base_y + self.height + 16):
                    has_banner = True
                    break

        if is_behind_hud or has_banner:
            hud_surf.set_alpha(65)
        else:
            hud_surf.set_alpha(245)

        surface.blit(hud_surf, (base_x, base_y))
