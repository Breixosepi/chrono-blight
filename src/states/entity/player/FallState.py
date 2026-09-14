from src.states.entity.EntityBaseState import EntityBaseState


class FallState(EntityBaseState):

    def enter(self) -> None:
        self.entity.change_animation("fall")

    def update(self, dt: float) -> None:
        self.apply_horizontal_movement()

        if self.entity.jump_requested and self.entity.jumps_left > 0:
            self.entity.jump_requested = False
            self.change_state("jump")
            return

        if self.handle_buffered_inputs(allow_air_special=True):
            return

        if self.entity.on_ground:
            self.on_land()

    def on_land(self) -> None:
        if self.entity.vx != 0.0:
            self.change_state("walk")
        else:
            self.change_state("idle")
