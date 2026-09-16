from src.states.entity.EntityBaseState import EntityBaseState


class WalkState(EntityBaseState):

    def enter(self) -> None:
        player = self.entity
        player.change_animation("run" if player.is_running else "walk")
        self.apply_horizontal_movement()

    def update(self, dt: float) -> None:
        player =self.entity
        
        if self.handle_buffered_inputs():
            return

        if player.move_direction == 0:
            player.vx = 0.0
            self.change_state("idle")
            return

        self.apply_horizontal_movement()
        player.change_animation("run" if player.is_running else "walk")

        if not player.on_ground:
            self.change_state("fall")
