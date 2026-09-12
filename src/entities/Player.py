"""
Chrono Blight
"""

from typing import Any, Optional, Dict, List
import pygame
from gale.animation import Animation
from gale.state import StateMachine
from gale.command import CommandBindings
from gale.input_handler import InputData

import settings
from src.definitions import entity as entity_defs
from src.entities.Entity import Entity
from src import commands
from src.states.entity.player.IdleState import IdleState
from src.states.entity.player.WalkState import WalkState
from src.states.entity.player.JumpState import JumpState
from src.states.entity.player.FallState import FallState
from src.states.entity.player.DashState import DashState
from src.states.entity.player.AttackState import AttackState
from src.states.entity.player.AttackSpecialState import AttackSpecialState
from src.states.entity.player.HitState import HitState
from src.states.entity.player.DeathState import DeathState


def _build_animations() -> dict[str, dict[str, Animation]]:
    result: dict[str, dict[str, Animation]] = {}
    player_anim_defs = entity_defs.ENTITY_DEFS["animations"]["player"]

    for skin, anim_dict in player_anim_defs.items():
        for color in ("red", "green"):
            texture_key = f"{skin}_{color}"
            frame_rects = settings.FRAMES[texture_key]

            state_animations: dict[str, Animation] = {}
            for state_name, anim_data in anim_dict.items():
                rects = [frame_rects[i] for i in anim_data["frames"]]
                state_animations[state_name] = Animation(
                    rects,
                    anim_data["interval"],
                    loops=anim_data.get("loops"),
                )

            result[texture_key] = state_animations

    return result


class Player(Entity):

    def __init__(
        self,
        x: float,
        y: float,
        floor_y: float = 160.0,
        map_w: float = 1248.0,
    ) -> None:
        super().__init__(
            x,
            y,
            width=entity_defs.PLAYER_HIT_W,
            height=entity_defs.PLAYER_HIT_H,
            floor_y=floor_y,
            map_w=map_w,
        )

        self.skin: str = "mage"
        self.phase_color: str = "red"
        self.available_skins: list[str] = ["mage", "morph", "sword"]

        self.form_stats: dict[str, dict[str, float]] = {}
        for form_key, form_data in entity_defs.ENTITY_DEFS["player"]["forms"].items():
            max_hp = float(form_data["stats"]["max_health"])
            max_mp = float(form_data["stats"]["max_mana"])
            self.form_stats[form_key] = {
                "health": max_hp,
                "max_health": max_hp,
                "mana": max_mp,
                "max_mana": max_mp,
                "mana_regen": float(form_data["stats"]["mana_regen"]),
                "jumps": int(form_data["stats"]["jumps"]),
            }

        self.jumps_left: int = self.form_stats[self.skin]["jumps"]

        self.animations: dict[str, dict[str, Animation]] = _build_animations()
        self.current_animation: Animation = self.animations["mage_red"]["idle"]

        self.command_bindings = CommandBindings()
        self.command_bindings.bind("move_left", press=commands.MOVE_LEFT, release=commands.STOP_MOVE_LEFT)
        self.command_bindings.bind("move_right", press=commands.MOVE_RIGHT, release=commands.STOP_MOVE_RIGHT)
        self.command_bindings.bind("up", press=commands.MOVE_UP, release=commands.STOP_MOVE_UP)
        self.command_bindings.bind("jump", press=commands.JUMP, release=commands.STOP_JUMP)
        self.command_bindings.bind("run", press=commands.RUN, release=commands.STOP_RUN)
        self.command_bindings.bind("attack", press=commands.ATTACK)
        self.command_bindings.bind("special", press=commands.ATTACK_SPECIAL)
        self.command_bindings.bind("dash", press=commands.DASH)

        self.phase_cooldown_max: float = 2.0
        self.phase_cooldown_timer: float = 0.0

        self.skin_cooldown_max: float = 5.0
        self.skin_cooldown_timer: float = 0.0

        self.area_circle_idx: int = 0
        self.area_subframe: int = 0
        self.area_active: bool = False
        self.area_pos_x: float = 0.0
        self.area_pos_y: float = 0.0
        self.flames: list[dict] = []

        self.state_machine = StateMachine({
            "idle": lambda sm: IdleState(self, sm),
            "walk": lambda sm: WalkState(self, sm),
            "jump": lambda sm: JumpState(self, sm),
            "fall": lambda sm: FallState(self, sm),
            "airborne": lambda sm: FallState(self, sm),
            "dash": lambda sm: DashState(self, sm),
            "attack": lambda sm: AttackState(self, sm),
            "attack_special": lambda sm: AttackSpecialState(self, sm),
            "hit": lambda sm: HitState(self, sm),
            "death": lambda sm: DeathState(self, sm),
        })
        self.change_state("idle")

    @property
    def health(self) -> float:
        return self.form_stats[self.skin]["health"]

    @health.setter
    def health(self, val: float) -> None:
        self.form_stats[self.skin]["health"] = val

    @property
    def MAX_HEALTH(self) -> float:
        return self.form_stats[self.skin]["max_health"]

    @property
    def mana(self) -> float:
        return self.form_stats[self.skin]["mana"]

    @mana.setter
    def mana(self, val: float) -> None:
        self.form_stats[self.skin]["mana"] = val

    @property
    def MAX_MANA(self) -> float:
        return self.form_stats[self.skin]["max_mana"]

    def on_land(self) -> None:
        """Reinicia los saltos disponibles según la forma activa al tocar el suelo."""
        super().on_land()
        self.jumps_left = self.form_stats[self.skin]["jumps"]

    def get_form_data(self) -> dict:
        return entity_defs.ENTITY_DEFS["player"]["forms"][self.skin]

    def get_action(self, action_name: str) -> dict:
        return self.get_form_data().get("actions", {}).get(action_name, {})

    def get_combat_data(self) -> dict:
        return self.get_form_data().get("combat", {})

    def can_dash(self) -> bool:
        action = self.get_action("dash")
        if not action:
            return False
        return self.mana >= action.get("mana_cost", 0)

    def can_attack(self) -> bool:
        action = self.get_action("attack")
        if not action:
            return False
        return self.mana >= action.get("mana_cost", 0)

    def can_special_attack(self) -> bool:
        action = self.get_action("special")
        if not action:
            return False
        return self.mana >= action.get("mana_cost", 0)

    def consume_mana(self, amount: float) -> bool:
        if self.mana >= amount:
            self.mana -= amount
            return True
        return False

    def toggle_phase(self) -> bool:
        if self.is_busy() or self.phase_cooldown_timer > 0.0:
            return False
        self.phase_color = "green" if self.phase_color == "red" else "red"
        self.phase_cooldown_timer = self.phase_cooldown_max
        self._sync_animation()
        return True

    def change_skin(self, new_skin: str) -> None:
        self.skin = new_skin
        self._anim_timer = 0.0
        self._anim_idx = 0
        self.area_active = False
        self.dash_requested = False
        self.attack_requested = False
        self.special_attack_requested = False
        self.jump_requested = False
        max_jumps = self.form_stats[self.skin]["jumps"]
        if self.on_ground:
            self.jumps_left = max_jumps
        elif self.jumps_left > max_jumps:
            self.jumps_left = max_jumps
        self._sync_animation()

    def cycle_skin(self, direction: int = 1) -> Optional[str]:
        if self.is_busy():
            return None
        if not self.available_skins or len(self.available_skins) <= 1:
            return None
        if self.skin_cooldown_timer > 0.0:
            return None

        if self.skin in self.available_skins:
            curr_idx = self.available_skins.index(self.skin)
            next_idx = (curr_idx + direction) % len(self.available_skins)
        else:
            next_idx = 0

        self.change_skin(self.available_skins[next_idx])
        self.skin_cooldown_timer = self.skin_cooldown_max
        return self.skin

    def toggle_skin(self) -> Optional[str]:
        return self.cycle_skin(1)

    def _sync_animation(self) -> None:
        texture_key = f"{self.skin}_{self.phase_color}"
        skin_anims = self.animations.get(texture_key, {})
        anim_name = getattr(self, "_last_anim_name", "idle")
        self.current_animation = skin_anims.get(anim_name, skin_anims.get("idle"))

    def change_animation(self, new_anim_name: str) -> None:
        self._last_anim_name = new_anim_name
        self._anim_timer = 0.0
        self._anim_idx = 0
        texture_key = f"{self.skin}_{self.phase_color}"
        skin_anims = self.animations.get(texture_key, {})
        self.current_animation = skin_anims.get(new_anim_name, skin_anims.get("idle"))
        if self.current_animation is not None:
            self.current_animation.reset()

    def _get_anim_dict(self) -> dict[str, list[int]]:
        anim_map = entity_defs.ENTITY_DEFS["animations"]["player"].get(self.skin, {})
        return {name: data["frames"] for name, data in anim_map.items()}

    def on_input(self, input_id: str, input_data: InputData) -> None:
        """Despacha la entrada a través del CommandBindings del jugador."""
        self.command_bindings.dispatch(self, input_id, input_data)

    def update(self, dt: float, commands: Optional[Any] = None) -> None:
        if commands is not None:
            self.commands = commands

        if self.phase_cooldown_timer > 0.0:
            self.phase_cooldown_timer = max(0.0, self.phase_cooldown_timer - dt)
        if self.skin_cooldown_timer > 0.0:
            self.skin_cooldown_timer = max(0.0, self.skin_cooldown_timer - dt)

        if self.state_name != "death":
            regen = self.form_stats[self.skin]["mana_regen"]
            max_mp = self.form_stats[self.skin]["max_mana"]
            self.form_stats[self.skin]["mana"] = min(max_mp, self.form_stats[self.skin]["mana"] + regen * dt)

        for f in self.flames[:]:
            f["timer"] += dt
            if f["timer"] >= (entity_defs.FLAME_FRAMES / 20.0):
                self.flames.remove(f)

        super().update(dt)

    def render(
        self,
        surface: pygame.Surface,
        camera_x: float = 0.0,
        camera_y: float = 0.0,
    ) -> None:
        if self.current_animation is None:
            return

        texture_key = f"{self.skin}_{self.phase_color}"
        frame_rect: pygame.Rect = self.current_animation.get_current_frame()

        offsets = entity_defs.ENTITY_DEFS["player"]["forms"][self.skin]["offsets"]
        ox = offsets["right"] if self.facing == "right" else offsets["left"]
        oy = offsets["y"]

        draw_x = self.hitbox.x + ox - camera_x
        draw_y = self.hitbox.y + oy - camera_y

        sub = settings.TEXTURES[texture_key].subsurface(frame_rect)
        if self.facing == "right":
            sprite_surf = sub
        else:
            sprite_surf = pygame.transform.flip(sub, True, False)

        outline_color = (255, 120, 120, 220) if self.phase_color == "red" else (90, 240, 150, 220)
        self.render_outline(surface, sprite_surf, draw_x, draw_y, outline_color)

        surface.blit(sprite_surf, (draw_x, draw_y))

        if self.skin == "mage" and self.area_active:
            atk2_key = f"mage_atk2_{self.phase_color}"
            atk2_texture = settings.TEXTURES.get(atk2_key)
            atk2_frames = settings.FRAMES.get(atk2_key)
            if atk2_texture and atk2_frames:
                circle_frame_indices = entity_defs.MAGE_AREA_CIRCLES[self.area_circle_idx]
                circle_rect = atk2_frames[circle_frame_indices[self.area_subframe]]

                offsets_x = [45, 105, 175]
                base_offset = offsets_x[self.area_circle_idx]
                circle_offset_x = base_offset if self.facing == "right" else -base_offset
                circle_draw_x = (
                    self.hitbox.centerx + circle_offset_x
                    - (128 // 2)
                    - camera_x
                )
                circle_draw_y = self.hitbox.bottom - 47 - camera_y

                if self.facing == "right":
                    surface.blit(atk2_texture, (circle_draw_x, circle_draw_y), circle_rect)
                else:
                    sub_circle = atk2_texture.subsurface(circle_rect)
                    flipped = pygame.transform.flip(sub_circle, True, False)
                    surface.blit(flipped, (circle_draw_x, circle_draw_y))

        flame_color = "purple" if self.phase_color == "red" else "green"
        flame_texture = settings.TEXTURES.get(f"flame_{flame_color}")
        flame_rects = settings.FRAMES.get(f"flame_{flame_color}")
        if flame_texture and flame_rects:
            for f in self.flames:
                frame_idx = int(f["timer"] * 20.0)
                if frame_idx < entity_defs.FLAME_FRAMES:
                    sizes = [64, 96, 128]
                    size = sizes[f["idx"]]
                    flame_rect = flame_rects[frame_idx]
                    sub_flame = flame_texture.subsurface(flame_rect)
                    scaled = pygame.transform.scale(sub_flame, (size, size))
                    scaled.set_alpha(200)
                    rect = scaled.get_rect(midbottom=(
                        int(f["x"] - camera_x),
                        int(f["y"] - camera_y),
                    ))
                    surface.blit(scaled, rect)
