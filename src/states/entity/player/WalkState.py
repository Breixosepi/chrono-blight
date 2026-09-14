from src.states.entity.EntityBaseState import EntityBaseState


class WalkState(EntityBaseState):

    def enter(self) -> None:
        self.entity.change_animation("run" if self.entity.is_running else "walk")
        self.apply_horizontal_movement()

    def update(self, dt: float) -> None:
        if self.handle_buffered_inputs():
            return

        if self.entity.move_direction == 0:
            self.entity.vx = 0.0
            self.change_state("idle")
            return

        self.apply_horizontal_movement()
        self.entity.change_animation("run" if self.entity.is_running else "walk")

        if not self.entity.on_ground:
            self.change_state("fall")
