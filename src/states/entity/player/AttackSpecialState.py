"""
Chrono Blight
"""

from src.states.entity.EntityBaseState import EntityBaseState
from src.definitions import entity as entity_defs


class AttackSpecialState(EntityBaseState):
    has_gravity: bool = False

    def enter(self) -> None:
        self.entity.change_animation("attack_special")
        self.entity.vx = 0.0
        self.entity.vy = 0.0
        self.action = self.entity.get_action("special")
        cost = self.action.get("mana_cost", 0)
        if cost > 0:
            self.entity.consume_mana(cost)

        if self.action.get("on_start"):
            self.action["on_start"](self.entity)

        self.entity.special_attack_requested = False

        anim_frames = self.entity._get_anim_dict().get("attack_special", [0])
        anim_def = entity_defs.ENTITY_DEFS["animations"]["player"][self.entity.skin].get(
            "attack_special", {"interval": 1/10.0}
        )
        self.duration = len(anim_frames) * anim_def["interval"]

    def update(self, dt: float) -> None:
        self.entity.vx = 0.0
        self.entity.vy = 0.0

        if self.action.get("on_update"):
            self.action["on_update"](self.entity, dt)

        if self.entity.is_animation_finished(fallback_duration=self.duration):
            if self.action.get("on_finish"):
                self.action["on_finish"](self.entity)

            if self.entity.on_ground:
                self.change_state("idle")
            else:
                self.change_state("fall")
