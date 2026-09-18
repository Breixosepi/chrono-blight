"""
Chrono Blight - Story Intro State (Visual Novel Prologue)
"""
from typing import Any, List, Dict, Optional
import pygame
from gale.state import BaseState
from gale.input_handler import InputData
from gale.text import render_text
from gale.timer import Timer
from src.world.room_connections import DEFAULT_START_ROOM, DEFAULT_START_SPAWN
from src.states.game.PlayState import PlayState
import settings

class StoryIntroState(BaseState):
    STORY_SCENES: List[Dict[str, Any]] = [
        {
            "bg": "page_1",
            "speaker": "Cronista Ancestral",
            "phase": "past",
            "text": (
                "En el principio, el tiempo fluía en perfecta armonía, \n"
                "hasta que la plaga devoró nuestro cielo."
            ),
        },
        {
            "bg": "page_1",
            "speaker": "Cronista Ancestral",
            "phase": "past",
            "text": (
                "Emergió desde los confines del vacío.\n"
                "Una corrupción oscura conocida como el Chrono Blight."
            ),
        },
        {
            "bg": "page_2",
            "speaker": "Cronista Ancestral",
            "phase": "past",
            "text": (
                "En su desesperación, los eruditos forjaron el Gran Reloj\n"
                "para congelar la era y engañar a la muerte..."
            ),
        },
        {
            "bg": "page_3",
            "speaker": "Cronista Ancestral",
            "phase": "future",
            "text": (
                "Pero el tiempo no se domina. El núcleo colapsó,\n"
                "fracturando la realidad en dos mitades sangrantes:"
            ),
        },
        {
            "bg": "page_4",
            "speaker": "Cronista Ancestral",
            "phase": "future",
            "text": (
                "Un pasado suspendido en una gracia falsa,\n"
                "y un futuro ahogado en la putrefacción."
            ),
        },
        {
            "bg": "page_5",
            "speaker": "Cronista Ancestral",
            "phase": "future",
            "text": (
                "De la brecha nació The Harvester:\n"
                "un antiguo guardián enloquecido"
                
            ),
        },
        {
            "bg": "page_5",
            "speaker": "Cronista Ancestral",
            "phase": "future",
            "text": (
                "decidido a cosechar la energía temporal del mundo\n"
                "para gobernar un vacío atemporal absoluto."
            ),
        },
        {
            "bg": "page_6",
            "speaker": "Cronista Ancestral",
            "phase": "future",
            "text": (
                "Quienes juraron proteger el castillo fueron retorcidos por él\n"
                "y convertidos en monstruosos celadores de las ruinas" 
            ),
        },
        {
            "bg": "page_6",
            "speaker": "Cronista Ancestral",
            "phase": "past",
            "text": (
                "De las ruinas del tiempo, naciste tú.\n"
                "Un eco destinado a reparar este mundo..."
            ),
        },
        {
            "bg": "page_6",
            "speaker": "Cronista Ancestral",
            "phase": "past",
            "text": (
                "o a consumirlo por completo.\n"
            ),
        },
        {
            "bg": "page_6",
            "speaker": "Cronista Ancestral",
            "phase": "past",
            "text": (
                "Un espíritu te ha entregado parte de su esencia\n" 
                "(El mago de Fase). Uno de tres avatares de combate:"
            ),
        },
        {
            "bg": "page_6",
            "speaker": "Cronista Ancestral",
            "phase": "past",
            "text": (
                "el Mago de Fase, el Maestro de la Espada\n"
                "y la Bestia Primal."
            ),
        },
        {
            "bg": "page_7",
            "speaker": "Mago de Fase",
            "phase": "past",
            "text": (
                "Despierto en la Zona Central... débil.\n"
                "Tengo el don del Cambio de Fase para saltar entre épocas."
            ),
        },
        {
            "bg": "page_7",
            "speaker": "Mago de Fase",
            "phase": "past",
            "text": (
                "Debo recuperar las almas perdidas antes\n"
                "de que el tiempo colapse."
            ),
        },
        {
            "bg": "page_8",
            "speaker": "Voz Del Destino",
            "phase": "past",
            "text": (
                "Explora los abismos, derrota a los sacerdotes de la corrupción,\n"
                "y despierta al Espadachín y a la Bestia"
            ),
        },
        {
            "bg": "page_8",
            "speaker": "Voz Del Destino",
            "phase": "past",
            "text": (
                "que yacen cautivos en los santuarios."
            ),
        },
        {
            "bg": "page_8",
            "speaker": "Voz Del Destino",
            "phase": "past",
            "text": (
                "Solo la unión de tus tres formas podrá\n"
                "quebrar el velo de oscuridad."
            ),
        },
        {
            "bg": "page_9",
            "speaker": "Mago de Fase",
            "phase": "future",
            "text": (
                "The Harvester cree que el tiempo le pertenece...\n"
                "Es hora de demostrarle que el destino aún puede reescribirse."
            ),
        }, 
    ]

    def enter(self, slot: str, **params: Any) -> None:
        self.slot = slot
        self.current_scene_index = 0
        self.char_index = 0
        self.char_timer = 0.0
        self.char_speed = 0.022  
        self.text_complete = False

        self.prev_bg_key: Optional[str] = None
        self.current_bg_key: str = self.STORY_SCENES[0]["bg"]
        self.fade_alpha = 255.0 
        self.is_crossfading = False
        self.crossfade_progress = 1.0

        self.box_w = 308
        self.box_h = 48
        self.box_x = (settings.VIRTUAL_WIDTH - self.box_w) // 2
        self.box_y = settings.VIRTUAL_HEIGHT - self.box_h - 5

        self._fade_in_initial()

        if "phase_shift_past" in settings.SOUNDS:
            settings.SOUNDS["phase_shift_past"].play()

    def _fade_in_initial(self) -> None:
        self.fade_alpha = 255.0
        Timer.tween(
            0.35,
            [(self, {"fade_alpha": 0.0})],
        )

    def _current_scene(self) -> Dict[str, Any]:
        return self.STORY_SCENES[self.current_scene_index]

    def _finish_typing(self) -> None:
        scene = self._current_scene()
        self.char_index = len(scene["text"])
        self.text_complete = True

    def _advance_dialogue(self) -> None:
        if not self.text_complete:
            self._finish_typing()
            if "change" in settings.SOUNDS:
                settings.SOUNDS["change"].play()
        else:
            if self.current_scene_index < len(self.STORY_SCENES) - 1:
                self.prev_bg_key = self._current_scene()["bg"]
                self.current_scene_index += 1
                self.current_bg_key = self._current_scene()["bg"]

                self.char_index = 0
                self.char_timer = 0.0
                self.text_complete = False

                self.is_crossfading = True
                self.crossfade_progress = 0.0
                Timer.tween(
                    0.28,
                    [(self, {"crossfade_progress": 1.0})],
                    on_finish=lambda: setattr(self, "is_crossfading", False),
                )

                if "enter" in settings.SOUNDS:
                    settings.SOUNDS["enter"].play()

                curr = self._current_scene()
                if curr.get("phase") == "future" and "phase_shift_future" in settings.SOUNDS:
                    settings.SOUNDS["phase_shift_future"].play()
                elif curr.get("phase") == "past" and "phase_shift_past" in settings.SOUNDS:
                    settings.SOUNDS["phase_shift_past"].play()
            else:
                self._start_game()

    def _start_game(self) -> None:
        while len(self.state_machine.states) > 0:
            self.state_machine.pop()
        play_state = PlayState(self.state_machine)

        params = {
            "slot": self.slot,
            "map_name": DEFAULT_START_ROOM,
            "spawn_point": DEFAULT_START_SPAWN,
        }
        self.state_machine.push(play_state, **params)
        settings.stop_music("intro")

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if not input_data.pressed:
            return

        if input_id in ("enter", "jump", "attack"):
            self._advance_dialogue()
        elif input_id in ("quit", "back"):
            if "change" in settings.SOUNDS:
                settings.SOUNDS["change"].play()
            self._start_game()

    def update(self, dt: float) -> None:
        scene = self._current_scene()
        full_text = scene["text"]

        if not self.text_complete:
            self.char_timer += dt
            if self.char_timer >= self.char_speed:
                chars_to_add = int(self.char_timer / self.char_speed)
                self.char_timer %= self.char_speed
                prev_idx = self.char_index
                self.char_index = min(len(full_text), self.char_index + chars_to_add)

                if self.char_index > prev_idx:
                    curr_char = full_text[self.char_index - 1]
                    if curr_char not in (" ", "\n") and self.char_index % 3 == 0:
                        if "change" in settings.SOUNDS:
                            sfx = settings.SOUNDS["change"]
                            sfx.set_volume(0.18)
                            sfx.play()

                if self.char_index >= len(full_text):
                    self.text_complete = True
                    if "change" in settings.SOUNDS:
                        settings.SOUNDS["change"].set_volume(1.0)

    def render(self, surface: pygame.Surface) -> None:
        scene = self._current_scene()

        curr_tex = settings.TEXTURES.get(self.current_bg_key)
        prev_tex = settings.TEXTURES.get(self.prev_bg_key) if self.prev_bg_key else None

        if self.is_crossfading and prev_tex and curr_tex:
            surface.blit(prev_tex, (0, 0))
            temp_surf = curr_tex.copy()
            alpha_val = int(max(0.0, min(1.0, self.crossfade_progress)) * 255)
            temp_surf.set_alpha(alpha_val)
            surface.blit(temp_surf, (0, 0))
        elif curr_tex:
            surface.blit(curr_tex, (0, 0))
        else:
            surface.fill((16, 12, 24))

        phase_tint = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
        if scene.get("phase") == "future":
            phase_tint.fill((30, 10, 22, 60))
        else:
            phase_tint.fill((10, 24, 18, 55))
        surface.blit(phase_tint, (0, 0))

        box_rect = pygame.Rect(self.box_x, self.box_y, self.box_w, self.box_h)
        dialog_bg = pygame.Surface((self.box_w, self.box_h), pygame.SRCALPHA)
        dialog_bg.fill((12, 10, 18, 220))
        surface.blit(dialog_bg, (self.box_x, self.box_y))

        border_col = (195, 160, 95) if scene.get("phase") == "past" else (225, 95, 90)
        inner_border = (65, 50, 58)
        pygame.draw.rect(surface, inner_border, box_rect.inflate(2, 2), 1, border_radius=3)
        pygame.draw.rect(surface, border_col, box_rect, 1, border_radius=3)

        speaker = scene.get("speaker", "")
        spk_badge_w = settings.FONTS["hud"].size(speaker)[0] + 10
        spk_rect = pygame.Rect(self.box_x + 8, self.box_y - 12, spk_badge_w, 18)
        pygame.draw.rect(surface, (22, 18, 30), spk_rect, border_radius=2)
        pygame.draw.rect(surface, border_col, spk_rect, 1, border_radius=2)

        render_text(
            surface,
            speaker,
            settings.FONTS["hud"],
            spk_rect.centerx,
            spk_rect.centery - 3,
            border_col,
            center=True,
        )

        page_counter_str = f"{self.current_scene_index + 1} / {len(self.STORY_SCENES)}"
        counter_w = settings.FONTS["hud"].size(page_counter_str)[0] + 8
        counter_rect = pygame.Rect(self.box_x + self.box_w - counter_w - 6, self.box_y - 7, counter_w, 13)
        pygame.draw.rect(surface, (22, 18, 30), counter_rect, border_radius=2)
        pygame.draw.rect(surface, border_col, counter_rect, 1, border_radius=2)

        render_text(
            surface,
            page_counter_str,
            settings.FONTS["hud"],
            counter_rect.centerx,
            counter_rect.centery - 2,
            (210, 200, 190),
            center=True,
        )

        displayed_text = scene["text"][:self.char_index]
        tx = self.box_x + 10
        ty = self.box_y + 4
        render_text(
            surface,
            displayed_text,
            settings.FONTS["hud"],
            tx,
            ty,
            (240, 235, 225),
            shadowed=True,
        )

        foot_y = self.box_y + self.box_h - 16
        if self.text_complete:
            is_last = (self.current_scene_index == len(self.STORY_SCENES) - 1)
            prompt_str = "[ENTER] Comenzar" if is_last else "[ENTER] Continuar"
            blink = (int(pygame.time.get_ticks() / 320) % 2 == 0)
            p_col = (255, 230, 90) if blink else (180, 160, 80)
            render_text(
                surface,
                prompt_str,
                settings.FONTS["hud_small"],
                self.box_x + self.box_w - 75,
                foot_y,
                p_col,
                center=False,
            )
        else:
            render_text(
                surface,
                "[ENTER] Rápido",
                settings.FONTS["hud_small"],
                self.box_x + self.box_w - 75,
                foot_y,
                (130, 120, 140),
            )

        render_text(
            surface,
            "[ESC] Saltar Prólogo",
            settings.FONTS["hud_small"],
            settings.VIRTUAL_WIDTH - 6,
            5,
            (160, 145, 170),
            shadowed=True,
        )

        if self.fade_alpha > 0.5:
            fade_surf = pygame.Surface((settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT), pygame.SRCALPHA)
            fade_surf.fill((8, 6, 14, int(self.fade_alpha)))
            surface.blit(fade_surf, (0, 0))
