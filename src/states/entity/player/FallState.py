from src.states.entity.EntityBaseState import EntityBaseState

class FallState(EntityBaseState):
    def enter(self) -> None:
        player = self.entity
        player.change_animation("fall")

    def update(self, dt: float) -> None:
        player = self.entity
        self.apply_horizontal_movement()

        if player.jump_requested and player.jumps_left > 0:
            player.jump_requested = False
            self.change_state("jump")
            return

        if self.handle_buffered_inputs(allow_air_special=True):
            return

        if player.on_ground:
            self.on_land()

    def on_land(self) -> None:
        player = self.entity
        if player.vx != 0.0:
            self.change_state("walk")
        else:
            self.change_state("idle")