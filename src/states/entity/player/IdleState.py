from src.states.entity.EntityBaseState import EntityBaseState


class IdleState(EntityBaseState):

    def enter(self) -> None:
        self.entity.change_animation("idle")
        self.entity.vx = 0.0

    def update(self, dt: float) -> None:
        if self.handle_buffered_inputs():
            return

        if self.entity.move_direction != 0:
            self.entity.facing = "left" if self.entity.move_direction < 0 else "right"
            self.change_state("walk")
            return

        if not self.entity.on_ground:
            self.change_state("fall")
