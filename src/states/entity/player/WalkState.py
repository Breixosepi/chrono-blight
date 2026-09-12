"""
Chrono Blight
"""

from src.states.entity.EntityBaseState import EntityBaseState
from src.definitions import entity as entity_defs


class WalkState(EntityBaseState):

    def enter(self) -> None:
        self.entity.change_animation("walk")
        if self.entity.move_direction != 0:
            self.entity.facing = "left" if self.entity.move_direction < 0 else "right"
            speed = entity_defs.RUN_SPEED if self.entity.is_running else entity_defs.WALK_SPEED
            self.entity.vx = speed * self.entity.move_direction

    def update(self, dt: float) -> None:
        if self.entity.attack_requested:
            self.entity.attack_requested = False
            if self.entity.can_attack():
                self.change_state("attack")
                return

        if self.entity.special_attack_requested:
            self.entity.special_attack_requested = False
            if self.entity.can_special_attack():
                self.change_state("attack_special")
                return

        if self.entity.dash_requested:
            self.entity.dash_requested = False
            if self.entity.can_dash():
                self.change_state("dash")
                return

        if self.entity.jump_requested:
            self.entity.jump_requested = False
            if self.entity.jumps_left > 0:
                self.change_state("jump")
                return

        if self.entity.move_direction == 0:
            self.entity.vx = 0.0
            self.change_state("idle")
            return

        self.entity.facing = "left" if self.entity.move_direction < 0 else "right"
        speed = entity_defs.RUN_SPEED if self.entity.is_running else entity_defs.WALK_SPEED
        self.entity.vx = speed * self.entity.move_direction

        target_anim = "run" if self.entity.is_running else "walk"
        if getattr(self.entity, "_last_anim_name", None) != target_anim:
            self.entity.change_animation(target_anim)

        if not self.entity.on_ground:
            self.change_state("fall")
