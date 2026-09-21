from typing import Any, Optional
import pygame
from gale.state import BaseState
from gale.input_handler import InputData, InputHandler
from gale.text import render_text

import settings
from src import controls_manager
from src.ui.MenuBackground import menu_background


class SettingsState(BaseState):
    CONFIG_ACTIONS = [
        "move_left",
        "move_right",
        "up",
        "down",
        "jump",
        "attack",
        "special",
        "dash",
        "phase_shift",
        "prev_form",
        "next_form",
        "map",
        "pause",
    ]

    def enter(self, from_pause: bool = False, **params: Any) -> None:
        self.from_pause = from_pause
        self.selected_index = 0
        self.rebinding_action: Optional[str] = None
        self._interceptor_installed: bool = False
        self.pulse_timer: float = 0.0
        self.status_message: str = ""
        self.status_timer: float = 0.0
        self.page_offset: int = 0
        self.visible_count: int = 7

        self.board_w = 276
        self.board_h = 176
        self.cx = settings.VIRTUAL_WIDTH // 2
        self.cy = settings.VIRTUAL_HEIGHT // 2
        self.bx = self.cx - self.board_w // 2
        self.by = self.cy - self.board_h // 2

        self._dim_overlay = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
        self._dim_overlay.fill((10, 8, 14, 200))

    def _setup_key_interceptor(self) -> None:
        if getattr(self, "_interceptor_installed", False):
            return
        self._interceptor_installed = True
        self._orig_handle_input = InputHandler.handle_input

        def _interceptor(event: pygame.event.Event) -> None:
            if self.rebinding_action is not None and event.type == pygame.KEYDOWN:
                key = event.key
                if key == pygame.K_ESCAPE:
                    self.rebinding_action = None
                    self.status_message = "Asignacion cancelada"
                    self.status_timer = 2.0
                    self._remove_key_interceptor()
                    if "close" in settings.SOUNDS:
                        settings.SOUNDS["close"].play()
                    return
                if key in controls_manager.SYSTEM_KEYBINDS.values():
                    self.rebinding_action = None
                    self.status_message = "!Tecla reservada!"
                    self.status_timer = 2.0
                    self._remove_key_interceptor()
                    if "close" in settings.SOUNDS:
                        settings.SOUNDS["close"].play()
                    return
                controls_manager.set_control(self.rebinding_action, key)
                self.rebinding_action = None
                self.status_message = "!Tecla guardada!"
                self.status_timer = 2.0
                self._remove_key_interceptor()
                if "save" in settings.SOUNDS:
                    settings.SOUNDS["save"].play()
                elif "enter" in settings.SOUNDS:
                    settings.SOUNDS["enter"].play()
                return
            self._orig_handle_input(event)

        InputHandler.handle_input = _interceptor

    def _remove_key_interceptor(self) -> None:
        if getattr(self, "_interceptor_installed", False):
            InputHandler.handle_input = self._orig_handle_input
            self._interceptor_installed = False

    def exit(self) -> None:
        self._remove_key_interceptor()

    def update(self, dt: float) -> None:
        self.pulse_timer += dt
        if not self.from_pause:
            menu_background.update(dt)
        if self.status_timer > 0.0:
            self.status_timer = max(0.0, self.status_timer - dt)
            if self.status_timer <= 0.0:
                self.status_message = ""

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if not input_data.pressed:
            return

        if self.rebinding_action is not None:
            return

        total_options = len(self.CONFIG_ACTIONS) + 2

        if input_id in ("up", "move_up"):
            self.selected_index = (self.selected_index - 1) % total_options
            if "change" in settings.SOUNDS:
                settings.SOUNDS["change"].play()
            self._adjust_scroll()
        elif input_id in ("down", "move_down"):
            self.selected_index = (self.selected_index + 1) % total_options
            if "change" in settings.SOUNDS:
                settings.SOUNDS["change"].play()
            self._adjust_scroll()
        elif input_id in ("enter", "jump", "attack"):
            self._handle_selection()
        elif input_id in ("back", "pause", "escape"):
            self._exit_state()

    def _adjust_scroll(self) -> None:
        if self.selected_index < len(self.CONFIG_ACTIONS):
            if self.selected_index < self.page_offset:
                self.page_offset = self.selected_index
            elif self.selected_index >= self.page_offset + self.visible_count:
                self.page_offset = self.selected_index - self.visible_count + 1
        elif self.selected_index == len(self.CONFIG_ACTIONS):
            self.page_offset = max(0, len(self.CONFIG_ACTIONS) - self.visible_count)

    def _handle_selection(self) -> None:
        if self.selected_index < len(self.CONFIG_ACTIONS):
            self.rebinding_action = self.CONFIG_ACTIONS[self.selected_index]
            self.status_message = "Presiona una tecla..."
            self.status_timer = 999.0
            self._setup_key_interceptor()
            if "enter" in settings.SOUNDS:
                settings.SOUNDS["enter"].play()
        elif self.selected_index == len(self.CONFIG_ACTIONS):
            controls_manager.reset_to_defaults()
            self.status_message = "Valores por defecto"
            self.status_timer = 2.0
            if "change-skin" in settings.SOUNDS:
                settings.SOUNDS["change-skin"].play()
        else:
            self._exit_state()

    def _exit_state(self) -> None:
        self._remove_key_interceptor()
        if "paper-fold" in settings.SOUNDS:
            settings.SOUNDS["paper-fold"].play()
        elif "close" in settings.SOUNDS:
            settings.SOUNDS["close"].play()
        self.state_machine.pop()

    def render(self, surface: pygame.Surface) -> None:
        if not self.from_pause:
            menu_background.render(surface)
        surface.blit(self._dim_overlay, (0, 0))

        board_rect = pygame.Rect(self.bx, self.by, self.board_w, self.board_h)
        shadow_rect = pygame.Rect(self.bx + 3, self.by + 4, self.board_w, self.board_h)

        shadow_surf = pygame.Surface((self.board_w, self.board_h), pygame.SRCALPHA)
        shadow_surf.fill((10, 8, 14, 130))
        surface.blit(shadow_surf, shadow_rect.topleft)

        pygame.draw.rect(surface, (238, 189, 138), board_rect, border_radius=4)
        pygame.draw.rect(surface, (44, 30, 40), board_rect, 2, border_radius=4)

        render_text(
            surface,
            "--o-- CONFIGURAR CONTROLES --o--",
            settings.FONTS["hud"],
            self.cx,
            self.by + 8,
            (44, 30, 40),
            center=True,
        )
        pygame.draw.line(surface, (180, 140, 105), (self.bx + 14, self.by + 19), (self.bx + self.board_w - 14, self.by + 19), 1)

        start_y = self.by + 23
        row_h = 15

        for i in range(self.visible_count):
            act_idx = self.page_offset + i
            if act_idx >= len(self.CONFIG_ACTIONS):
                break

            action_key = self.CONFIG_ACTIONS[act_idx]
            label = controls_manager.ACTION_LABELS.get(action_key, action_key)
            bound_code = controls_manager.CURRENT_KEYBINDS.get(action_key, 0)
            key_name = controls_manager.get_key_name(bound_code)

            is_selected = (self.selected_index == act_idx)
            is_waiting = (self.rebinding_action == action_key)

            row_y = start_y + (i * row_h)
            row_rect = pygame.Rect(self.bx + 8, row_y, self.board_w - 16, row_h)

            if is_waiting:
                pygame.draw.rect(surface, (255, 230, 160), row_rect, border_radius=2)
                pygame.draw.rect(surface, (210, 70, 30), row_rect, 1, border_radius=2)
                t_col = (210, 70, 30)
                val_text = "< PRESIONA TECLA >"
                val_col = (210, 70, 30)
            elif is_selected:
                pygame.draw.rect(surface, (255, 225, 175), row_rect, border_radius=2)
                pygame.draw.rect(surface, (195, 60, 30), row_rect, 1, border_radius=2)
                t_col = (195, 60, 30)
                val_text = f"[{key_name}]"
                val_col = (195, 60, 30)
            else:
                t_col = (55, 38, 50)
                val_text = f"[{key_name}]"
                val_col = (120, 50, 40)

            prefix = "> " if is_selected else "  "
            row_text_y = row_y - 2
            render_text(
                surface,
                f"{prefix}{label}",
                settings.FONTS["hud_small"],
                self.bx + 10,
                row_text_y,
                t_col,
            )

            text_w = settings.FONTS["hud_small"].size(val_text)[0]
            val_x = self.bx + self.board_w - 14 - text_w
            render_text(
                surface,
                val_text,
                settings.FONTS["hud_small"],
                val_x,
                row_text_y,
                val_col,
            )

        btn_y = self.by + self.board_h - 40
        btn_w, btn_h = 100, 16
        def_x = self.cx - btn_w - 6
        back_x = self.cx + 6

        def_idx = len(self.CONFIG_ACTIONS)
        is_def_sel = (self.selected_index == def_idx)
        def_rect = pygame.Rect(def_x, btn_y, btn_w, btn_h)
        if is_def_sel:
            pygame.draw.rect(surface, (255, 225, 175), def_rect, border_radius=3)
            pygame.draw.rect(surface, (195, 60, 30), def_rect, 1, border_radius=3)
            def_tcol = (195, 60, 30)
        else:
            pygame.draw.rect(surface, (244, 205, 160), def_rect, border_radius=3)
            pygame.draw.rect(surface, (185, 145, 110), def_rect, 1, border_radius=3)
            def_tcol = (55, 38, 50)

        render_text(
            surface,
            "POR DEFECTO",
            settings.FONTS["hud_small"],
            def_rect.centerx,
            def_rect.centery - 3,
            def_tcol,
            center=True,
        )

        back_idx = len(self.CONFIG_ACTIONS) + 1
        is_back_sel = (self.selected_index == back_idx)
        back_rect = pygame.Rect(back_x, btn_y, btn_w, btn_h)
        if is_back_sel:
            pygame.draw.rect(surface, (255, 225, 175), back_rect, border_radius=3)
            pygame.draw.rect(surface, (195, 60, 30), back_rect, 1, border_radius=3)
            back_tcol = (195, 60, 30)
        else:
            pygame.draw.rect(surface, (244, 205, 160), back_rect, border_radius=3)
            pygame.draw.rect(surface, (185, 145, 110), back_rect, 1, border_radius=3)
            back_tcol = (55, 38, 50)

        render_text(
            surface,
            "VOLVER",
            settings.FONTS["hud_small"],
            back_rect.centerx,
            back_rect.centery - 3,
            back_tcol,
            center=True,
        )

        foot_y = self.by + self.board_h - 11
        if self.status_message:
            render_text(
                surface,
                self.status_message,
                settings.FONTS["hud_small"],
                self.cx,
                foot_y - 3,
                (195, 60, 30),
                center=True,
            )
        else:
            render_text(
                surface,
                "[ENTER] Cambiar tecla   [ESC/BACK] Salir",
                settings.FONTS["hud_small"],
                self.cx,
                foot_y - 3,
                (115, 85, 95),
                center=True,
            )
