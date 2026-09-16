from src.states.entity.EntityBaseState import EntityBaseState


class IdleState(EntityBaseState):

    def enter(self) -> None:
        player = self.entity
        player.change_animation("idle")
        player.vx = 0.0

    def update(self, dt: float) -> None:
        player = self.entity
        if self.handle_buffered_inputs():
            return

        if player.move_direction != 0:
            player.facing = "left" if player.move_direction < 0 else "right"
            self.change_state("walk")
            return

        if not player.on_ground:
            self.change_state("fall")
