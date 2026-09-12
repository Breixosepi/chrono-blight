"""
Chrono Blight
"""

from src.states.entity.EntityBaseState import EntityBaseState
from src.definitions import entity as entity_defs


class DashState(EntityBaseState):
    has_gravity: bool = False

    def enter(self) -> None:
        self.entity.change_animation("dash")
        self.entity.dash_requested = False
        action = self.entity.get_action("dash")
        self.dash_speed = action.get("dash_speed", 220.0)
        self.entity.vx = self.dash_speed if self.entity.facing == "right" else -self.dash_speed
        self.entity.vy = 0.0

        cost = action.get("mana_cost", 0)
        if cost > 0:
            self.entity.consume_mana(cost)
        if action.get("func"):
            action["func"](self.entity)

        anim_frames = self.entity._get_anim_dict().get("dash", [0])
        anim_def = entity_defs.ENTITY_DEFS["animations"]["player"][self.entity.skin].get(
            "dash", {"interval": 1/10.0}
        )
        self.duration = len(anim_frames) * anim_def["interval"]

    def update(self, dt: float) -> None:
        self.entity.vx = self.dash_speed if self.entity.facing == "right" else -self.dash_speed
        self.entity.vy = 0.0

        if self.entity.is_animation_finished(fallback_duration=self.duration):
            self.entity.vx = 0.0
            if self.entity.on_ground:
                self.change_state("idle")
            else:
                self.change_state("fall")

