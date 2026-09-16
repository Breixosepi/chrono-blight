"""
Chrono Blight - Slot Selection Screen with New Game, Load Game, Overwrite, and Delete
"""
import time
import os
from typing import Any
import pygame
from gale.state import BaseState
from gale.save import SaveManager, SaveError
from gale.input_handler import InputData
from gale.text import render_text

import settings


class SlotSelectState(BaseState):
    def enter(self, **params: Any) -> None:
        self.mode = params.get("mode", "new") 
        self.selected_index = 0
        self.slots = settings.SAVE_SLOTS
        self.manager = SaveManager()
        self.confirming_overwrite = False
        self._refresh_metadata()

        self.card_w = 220
        self.card_h = 34
        self.card_gap = 8

        self.start_x = (settings.VIRTUAL_WIDTH - self.card_w) // 2
        total_h = len(self.slots) * self.card_h + (len(self.slots) - 1) * self.card_gap
        self.start_y = (settings.VIRTUAL_HEIGHT - total_h) // 2 + 10

    def _refresh_metadata(self) -> None:
        self.metadata = []
        for slot in self.slots:
            try:
                self.metadata.append(self.manager.read_metadata(slot))
            except SaveError:
                self.metadata.append(None)

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if not input_data.pressed:
            return

        if self.confirming_overwrite:
            if input_id in ("enter", "attack", "jump"):
                self._start_new_game_on_slot(self.slots[self.selected_index])
            elif input_id in ("quit", "back", "pause", "special"):
                self.confirming_overwrite = False
            return

        if input_id in ("up", "move_left"):
            self.selected_index = (self.selected_index - 1) % len(self.slots)
        elif input_id in ("down", "move_right"):
            self.selected_index = (self.selected_index + 1) % len(self.slots)
        elif input_id in ("enter", "attack", "jump"):
            self._handle_slot_selection()
        elif input_id == "special":
            self._delete_selected_slot()
        elif input_id in ("quit", "back", "pause"):
            from src.states.game.TitleState import TitleState
            self.state_machine.pop()
            title_state = TitleState(self.state_machine)
            self.state_machine.push(title_state)
            title_state.enter()

    def _handle_slot_selection(self) -> None:
        slot = self.slots[self.selected_index]
        meta = self.metadata[self.selected_index]

        if self.mode == "new":
            if meta is not None:
                self.confirming_overwrite = True
            else:
                self._start_new_game_on_slot(slot)
        elif self.mode == "load":
            if meta is not None:
                self._load_game_from_slot(slot)

    def _start_new_game_on_slot(self, slot: str) -> None:
        from src.states.game.PlayState import PlayState

        self.state_machine.pop()
        play_state = PlayState(self.state_machine)
        self.state_machine.push(play_state)

        params = {
            "slot": slot,
            "map_name": "middle",
            "spawn_point": (64.0, 208.0),
        }
        play_state.enter(**params)

    def _load_game_from_slot(self, slot: str) -> None:
        try:
            save_data = self.manager.load(slot)
        except SaveError:
            return

        from src.states.game.PlayState import PlayState

        self.state_machine.pop()
        play_state = PlayState(self.state_machine)
        self.state_machine.push(play_state)

        params = {
            "slot": slot,
            "map_name": save_data.get("room", "middle"),
            "spawn_point": (save_data.get("spawn_x", 64.0), save_data.get("spawn_y", 208.0)),
            "save_data": save_data,
        }
        play_state.enter(**params)

    def _delete_selected_slot(self) -> None:
        slot = self.slots[self.selected_index]
        save_path = settings.BASE_DIR / "saves" / f"{slot}.sav"
        if os.path.exists(save_path):
            try:
                os.remove(save_path)
            except OSError:
                pass
        self._refresh_metadata()

    def render(self, surface: pygame.Surface) -> None:
        surface.fill((16, 12, 24))

        title_text = "NUEVA PARTIDA" if self.mode == "new" else "CARGAR PARTIDA"
        render_text(
            surface,
            title_text,
            settings.FONTS["title"],
            settings.VIRTUAL_WIDTH // 2,
            16,
            (235, 190, 70),
            center=True,
            shadowed=True,
        )

        for i, slot in enumerate(self.slots):
            cy = self.start_y + i * (self.card_h + self.card_gap)
            meta = self.metadata[i]
            is_selected = (i == self.selected_index)

            card_rect = pygame.Rect(self.start_x, cy, self.card_w, self.card_h)
            
            bg_color = (36, 28, 48) if is_selected else (24, 18, 34)
            border_color = (255, 215, 80) if is_selected else (60, 50, 75)
            
            pygame.draw.rect(surface, bg_color, card_rect, border_radius=4)
            pygame.draw.rect(surface, border_color, card_rect, width=1, border_radius=4)

            if is_selected:
                render_text(
                    surface,
                    ">",
                    settings.FONTS["ui"],
                    self.start_x - 12,
                    cy + 8,
                    (255, 230, 90),
                    shadowed=True,
                )

            slot_label = f"RANURA {i + 1}"
            slot_title_color = (255, 240, 180) if is_selected else (170, 160, 180)
            render_text(
                surface,
                slot_label,
                settings.FONTS["hud"],
                self.start_x + 10,
                cy + 4,
                slot_title_color,
                shadowed=True,
            )

            if meta is None:
                status_text = "--- Vacío (Nueva Partida) ---" if self.mode == "new" else "--- Ranura Vacía ---"
                render_text(
                    surface,
                    status_text,
                    settings.FONTS["hud"],
                    self.start_x + 10,
                    cy + 17,
                    (110, 100, 125),
                )
            else:
                extra = getattr(meta, "extra", {}) or {}
                room_name = extra.get("room_name", "Sala").replace("_", " ").title()
                skin = extra.get("skin", "Mago").capitalize()
                hp = int(extra.get("health", 100))
                date_str = time.strftime("%d/%m %H:%M", time.localtime(meta.updated_at))

                details = f"{room_name} | {skin} | HP: {hp} | {date_str}"
                detail_color = (130, 230, 170) if is_selected else (110, 180, 140)
                render_text(
                    surface,
                    details,
                    settings.FONTS["hud"],
                    self.start_x + 10,
                    cy + 17,
                    detail_color,
                    shadowed=True,
                )

        if self.confirming_overwrite:
            overlay = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surface.blit(overlay, (0, 0))

            box_w, box_h = 240, 60
            box_x = (settings.VIRTUAL_WIDTH - box_w) // 2
            box_y = (settings.VIRTUAL_HEIGHT - box_h) // 2
            box_rect = pygame.Rect(box_x, box_y, box_w, box_h)
            pygame.draw.rect(surface, (40, 25, 30), box_rect, border_radius=5)
            pygame.draw.rect(surface, (255, 90, 90), box_rect, width=1, border_radius=5)

            render_text(
                surface,
                f"¿SOBRESCRIBIR RANURA {self.selected_index + 1}?",
                settings.FONTS["ui"],
                settings.VIRTUAL_WIDTH // 2,
                box_y + 10,
                (255, 120, 120),
                center=True,
                shadowed=True,
            )
            render_text(
                surface,
                "[ENTER/Z] Confirmar  [ESC] Cancelar",
                settings.FONTS["hud"],
                settings.VIRTUAL_WIDTH // 2,
                box_y + 36,
                (220, 220, 220),
                center=True,
                shadowed=True,
            )
        else:
            render_text(
                surface,
                "[ENTER/Z] Elegir  [X] Borrar  [ESC] Volver",
                settings.FONTS["hud"],
                settings.VIRTUAL_WIDTH // 2,
                settings.VIRTUAL_HEIGHT - 12,
                (140, 130, 155),
                center=True,
                shadowed=True,
            )
