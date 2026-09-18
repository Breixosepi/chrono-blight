"""
Chrono Blight - DashState
"""
from src.states.entity.EntityBaseState import EntityBaseState
import settings


class DashState(EntityBaseState):
    has_gravity: bool = False

    def enter(self) -> None:
        
        player = self.entity
        player.change_animation("dash")
        player.dash_requested = False

        dash_action = player.get_action("dash")
        self.dash_speed = float(dash_action.get("dash_speed", 220.0))

        direction = 1.0 if player.facing == "right" else -1.0
        player.vx = self.dash_speed * direction
        player.vy = 0.0

        mana_cost = dash_action.get("mana_cost", 0)
        if mana_cost > 0:
            player.consume_mana(mana_cost)

        if "morph-dash" in settings.SOUNDS:
            settings.SOUNDS["morph-dash"].play()

    def update(self, dt: float) -> None:
        player = self.entity
        direction = 1.0 if player.facing == "right" else -1.0
        player.vx = self.dash_speed * direction
        player.vy = 0.0

        if player.is_animation_finished():
            player.vx = 0.0
            post_dash_invulnerability = 0.15
            player.invulnerable_timer = max(
                player.invulnerable_timer, post_dash_invulnerability
            )

            if player.on_ground:
                self.change_state("idle")
            else:
                self.change_state("fall")

    def exit(self) -> None:
        player = self.entity
        player.vx = 0.0