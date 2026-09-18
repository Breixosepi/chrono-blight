"""
Chrono Blight - Animated Pause State (Humble Gift Paper UI System v1.1)
"""
from typing import Any, Optional, List, Dict
import math
import pygame
from gale.state import BaseState
from gale.input_handler import InputData
from gale.timer import Timer
from gale.text import render_text
from src.states.game.MapState import MapState

import settings


class PauseState(BaseState):
    """
    Modern animated Pause menu featuring Paper UI System v1.1 aesthetic:
      - Smooth vertical unfold animation with ease_out_back on enter.
      - Smooth vertical fold animation with ease_in_back on exit.
      - Tactile paper drop shadow.
      - Smooth interpolated cursor indicator (lerp).
      - Interactive sub-panel for 'CONTROLES Y FORMAS'.
      - Direct shortcut to open World Map.
    """

    MENU_OPTIONS: List[Dict[str, str]] = [
        {"id": "resume", "label": "REANUDAR"},
        {"id": "map", "label": "MAPA DEL MUNDO"},
        {"id": "controls", "label": "CONTROLES Y FORMAS"},
        {"id": "title", "label": "MENU PRINCIPAL"},
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

        self.selected_index: int = 0
        self.cursor_visual_y: float = 0.0
        self.pulse_timer: float = 0.0

        # Animation & subscreen states
        self.open_progress: float = 0.0
        self.is_closing: bool = False
        self.showing_controls: bool = False
        self.showing_quit_confirm: bool = False
        self.confirm_quit_index: int = 0  # 0: Cancelar, 1: Salir

        # Dimensions of the main pause paper board
        self.BOARD_W: int = 264
        self.BOARD_H: int = 152

        # Trigger unfold animation
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
            0.15,
            [(self, {"open_progress": 0.0})],
            ease_function_name="in_back",
            on_finish=cb,
        )

    def update(self, dt: float) -> None:
        self.pulse_timer += dt

        # Smooth cursor interpolation
        target_y = float(self.selected_index * 22)
        self.cursor_visual_y += (target_y - self.cursor_visual_y) * min(1.0, dt * 20.0)

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if not input_data.pressed or self.is_closing:
            return

        # If quit confirmation modal is open
        if self.showing_quit_confirm:
            if input_id in ("back", "escape"):
                self.showing_quit_confirm = False
                return
            if input_id in ("move_left", "move_right", "left", "right", "up", "down", "move_up", "move_down"):
                self.confirm_quit_index = 1 - self.confirm_quit_index
                settings.SOUNDS["change"].play()
            elif input_id in ("enter", "jump", "attack"):
                settings.SOUNDS["enter"].play()
                if self.confirm_quit_index == 0:
                    # Cancel
                    self.showing_quit_confirm = False
                else:
                    # Quit to title
                    def go_to_title():
                        settings.stop_all_music()
                        from src.states.game.TitleState import TitleState
                        while len(self.state_machine.states) > 0:
                            self.state_machine.pop()
                        self.state_machine.push(TitleState(self.state_machine))

                    self._start_close(on_finish_callback=go_to_title)
            return

        # If inspecting controls sub-screen
        if self.showing_controls:
            if input_id in ("back", "escape", "enter", "pause", "jump", "attack"):
                self.showing_controls = False
            return

        # Regular pause navigation
        if input_id in ("pause", "escape", "back"):
            self._start_close()
            return

        if input_id in ("up", "move_up"):
            self.selected_index = (self.selected_index - 1) % len(self.MENU_OPTIONS)
            settings.SOUNDS["change"].play()
        elif input_id in ("down", "move_down"):
            self.selected_index = (self.selected_index + 1) % len(self.MENU_OPTIONS)
            settings.SOUNDS["change"].play()
        elif input_id in ("enter", "jump", "attack"):
            settings.SOUNDS["enter"].play()
            self._select_option()

    def _select_option(self) -> None:
        chosen = self.MENU_OPTIONS[self.selected_index]["id"]
        if chosen == "resume":
            self._start_close()
        elif chosen == "map":
            # Close pause and open MapState
            def open_map():
                self.state_machine.pop()
                self.state_machine.push(MapState(self.state_machine), play_state=self.play_state)

            self._start_close(on_finish_callback=open_map)
        elif chosen == "controls":
            self.showing_controls = True
        elif chosen == "title":
            # Prompt confirmation before abandoning unsaved progress
            self.showing_quit_confirm = True
            self.confirm_quit_index = 0

    def render(self, surface: pygame.Surface) -> None:
        # Calculate dynamic animation scale (open_progress is eased via out_back / in_back)
        scale_y = max(0.01, self.open_progress)

        # 1. Dark background overlay
        dim_alpha = int(min(1.0, self.open_progress) * 190)
        overlay = pygame.Surface(
            (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA
        )
        overlay.fill((10, 8, 14, dim_alpha))
        surface.blit(overlay, (0, 0))

        # 2. Paper Board Geometry
        cur_h = int(self.BOARD_H * scale_y)
        cur_w = self.BOARD_W
        cx, cy = settings.VIRTUAL_WIDTH // 2, settings.VIRTUAL_HEIGHT // 2
        bx = cx - cur_w // 2
        by = cy - cur_h // 2

        # Drop shadow beneath paper
        shadow_rect = pygame.Rect(bx + 4, by + 5, cur_w, cur_h)
        shadow_alpha = int(min(1.0, self.open_progress) * 120)
        shadow_surf = pygame.Surface((cur_w, cur_h), pygame.SRCALPHA)
        shadow_surf.fill((15, 10, 18, shadow_alpha))
        surface.blit(shadow_surf, shadow_rect.topleft)

        # Parchment body (Humble Gift #eebd8a)
        board_rect = pygame.Rect(bx, by, cur_w, cur_h)
        pygame.draw.rect(surface, (238, 189, 138), board_rect, border_radius=4)
        pygame.draw.rect(surface, (44, 30, 40), board_rect, 2, border_radius=4)

        # Corner diamond filigrees
        if cur_h > 30:
            self._draw_diamond(surface, bx + 6, by + 6, 3)
            self._draw_diamond(surface, bx + cur_w - 7, by + 6, 3)
            self._draw_diamond(surface, bx + 6, by + cur_h - 7, 3)
            self._draw_diamond(surface, bx + cur_w - 7, by + cur_h - 7, 3)

        # Only render inner content when unfolded enough
        if self.open_progress < 0.6:
            return

        if self.showing_controls:
            self._render_controls_view(surface, bx, by, cur_w, cur_h)
        else:
            self._render_main_pause_view(surface, bx, by, cur_w, cur_h)

        if self.showing_quit_confirm:
            self._render_quit_confirm_modal(surface)

    def _render_main_pause_view(self, surface: pygame.Surface, bx: int, by: int, bw: int, bh: int) -> None:
        cx = settings.VIRTUAL_WIDTH // 2

        # Decorative Header Banner
        header_y = by + 12
        render_text(
            surface,
            "--o-- PAUSA --o--",
            settings.FONTS["ui"],
            cx,
            header_y,
            (44, 30, 40),
            center=True,
        )

        # Subtle divider line
        pygame.draw.line(surface, (180, 140, 105), (bx + 16, by + 25), (bx + bw - 16, by + 25), 1)

        # Button Options
        start_y = by + 33
        btn_w, btn_h = 160, 20
        btn_x = cx - btn_w // 2

        for i, opt in enumerate(self.MENU_OPTIONS):
            oy = start_y + (i * 24)
            btn_rect = pygame.Rect(btn_x, oy, btn_w, btn_h)
            is_selected = (i == self.selected_index)

            if is_selected:
                # Highlighted button card with gentle pulse
                pulse = (math.sin(self.pulse_timer * 6.0) + 1.0) * 0.5
                bg_col = (255, 225, 175)
                border_col = (195, 60, 30)
                pygame.draw.rect(surface, bg_col, btn_rect, border_radius=3)
                pygame.draw.rect(surface, border_col, btn_rect, 1, border_radius=3)

                # Smooth cursor pointer
                arrow_x = btn_x - 10 + int(pulse * 2)
                render_text(
                    surface,
                    ">",
                    settings.FONTS["hud"],
                    arrow_x,
                    oy,
                    (195, 60, 30),
                )
                text_col = (195, 60, 30)
            else:
                # Normal button card
                pygame.draw.rect(surface, (244, 205, 160), btn_rect, border_radius=3)
                pygame.draw.rect(surface, (185, 145, 110), btn_rect, 1, border_radius=3)
                text_col = (55, 38, 50)

            render_text(
                surface,
                opt["label"],
                settings.FONTS["hud"],
                cx,
                oy + 8,
                text_col,
                center=True,
            )

        # Footer instruction
        render_text(
            surface,
            "[P/ESC] Reanudar   [ENTER] Seleccionar",
            settings.FONTS["hud"],
            cx,
            by + bh - 14,
            (115, 85, 95),
            center=True,
        )

    def _render_controls_view(self, surface: pygame.Surface, bx: int, by: int, bw: int, bh: int) -> None:
        cx = settings.VIRTUAL_WIDTH // 2

        # Header
        render_text(
            surface,
            "--o-- CONTROLES Y FORMAS --o--",
            settings.FONTS["hud"],
            cx,
            by + 10,
            (44, 30, 40),
            center=True,
        )
        pygame.draw.line(surface, (180, 140, 105), (bx + 14, by + 22), (bx + bw - 14, by + 22), 1)

        # Lines of controls
        lines = [
            ("[FLECHAS / A-D]", "Moverse e interactuar"),
            ("[ESPACIO]", "Saltar"),
            ("[Z] ATACAR", "Mag: Orbe | Swd: Espada | Mor: Garra"),
            ("[X] ESPECIAL", "Mag: Fuego | Swd: Dash | Mor: Dash"),
            ("[Q] / [E]", "Alternar Formas desbloqueadas"),
            ("[F]", "Cambio de Fase (Pasado / Futuro)"),
            ("[M]", "Mapa del Mundo"),
        ]

        sy = by + 28
        for key_str, desc_str in lines:
            render_text(surface, key_str, settings.FONTS["hud_small"], bx + 12, sy, (190, 60, 30))
            render_text(surface, desc_str, settings.FONTS["hud_small"], bx + 84, sy, (55, 40, 50))
            sy += 15

        render_text(
            surface,
            "[ESC o ENTER] Volver a la Pausa",
            settings.FONTS["hud"],
            cx,
            by + bh - 12,
            (115, 85, 95),
            center=True,
        )

    def _render_quit_confirm_modal(self, surface: pygame.Surface) -> None:
        cx = settings.VIRTUAL_WIDTH // 2
        cy = settings.VIRTUAL_HEIGHT // 2

        # Dim dark overlay
        dim = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
        dim.fill((10, 8, 14, 150))
        surface.blit(dim, (0, 0))

        # Modal dialog card
        mw, mh = 206, 92
        mx = cx - mw // 2
        my = cy - mh // 2

        # Drop shadow
        m_shadow = pygame.Surface((mw, mh), pygame.SRCALPHA)
        m_shadow.fill((15, 10, 18, 140))
        surface.blit(m_shadow, (mx + 3, my + 4))

        # Parchment background
        modal_rect = pygame.Rect(mx, my, mw, mh)
        pygame.draw.rect(surface, (244, 205, 160), modal_rect, border_radius=4)
        pygame.draw.rect(surface, (44, 30, 40), modal_rect, 2, border_radius=4)

        # Corner diamond accents
        self._draw_diamond(surface, mx + 5, my + 5, 2)
        self._draw_diamond(surface, mx + mw - 6, my + 5, 2)
        self._draw_diamond(surface, mx + 5, my + mh - 6, 2)
        self._draw_diamond(surface, mx + mw - 6, my + mh - 6, 2)

        # Title
        render_text(
            surface,
            "--o-- ATENCION --o--",
            settings.FONTS["hud"],
            cx,
            my + 8,
            (190, 50, 30),
            center=True,
        )

        render_text(
            surface,
            "¿Volver al Menu Principal?",
            settings.FONTS["hud"],
            cx,
            my + 23,
            (44, 30, 40),
            center=True,
        )

        render_text(
            surface,
            "El progreso no guardado se perdera.",
            settings.FONTS["hud"],
            cx,
            my + 36,
            (140, 50, 40),
            center=True,
        )

        # Buttons: [ CANCELAR ]   [ SALIR ]
        btn_w, btn_h = 76, 20
        btn_y = my + 52
        btn1_x = cx - btn_w - 6
        btn2_x = cx + 6

        buttons = [
            (btn1_x, "CANCELAR", 0),
            (btn2_x, "SALIR", 1),
        ]

        for bx_pos, label, idx in buttons:
            b_rect = pygame.Rect(bx_pos, btn_y, btn_w, btn_h)
            is_sel = (self.confirm_quit_index == idx)
            if is_sel:
                pygame.draw.rect(surface, (255, 238, 205), b_rect, border_radius=3)
                pygame.draw.rect(surface, (195, 60, 30), b_rect, 2, border_radius=3)
                t_col = (195, 60, 30)
            else:
                pygame.draw.rect(surface, (230, 185, 140), b_rect, border_radius=3)
                pygame.draw.rect(surface, (160, 120, 85), b_rect, 1, border_radius=3)
                t_col = (60, 40, 50)

            render_text(
                surface,
                label,
                settings.FONTS["hud"],
                b_rect.centerx,
                b_rect.centery - 4,
                t_col,
                center=True,
            )

        render_text(
            surface,
            "[FLECHAS] Elegir   [ENTER] Aceptar",
            settings.FONTS["hud"],
            cx,
            my + mh - 11,
            (100, 75, 85),
            center=True,
        )

    def _draw_diamond(self, surf: pygame.Surface, cx: int, cy: int, r: int, col: tuple = (44, 30, 40)) -> None:
        pts = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
        pygame.draw.polygon(surf, col, pts)