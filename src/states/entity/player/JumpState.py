from src.states.entity.EntityBaseState import EntityBaseState
from src.definitions import entity as entity_defs


class JumpState(EntityBaseState):

    def enter(self) -> None:
        if self.entity.on_ground and hasattr(self.entity, "on_jump_effect"):
            self.entity.on_jump_effect()
        self.entity.change_animation("jump")
        self.entity.vy = entity_defs.JUMP_VELOCITY
        self.entity.jumps_left -= 1
        self.entity.on_ground = False
        self.entity.jump_requested = False

    def update(self, dt: float) -> None:
        if not self.entity.jump_held and self.entity.vy < -120.0:
            self.entity.vy = -120.0

        self.apply_horizontal_movement()

        if self.entity.jump_requested and self.entity.jumps_left > 0:
            self.entity.jump_requested = False
            self.change_state("jump")
            return

        if self.handle_buffered_inputs(allow_air_special=True):
            return

        if self.entity.vy >= 0:
            self.change_state("fall")
            return

        if self.entity.on_ground:
            self.on_land()

    def on_land(self) -> None:
        self.change_state("walk" if self.entity.vx != 0.0 else "idle")
