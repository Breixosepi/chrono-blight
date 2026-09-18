"""
Chrono Blight - World Map State (Humble Gift UI Style)
"""
from typing import Any, Dict, List, Optional, Tuple, Set
import math
import pygame
from gale.state import BaseState
from gale.input_handler import InputData
from gale.timer import Timer
from gale.text import render_text

import settings


class MapState(BaseState):
    """
    World Map screen accessible via [M].
    Features:
      - Parchment UI inspired by Humble Gift (Frc_nf.gif & ps3Urw.gif).
      - Visited rooms rendered clearly with POI mini-icons.
      - Defeated bosses stamped with an 'X'.
      - Unvisited rooms rendered shrouded in diffuse fog with a '?'.
      - Player location beacon.
      - Bottom INFO card detailing the inspected room.
      - Arrow key navigation to inspect connected rooms.
    """

    ROOM_DEFINITIONS: Dict[str, Dict[str, Any]] = {
        "middle": {
            "name": "SALA CENTRAL",
            "rect": pygame.Rect(166, 58, 44, 34),
            "poi": "altar",
            "desc": "Altar ancestral de guardado y restauracion total.",
            "desc_cleared": "Altar ancestral de guardado y restauracion total.",
        },
        "big_room": {
            "name": "GRAN SALON DEL NORTE",
            "rect": pygame.Rect(154, 30, 76, 16),
            "poi": "final_boss",
            "desc": "Camara monumental sellada en la cuspide.",
            "desc_cleared": "El bastion supremo ha sido conquistado.",
        },
        "left_corner": {
            "name": "CAMARA DEL OBELISCO NOROESTE",
            "rect": pygame.Rect(104, 54, 46, 20),
            "poi": "obelisk",
            "desc": "Monolito sagrado y conector hacia el futuro.",
            "desc_cleared": "Monolito sagrado y conector hacia el futuro.",
        },
        "sala_future": {
            "name": "CATEDRAL DEL CULTISTA",
            "rect": pygame.Rect(104, 30, 46, 16),
            "poi": "boss_cultist",
            "event": "boss_cultist_defeated",
            "desc": "Dominio del Sumo Sacerdote Cultista.",
            "desc_cleared": "Sacerdote derrotado. Elevador activado.",
        },
        "abismo_fixed": {
            "name": "ABISMO SUBTERRANEO",
            "rect": pygame.Rect(104, 78, 46, 20),
            "poi": "falling_block",
            "desc": "Pasaje precario con plataformas desmoronables.",
            "desc_cleared": "Pasaje precario con plataformas desmoronables.",
        },
        "sala_past": {
            "name": "ARENA DEL PASADO",
            "rect": pygame.Rect(50, 78, 46, 20),
            "poi": "boss_past",
            "event": "survival_boss_defeated",
            "desc": "Prueba de supervivencia ante el Gran Monstruo.",
            "desc_cleared": "Supervivencia superada. Forma Caballero obtenida.",
        },
        "esquina_1": {
            "name": "ESQUINA SUPERIOR NORESTE",
            "rect": pygame.Rect(226, 54, 46, 20),
            "poi": "obelisk",
            "desc": "Monolito resonante tras el ascenso.",
            "desc_cleared": "Forma Morph desbloqueada en este sector.",
        },
        "subida": {
            "name": "SUBIDA AL ABISMO",
            "rect": pygame.Rect(232, 78, 34, 32),
            "poi": "lava",
            "event": "subida_cleared",
            "desc": "Peligro letal: Lava y acido ascendente.",
            "desc_cleared": "Escapatoria completada con exito.",
        },
    }

    # Interconnected straight architectural doors: (room_a, room_b, rect)
    CORRIDORS: List[Tuple[str, str, pygame.Rect]] = [
        # middle -> big_room (straight vertical doorway)
        ("middle", "big_room", pygame.Rect(184, 46, 8, 12)),
        # left_corner -> sala_future (straight vertical doorway)
        ("left_corner", "sala_future", pygame.Rect(123, 46, 8, 8)),
        # sala_past -> abismo_fixed (straight horizontal doorway)
        ("sala_past", "abismo_fixed", pygame.Rect(96, 84, 8, 8)),
        # esquina_1 -> subida (straight vertical doorway)
        ("esquina_1", "subida", pygame.Rect(245, 74, 8, 4)),
        # middle upper-left -> left_corner (straight horizontal doorway)
        ("middle", "left_corner", pygame.Rect(150, 60, 16, 8)),
        # middle lower-left -> abismo_fixed (straight horizontal doorway)
        ("middle", "abismo_fixed", pygame.Rect(150, 82, 16, 8)),
        # middle upper-right -> esquina_1 (straight horizontal doorway)
        ("middle", "esquina_1", pygame.Rect(210, 60, 16, 8)),
        # middle lower-right -> subida (straight horizontal doorway)
        ("middle", "subida", pygame.Rect(210, 82, 22, 8)),
    ]

    ROOM_ORDER: List[str] = [
        "middle",
        "left_corner",
        "sala_future",
        "abismo_fixed",
        "sala_past",
        "esquina_1",
        "subida",
        "big_room",
    ]

    def __init__(self, state_machine: Any, play_state: Any = None, **kwargs: Any) -> None:
        super().__init__(state_machine)
        self.play_state = play_state

    def enter(self, play_state: Any = None, **params: Any) -> None:
        if play_state is not None:
            self.play_state = play_state
        elif self.play_state is None and hasattr(self.state_machine, "states"):
            for s in reversed(self.state_machine.states):
                if hasattr(s, "visited_rooms"):
                    self.play_state = s
                    break

        self.current_room_key: str = (
            self.play_state.room.map_name if self.play_state and self.play_state.room else "middle"
        )
        self.visited_rooms: Set[str] = (
            getattr(self.play_state, "visited_rooms", {"middle"}) if self.play_state else {"middle"}
        )
        self.cleared_events: Set[str] = (
            getattr(self.play_state, "cleared_events", set()) if self.play_state else set()
        )

        # Selected room for bottom info card inspection
        self.inspected_room_key: str = self.current_room_key
        self.pulse_timer: float = 0.0

        # Animation states
        self.open_progress: float = 0.0
        self.is_closing: bool = False

        # Page Dimensions
        self.PAGE_W: int = 304
        self.PAGE_H: int = 168

        # Cursor interpolation (starts directly at inspected room rect)
        cur_r = self.ROOM_DEFINITIONS[self.inspected_room_key]["rect"]
        self.cursor_x: float = float(cur_r.x)
        self.cursor_y: float = float(cur_r.y)
        self.cursor_w: float = float(cur_r.w)
        self.cursor_h: float = float(cur_r.h)

        # Initialize icons
        self._init_icons()

        # Trigger paper unfolding animation
        settings.SOUNDS["paper-unfold"].play()
        Timer.tween(
            0.24,
            [(self, {"open_progress": 1.0})],
            ease_function_name="out_back",
        )

    def _start_close(self, on_finish_callback: Optional[Any] = None) -> None:
        if self.is_closing:
            return
        self.is_closing = True
        settings.SOUNDS["paper-fold"].play()
        cb = on_finish_callback if on_finish_callback else self.state_machine.pop
        Timer.tween(
            0.16,
            [(self, {"open_progress": 0.0})],
            ease_function_name="in_back",
            on_finish=cb,
        )

    def _init_icons(self) -> None:
        self.icons: Dict[str, pygame.Surface] = {}
        try:
            # Altar
            save_tex = settings.TEXTURES.get("save_icon")
            if save_tex:
                self.icons["altar"] = pygame.transform.scale(
                    save_tex.subsurface((0, 0, 16, 16)), (12, 12)
                )

            # Falling block
            block_tex = settings.TEXTURES.get("destructible_block")
            if block_tex:
                self.icons["falling_block"] = pygame.transform.scale(
                    block_tex.subsurface((0, 0, 32, 32)), (12, 12)
                )

            # Cultist boss face
            self.icons["boss_cultist"] = self._create_cultist_icon()

            # Past monster boss face
            self.icons["boss_past"] = self._create_monster_icon()

            # Obelisk (high-contrast runic pillar)
            self.icons["obelisk"] = self._create_obelisk_icon()

            # Lava hazard (molten fire drop)
            self.icons["lava"] = self._create_lava_icon()

            # Final boss skull
            self.icons["final_boss"] = self._create_skull_icon()
        except Exception:
            pass

    def _create_cultist_icon(self) -> pygame.Surface:
        surf = pygame.Surface((12, 12), pygame.SRCALPHA)
        # Hooded cultist
        pygame.draw.polygon(surf, (85, 35, 95), [(6, 1), (10, 5), (10, 11), (2, 11), (2, 5)])
        # Shadowed face
        pygame.draw.polygon(surf, (30, 18, 35), [(6, 4), (9, 7), (9, 10), (3, 10), (3, 7)])
        # Glowing purple sinister eyes
        pygame.draw.rect(surf, (225, 80, 255), (4, 7, 2, 1))
        pygame.draw.rect(surf, (225, 80, 255), (7, 7, 2, 1))
        return surf

    def _create_monster_icon(self) -> pygame.Surface:
        surf = pygame.Surface((12, 12), pygame.SRCALPHA)
        # Abyssal horned monster icon
        # Horns
        pygame.draw.polygon(surf, (190, 45, 45), [(1, 1), (4, 4), (1, 5)])
        pygame.draw.polygon(surf, (190, 45, 45), [(10, 1), (7, 4), (10, 5)])
        # Head / maw
        pygame.draw.rect(surf, (44, 25, 35), (2, 4, 8, 7), border_radius=2)
        # Glowing crimson eyes
        pygame.draw.rect(surf, (255, 50, 40), (4, 6, 2, 2))
        pygame.draw.rect(surf, (255, 50, 40), (7, 6, 2, 2))
        # Fangs
        pygame.draw.line(surf, (240, 220, 190), (4, 10), (4, 11), 1)
        pygame.draw.line(surf, (240, 220, 190), (7, 10), (7, 11), 1)
        return surf

    def _create_obelisk_icon(self) -> pygame.Surface:
        surf = pygame.Surface((14, 14), pygame.SRCALPHA)
        # Base pedestal
        pygame.draw.rect(surf, (44, 30, 40), (2, 10, 10, 3))
        pygame.draw.rect(surf, (90, 85, 110), (3, 10, 8, 2))
        # Pillar
        pygame.draw.polygon(surf, (44, 30, 40), [(4, 10), (10, 10), (9, 3), (5, 3)])
        pygame.draw.polygon(surf, (120, 115, 145), [(5, 9), (9, 9), (8, 4), (6, 4)])
        # Glowing cyan rune
        pygame.draw.circle(surf, (40, 200, 255), (7, 6), 2)
        pygame.draw.circle(surf, (220, 245, 255), (7, 6), 1)
        return surf

    def _create_lava_icon(self) -> pygame.Surface:
        surf = pygame.Surface((14, 14), pygame.SRCALPHA)
        # Molten lava droplet / flame
        pts_out = [(7, 1), (12, 7), (10, 12), (4, 12), (2, 7)]
        pygame.draw.polygon(surf, (44, 30, 40), pts_out)
        pts_in = [(7, 2), (11, 7), (9, 11), (5, 11), (3, 7)]
        pygame.draw.polygon(surf, (240, 75, 30), pts_in)
        pts_core = [(7, 5), (9, 8), (8, 10), (6, 10), (5, 8)]
        pygame.draw.polygon(surf, (255, 220, 50), pts_core)
        return surf

    def _create_skull_icon(self) -> pygame.Surface:
        surf = pygame.Surface((12, 12), pygame.SRCALPHA)
        # Stylized skull / crown shape
        pygame.draw.rect(surf, (220, 50, 50), (2, 2, 8, 6))
        pygame.draw.rect(surf, (220, 50, 50), (4, 8, 4, 3))
        pygame.draw.rect(surf, (40, 20, 20), (3, 4, 2, 2))
        pygame.draw.rect(surf, (40, 20, 20), (7, 4, 2, 2))
        return surf

    def update(self, dt: float) -> None:
        self.pulse_timer += dt

        # Smooth cursor interpolation (lerp towards target room rect)
        target_r = self.ROOM_DEFINITIONS[self.inspected_room_key]["rect"]
        lerp_speed = min(1.0, dt * 20.0)
        self.cursor_x += (target_r.x - self.cursor_x) * lerp_speed
        self.cursor_y += (target_r.y - self.cursor_y) * lerp_speed
        self.cursor_w += (target_r.w - self.cursor_w) * lerp_speed
        self.cursor_h += (target_r.h - self.cursor_h) * lerp_speed

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if not input_data.pressed or self.is_closing:
            return

        if input_id in ("map", "back", "escape", "quit", "pause"):
            self._start_close()
            return

        # Arrow navigation between rooms
        if input_id in ("up", "move_up"):
            self._navigate_rooms((0, -1))
        elif input_id in ("down", "move_down"):
            self._navigate_rooms((0, 1))
        elif input_id in ("move_left",):
            self._navigate_rooms((-1, 0))
        elif input_id in ("move_right",):
            self._navigate_rooms((1, 0))

    def _navigate_rooms(self, direction: Tuple[int, int]) -> None:
        current_rect = self.ROOM_DEFINITIONS[self.inspected_room_key]["rect"]
        best_candidate: Optional[str] = None
        min_dist: float = 999999.0

        for key, data in self.ROOM_DEFINITIONS.items():
            if key == self.inspected_room_key:
                continue
            r = data["rect"]
            dx = r.centerx - current_rect.centerx
            dy = r.centery - current_rect.centery

            # Check if candidate is along direction vector
            if direction[0] > 0 and dx <= 10:
                continue
            if direction[0] < 0 and dx >= -10:
                continue
            if direction[1] > 0 and dy <= 10:
                continue
            if direction[1] < 0 and dy >= -10:
                continue

            dist = math.hypot(dx, dy)
            if dist < min_dist:
                min_dist = dist
                best_candidate = key

        if best_candidate:
            self.inspected_room_key = best_candidate
            settings.SOUNDS["change"].play()

    def render(self, surface: pygame.Surface) -> None:
        # Dynamic paper unfolding scale (open_progress is eased via out_back / in_back)
        scale_y = max(0.01, self.open_progress)

        # 1. Dark ambient background blur/overlay
        dim_alpha = int(min(1.0, self.open_progress) * 200)
        dark_dim = pygame.Surface(
            (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA
        )
        dark_dim.fill((10, 8, 14, dim_alpha))
        surface.blit(dark_dim, (0, 0))

        # 2. Paper Board Geometry with vertical unfold
        cur_w = self.PAGE_W
        cur_h = int(self.PAGE_H * scale_y)
        cx, cy = settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT // 2
        bx = cx - cur_w // 2
        by = cy - cur_h // 2

        # Drop shadow beneath paper
        shadow_rect = pygame.Rect(bx + 4, by + 5, cur_w, cur_h)
        shadow_alpha = int(min(1.0, self.open_progress) * 125)
        shadow_surf = pygame.Surface((cur_w, cur_h), pygame.SRCALPHA)
        shadow_surf.fill((15, 10, 18, shadow_alpha))
        surface.blit(shadow_surf, shadow_rect.topleft)

        # Parchment body (Humble Gift Warm Parchment #eebd8a)
        page_rect = pygame.Rect(bx, by, cur_w, cur_h)
        pygame.draw.rect(surface, (238, 189, 138), page_rect, border_radius=4)
        pygame.draw.rect(surface, (44, 30, 40), page_rect, 2, border_radius=4)

        # Corner diamonds (Humble Gift signature filigree)
        if cur_h > 30:
            self._draw_diamond(surface, page_rect.left + 5, page_rect.top + 5, 3)
            self._draw_diamond(surface, page_rect.right - 6, page_rect.top + 5, 3)
            self._draw_diamond(surface, page_rect.left + 5, page_rect.bottom - 6, 3)
            self._draw_diamond(surface, page_rect.right - 6, page_rect.bottom - 6, 3)

        # Only render inner content when unfolded enough
        if self.open_progress < 0.6:
            return

        # 3. Top Header: --o-- MAPA DEL MUNDO --o--
        header_y = 13
        render_text(
            surface,
            "--o-- MAPA DEL MUNDO --o--",
            settings.FONTS["hud"],
            settings.VIRTUAL_WIDTH // 2,
            header_y,
            (44, 30, 40),
            center=True,
        )

        # 4. Inner Map Viewport Frame (ps3Urw.gif style)
        v_rect = pygame.Rect(18, 22, 284, 98)
        pygame.draw.rect(surface, (246, 214, 172), v_rect)
        pygame.draw.rect(surface, (44, 30, 40), v_rect, 1)

        # Corner diamond accents inside viewport
        self._draw_diamond(surface, v_rect.left + 4, v_rect.top + 4, 2)
        self._draw_diamond(surface, v_rect.right - 5, v_rect.top + 4, 2)
        self._draw_diamond(surface, v_rect.left + 4, v_rect.bottom - 5, 2)
        self._draw_diamond(surface, v_rect.right - 5, v_rect.bottom - 5, 2)

        # 5. Render Walled Architectural Corridors between rooms
        for r_a, r_b, c_rect in self.CORRIDORS:
            visited_a = r_a in self.visited_rooms
            visited_b = r_b in self.visited_rooms
            if visited_a or visited_b:
                # Discovered corridor: warm chamber floor with thick stone walls
                pygame.draw.rect(surface, (242, 208, 166), c_rect)
                if c_rect.width > c_rect.height:
                    pygame.draw.line(surface, (44, 30, 40), (c_rect.left, c_rect.top), (c_rect.right, c_rect.top), 2)
                    pygame.draw.line(surface, (44, 30, 40), (c_rect.left, c_rect.bottom - 1), (c_rect.right, c_rect.bottom - 1), 2)
                else:
                    pygame.draw.line(surface, (44, 30, 40), (c_rect.left, c_rect.top), (c_rect.left, c_rect.bottom), 2)
                    pygame.draw.line(surface, (44, 30, 40), (c_rect.right - 1, c_rect.top), (c_rect.right - 1, c_rect.bottom), 2)
            else:
                # Faint dashed unexplored passage
                if c_rect.width > c_rect.height:
                    self._draw_dashed_line(surface, (195, 160, 125), (c_rect.left, c_rect.centery), (c_rect.right, c_rect.centery))
                else:
                    self._draw_dashed_line(surface, (195, 160, 125), (c_rect.centerx, c_rect.top), (c_rect.centerx, c_rect.bottom))


        # 6. Render Room Rectangles & POIs (Clean Cartographic Filigree Style)
        for room_key, data in self.ROOM_DEFINITIONS.items():
            r: pygame.Rect = data["rect"]
            is_visited: bool = room_key in self.visited_rooms
            is_current: bool = room_key == self.current_room_key

            if is_visited:
                # Explored Room: warm stone floor
                bg_col = (255, 246, 226) if is_current else (246, 228, 202)
                pygame.draw.rect(surface, bg_col, r)

                # Heavy outer stone wall outline (2px)
                pygame.draw.rect(surface, (44, 30, 40), r, 2)

                # Delicate gold inner bevel
                pygame.draw.rect(surface, (225, 195, 155), r.inflate(-4, -4), 1)

                # 4 Corner cartographic filigrees
                c_len = 3
                c_col = (195, 160, 115)
                # Top-left
                pygame.draw.line(surface, c_col, (r.left + 3, r.top + 3), (r.left + 3 + c_len, r.top + 3), 1)
                pygame.draw.line(surface, c_col, (r.left + 3, r.top + 3), (r.left + 3, r.top + 3 + c_len), 1)
                # Top-right
                pygame.draw.line(surface, c_col, (r.right - 4, r.top + 3), (r.right - 4 - c_len, r.top + 3), 1)
                pygame.draw.line(surface, c_col, (r.right - 4, r.top + 3), (r.right - 4, r.top + 3 + c_len), 1)
                # Bottom-left
                pygame.draw.line(surface, c_col, (r.left + 3, r.bottom - 4), (r.left + 3 + c_len, r.bottom - 4), 1)
                pygame.draw.line(surface, c_col, (r.left + 3, r.bottom - 4), (r.left + 3, r.bottom - 4 - c_len), 1)
                # Bottom-right
                pygame.draw.line(surface, c_col, (r.right - 4, r.bottom - 4), (r.right - 4 - c_len, r.bottom - 4), 1)
                pygame.draw.line(surface, c_col, (r.right - 4, r.bottom - 4), (r.right - 4, r.bottom - 4 - c_len), 1)

                # Bright gold highlight for current room
                if is_current:
                    pygame.draw.rect(surface, (235, 150, 40), r.inflate(-2, -2), 1)

                # Render POI Badge & Icon in center
                poi_type = data.get("poi")
                icon = self.icons.get(poi_type)
                if icon:
                    bx, by = r.centerx, r.centery - 2
                    # Embossed badge frame
                    pygame.draw.circle(surface, (44, 30, 40), (bx, by), 8)
                    pygame.draw.circle(surface, (248, 225, 192), (bx, by), 7)
                    surface.blit(icon, (bx - icon.get_width() // 2, by - icon.get_height() // 2))

                    # If boss or challenge is defeated, draw bold X stamp
                    event_req = data.get("event")
                    if event_req and event_req in self.cleared_events:
                        self._draw_defeat_x(surface, bx, by, 6)

                # Player Location Beacon (pulsing pin + expanding radar ripple)
                if is_current:
                    pin_cx = r.right - 5
                    pin_cy = r.top + 5
                    pulse = (math.sin(self.pulse_timer * 6.0) + 1.0) * 0.5
                    pin_radius = 2 + int(pulse * 1.5)

                    # Expanding radar ripple
                    ripple_phase = (self.pulse_timer * 1.8) % 1.0
                    ripple_r = 3 + int(ripple_phase * 9)
                    ripple_alpha = int((1.0 - ripple_phase) * 200)
                    ripple_surf = pygame.Surface((ripple_r * 2 + 2, ripple_r * 2 + 2), pygame.SRCALPHA)
                    pygame.draw.circle(ripple_surf, (240, 70, 70, ripple_alpha), (ripple_r + 1, ripple_r + 1), ripple_r, 1)
                    surface.blit(ripple_surf, (pin_cx - ripple_r - 1, pin_cy - ripple_r - 1))

                    # Center pin
                    pygame.draw.circle(surface, (44, 30, 40), (pin_cx, pin_cy), pin_radius + 1)
                    pygame.draw.circle(surface, (240, 60, 60), (pin_cx, pin_cy), pin_radius)

            else:
                # Unvisited Room: Living Diffuse / Animated Fog Shroud
                fog_surf = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
                fog_alpha = int(145 + math.sin(self.pulse_timer * 3.0 + r.x * 0.1) * 25)
                fog_surf.fill((65, 48, 55, fog_alpha))

                # Moving fog scanlines
                drift_offset = int(self.pulse_timer * 8) % 4
                for y_line in range(drift_offset, r.height, 4):
                    line_alpha = int(170 + math.cos(self.pulse_timer * 2.0 + y_line) * 30)
                    pygame.draw.line(fog_surf, (40, 28, 35, line_alpha), (0, y_line), (r.width, y_line))

                surface.blit(fog_surf, (r.x, r.y))
                pygame.draw.rect(surface, (140, 110, 95), r, 1)

                # Subtle floating '?'
                question_y = r.centery - 4 + int(math.sin(self.pulse_timer * 3.5 + r.x) * 1.2)
                render_text(
                    surface,
                    "?",
                    settings.FONTS["hud"],
                    r.centerx,
                    question_y,
                    (195, 165, 140),
                    center=True,
                )

        # 6.5 Render Smooth Gliding Cursor around Inspected Room
        cursor_draw_rect = pygame.Rect(
            int(self.cursor_x) - 3,
            int(self.cursor_y) - 3,
            int(self.cursor_w) + 6,
            int(self.cursor_h) + 6,
        )
        cursor_pulse = (math.sin(self.pulse_timer * 7.0) + 1.0) * 0.5
        c_col = (
            int(215 + cursor_pulse * 40),
            int(75 + cursor_pulse * 35),
            int(30),
        )
        pygame.draw.rect(surface, (44, 30, 40), cursor_draw_rect.inflate(2, 2), 1)
        pygame.draw.rect(surface, c_col, cursor_draw_rect, 2)
        for cx_pt, cy_pt in [cursor_draw_rect.topleft, cursor_draw_rect.topright, cursor_draw_rect.bottomleft, cursor_draw_rect.bottomright]:
            pts = [(cx_pt, cy_pt - 2), (cx_pt + 2, cy_pt), (cx_pt, cy_pt + 2), (cx_pt - 2, cy_pt)]
            pygame.draw.polygon(surface, c_col, pts)

        # 7. Bottom INFO Card (matching ps3Urw.gif)
        info_rect = pygame.Rect(18, 124, 284, 32)
        pygame.draw.rect(surface, (246, 214, 172), info_rect)
        pygame.draw.rect(surface, (44, 30, 40), info_rect, 1)

        # Icon box on left side of info card
        icon_box = pygame.Rect(22, 127, 26, 26)
        pygame.draw.rect(surface, (238, 189, 138), icon_box)
        pygame.draw.rect(surface, (44, 30, 40), icon_box, 1)

        # Draw icon in info box
        insp_data = self.ROOM_DEFINITIONS[self.inspected_room_key]
        insp_visited = self.inspected_room_key in self.visited_rooms

        if insp_visited:
            icon_name = insp_data.get("poi")
            icon_img = self.icons.get(icon_name)
            if icon_img:
                ix = icon_box.centerx - icon_img.get_width() // 2
                iy = icon_box.centery - icon_img.get_height() // 2
                surface.blit(icon_img, (ix, iy))
                event_req = insp_data.get("event")
                if event_req and event_req in self.cleared_events:
                    self._draw_defeat_x(surface, icon_box.centerx, icon_box.centery, 7)

            # Room title
            title_str = insp_data["name"]
            if self.inspected_room_key == self.current_room_key:
                title_str += "  [TU POSICION]"

            render_text(
                surface,
                title_str,
                settings.FONTS["hud"],
                54,
                124,
                (44, 30, 40),
            )

            # Description / Status
            event_req = insp_data.get("event")
            if event_req and event_req in self.cleared_events:
                desc_str = insp_data.get("desc_cleared", insp_data["desc"])
            else:
                desc_str = insp_data["desc"]

            render_text(
                surface,
                desc_str,
                settings.FONTS["hud"],
                54,
                136,
                (105, 75, 85),
            )
        else:
            # Unvisited Info
            render_text(
                surface,
                "?",
                settings.FONTS["title"],
                icon_box.centerx,
                icon_box.centery - 6,
                (110, 85, 95),
                center=True,
            )
            render_text(
                surface,
                "SALA INEXPLORADA",
                settings.FONTS["hud"],
                54,
                124,
                (95, 70, 80),
            )
            render_text(
                surface,
                "Niebla densa. Sector aun sin explorar.",
                settings.FONTS["hud_small"],
                54,
                136,
                (125, 95, 105),
            )

        # 8. Footer Controls & Statistics (Two-column layout)
        visited_count = len([k for k in self.ROOM_DEFINITIONS if k in self.visited_rooms])
        total_rooms = len(self.ROOM_DEFINITIONS)
        visited_pct = int((visited_count / float(total_rooms)) * 100)

        # Left: Controls
        render_text(
            surface,
            "[M/ESC] Cerrar  [FLECHAS] Explorar",
            settings.FONTS["hud_small"],
            22,
            155,
            (65, 45, 55),
        )

        # Right: Exploration Percentage & Progress Bar
        exp_text = f"Exploracion: {visited_pct}% ({visited_count}/{total_rooms})"
        exp_w = settings.FONTS["hud_small"].size(exp_text)[0]
        bar_w = 30
        bar_h = 4
        bar_x = 296 - bar_w
        bar_y = 160
        txt_x = bar_x - 6 - exp_w

        render_text(
            surface,
            exp_text,
            settings.FONTS["hud_small"],
            txt_x,
            155,
            (65, 45, 55),
        )

        pygame.draw.rect(surface, (205, 170, 130), (bar_x, bar_y, bar_w, bar_h), border_radius=2)
        fill_w = max(2, int(bar_w * (visited_count / float(total_rooms))))
        pygame.draw.rect(surface, (210, 85, 35), (bar_x, bar_y, fill_w, bar_h), border_radius=2)
        pygame.draw.rect(surface, (44, 30, 40), (bar_x, bar_y, bar_w, bar_h), 1, border_radius=2)

    def _draw_diamond(self, surf: pygame.Surface, cx: int, cy: int, r: int, col: Tuple[int, int, int] = (44, 30, 40)) -> None:
        pts = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
        pygame.draw.polygon(surf, col, pts)

    def _draw_defeat_x(self, surf: pygame.Surface, cx: int, cy: int, radius: int) -> None:
        """Draw bold red/crimson victory X over defeated boss/challenge."""
        col = (205, 35, 35)
        pygame.draw.line(surf, (40, 15, 15), (cx - radius, cy - radius), (cx + radius, cy + radius), 3)
        pygame.draw.line(surf, (40, 15, 15), (cx - radius, cy + radius), (cx + radius, cy - radius), 3)
        pygame.draw.line(surf, col, (cx - radius, cy - radius), (cx + radius, cy + radius), 2)
        pygame.draw.line(surf, col, (cx - radius, cy + radius), (cx + radius, cy - radius), 2)

    def _draw_dashed_line(self, surf: pygame.Surface, color: Tuple[int, int, int], pt_a: Tuple[int, int], pt_b: Tuple[int, int]) -> None:
        """Draw fine dashed corridor line."""
        dx = pt_b[0] - pt_a[0]
        dy = pt_b[1] - pt_a[1]
        dist = math.hypot(dx, dy)
        if dist == 0:
            return
        steps = int(dist // 4)
        for i in range(0, steps, 2):
            t1 = i / max(1, steps)
            t2 = min(1.0, (i + 1) / max(1, steps))
            p1 = (int(pt_a[0] + dx * t1), int(pt_a[1] + dy * t1))
            p2 = (int(pt_a[0] + dx * t2), int(pt_a[1] + dy * t2))
            pygame.draw.line(surf, color, p1, p2, 1)
