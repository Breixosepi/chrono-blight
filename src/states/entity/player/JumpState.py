from src.states.entity.EntityBaseState import EntityBaseState
from src.definitions import entity as entity_defs
import settings

class JumpState(EntityBaseState):
    def enter(self) -> None:
        settings.SOUNDS["jump"].play()
        player = self.entity
        if player.on_ground and hasattr(player, "on_jump_effect"):
            player.on_jump_effect()
            
        player.change_animation("jump")
        player.vy = entity_defs.JUMP_VELOCITY
        player.jumps_left -= 1
        player.on_ground = False
        player.jump_requested = False

    def update(self, dt: float) -> None:
        player = self.entity
        
        if not player.jump_held and player.vy < -120.0:
            player.vy = -120.0
            
        self.apply_horizontal_movement()

        if player.jump_requested and player.jumps_left > 0:
            player.jump_requested = False
            self.change_state("jump")
            return

        if self.handle_buffered_inputs(allow_air_special=True):
            return

        if player.vy >= 0:
            self.change_state("fall")
            return

        if player.on_ground:
            self.on_land()

    def on_land(self) -> None:
        player = self.entity
        self.change_state("walk" if player.vx != 0.0 else "idle")