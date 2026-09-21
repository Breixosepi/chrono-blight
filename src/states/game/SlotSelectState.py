"""
Chrono Blight - Slot Selection Screen with New Game, Load Game, Overwrite, and Delete
"""
import time
from typing import Any
import pygame
from gale.state import BaseState
from gale.save import SaveManager, SaveError
from gale.input_handler import InputData
from gale.text import render_text

import settings
from src.world.room_connections import DEFAULT_START_ROOM, DEFAULT_START_SPAWN
from src.ui.MenuBackground import menu_background

ROOM_DISPLAY_NAMES = {
    "middle": "Zona Central",
    "left_corner": "Abismo Oeste",
    "sala_future": "Santuario Futuro",
    "abismo_fixed": "Abismo Este",
    "sala_past": "Santuario Pasado",
    "esquina_1": "Santuario Noreste",
    "subida": "Subida al Abismo",
    "big_room": "Gran Pirámide",
}


class SlotSelectState(BaseState):
    def enter(self, **params: Any) -> None:
        self.mode = params.get("mode", "new")
        self.from_game_over = params.get("from_game_over", False)
        self.selected_index = 0
        self.slots = settings.SAVE_SLOTS
        self.manager = SaveManager()
        self.confirming_overwrite = False
        self._refresh_metadata()

        self.card_w = 236
        self.card_h = 34
        self.card_gap = 8

        self.start_x = (settings.VIRTUAL_WIDTH - self.card_w) // 2
        total_h = len(self.slots) * self.card_h + (len(self.slots) - 1) * self.card_gap
        self.start_y = (settings.VIRTUAL_HEIGHT - total_h) // 2 + 10

        self._dim_overlay = pygame.Surface(
            (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA
        )
        self._dim_overlay.fill((0, 0, 0, 180))

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
            if input_id in ("enter", "jump", "attack"):
                settings.SOUNDS["enter"].play()
                self._start_new_game_on_slot(self.slots[self.selected_index])
            elif input_id in ("back", "pause"):
                self.confirming_overwrite = False
            return

        if input_id in ("up"):
            self.selected_index = (self.selected_index - 1) % len(self.slots)
            settings.SOUNDS["change"].play()
        elif input_id in ("down"):
            self.selected_index = (self.selected_index + 1) % len(self.slots)
            settings.SOUNDS["change"].play()
        elif input_id in ("enter", "jump", "attack"):
            settings.SOUNDS["enter"].play()
            self._handle_slot_selection()
        elif input_id == "special":
            self._delete_selected_slot()
        elif input_id in ("back", "pause"):
            if self.from_game_over:
                self.state_machine.pop()
            else:
                from src.states.game.TitleState import TitleState
                self.state_machine.pop()
                self.state_machine.push(TitleState(self.state_machine))

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
        from src.states.game.StoryIntroState import StoryIntroState

        while len(self.state_machine.states) > 0:
            self.state_machine.pop()
        story_state = StoryIntroState(self.state_machine)
        self.state_machine.push(story_state, slot=slot)

    def _load_game_from_slot(self, slot: str) -> None:
        try:
            save_data = self.manager.load(slot)
        except SaveError:
            return

        from src.states.game.PlayState import PlayState

        while len(self.state_machine.states) > 0:
            self.state_machine.pop()
        play_state = PlayState(self.state_machine)

        room_name = save_data.get("room", DEFAULT_START_ROOM)
        spawn_x = save_data.get("spawn_x", DEFAULT_START_SPAWN[0])
        spawn_y = save_data.get("spawn_y", DEFAULT_START_SPAWN[1])
        if "big_room" in room_name or "b_r" in room_name:
            room_name = "middle"
            spawn_x, spawn_y = 240.0, 48.0
            cleared_ev = set(save_data.get("cleared_events", []))
            cleared_ev.discard("the_harvester_defeated")
            save_data["cleared_events"] = list(cleared_ev)
            save_data["room"] = room_name
            save_data["spawn_x"] = spawn_x
            save_data["spawn_y"] = spawn_y

        params = {
            "slot": slot,
            "map_name": room_name,
            "spawn_point": (spawn_x, spawn_y),
            "save_data": save_data,
        }
        self.state_machine.push(play_state, **params)

    def _delete_selected_slot(self) -> None:
        slot = self.slots[self.selected_index]
        save_path = settings.BASE_DIR / "saves" / f"{slot}.sav"
        save_path.unlink(missing_ok=True)
        self._refresh_metadata()

    def update(self, dt: float) -> None:
        menu_background.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        menu_background.render(surface)

        title_text = "Nueva Partida" if self.mode == "new" else "Cargar Partida"
        render_text(
            surface,
            title_text,
            settings.FONTS["title_1"],
            settings.VIRTUAL_WIDTH // 2,
            20,
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
                    settings.FONTS["hud_small"],
                    self.start_x + 10,
                    cy + 17,
                    (110, 100, 125),
                )
            else:
                extra = getattr(meta, "extra", {}) or {}
                if "metadata" in extra and isinstance(extra["metadata"], dict):
                    extra = {**extra["metadata"], **extra}

                raw_room = extra.get("room_name") or extra.get("room", "middle")
                if "big_room" in raw_room or "b_r" in raw_room:
                    raw_room = "middle"
                room_display = ROOM_DISPLAY_NAMES.get(raw_room, raw_room.replace("_", " ").title())

                exploration = extra.get("exploration")
                playtime_sec = extra.get("playtime")
                forms_count = extra.get("forms_count")

                if exploration is None or playtime_sec is None or forms_count is None:
                    try:
                        data = self.manager.load(self.slots[i])
                        if data:
                            if exploration is None:
                                visited = data.get("visited_rooms", [])
                                exploration = data.get("exploration", min(100, int((len(visited) / 8.0) * 100)) if visited else 0)
                            if playtime_sec is None:
                                playtime_sec = data.get("playtime", 0)
                            if forms_count is None:
                                cleared = set(data.get("cleared_events", []))
                                f_count = 1
                                if "survival_boss_defeated" in cleared:
                                    f_count += 1
                                if "subida_cleared" in cleared:
                                    f_count += 1
                                forms_count = data.get("forms_count", f_count)
                    except Exception:
                        pass

                exploration = int(exploration if exploration is not None else 0)
                playtime_sec = int(playtime_sec if playtime_sec is not None else 0)
                forms_count = int(forms_count if forms_count is not None else 1)

                hours = playtime_sec // 3600
                mins = (playtime_sec % 3600) // 60
                secs = playtime_sec % 60
                if hours > 0:
                    time_str = f"{hours}h {mins:02d}m"
                else:
                    time_str = f"{mins:02d}m {secs:02d}s"

                exp_text = f"Explorado: {exploration}%"
                exp_w = settings.FONTS["hud_small"].size(exp_text)[0]
                render_text(
                    surface,
                    exp_text,
                    settings.FONTS["hud_small"],
                    self.start_x + self.card_w - 10 - exp_w,
                    cy + 5,
                    (130, 230, 170) if is_selected else (100, 180, 130),
                    shadowed=True,
                )

                details = f"{room_display} | Formas: {forms_count}/3 | {time_str}"
                detail_color = (220, 215, 230) if is_selected else (160, 150, 170)
                render_text(
                    surface,
                    details,
                    settings.FONTS["hud_small"],
                    self.start_x + 10,
                    cy + 18,
                    detail_color,
                    shadowed=True,
                )

        if self.confirming_overwrite:
            surface.blit(self._dim_overlay, (0, 0))

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
                "[ENTER] Confirmar  [P] Cancelar",
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
                "[ENTER] Elegir  [X] Borrar  [P] Volver",
                settings.FONTS["hud"],
                settings.VIRTUAL_WIDTH // 2,
                settings.VIRTUAL_HEIGHT - 12,
                (140, 130, 155),
                center=True,
                shadowed=True,
            )