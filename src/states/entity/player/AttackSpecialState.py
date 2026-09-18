"""
Chrono Blight - AttackSpecialState
"""
from src.states.entity.EntityBaseState import EntityBaseState
from src.definitions import entity as entity_defs
import settings

class AttackSpecialState(EntityBaseState):
    has_gravity: bool = False

    def enter(self) -> None:

        player = self.entity
        player.change_animation("attack_special")
        player.vx = 0.0
        player.vy = 0.0

        self.action = player.get_action("special")
        mana_cost = self.action.get("mana_cost", 0)
        if mana_cost > 0:
            player.consume_mana(mana_cost)

        if player.skin == "mage":
            player.area_active = True
            player.area_circle_idx = 0
            player.area_subframe = 0

        player.special_attack_requested = False

        if player.skin == "sword":
            settings.SOUNDS["sword-dash"].play()
        elif player.skin == "mage":
            settings.SOUNDS["mage-special"].play()
        elif player.skin == "morph":
            settings.SOUNDS["morph-power"].play()

    def _update_mage_fire_area(self, dt: float) -> None:

        player = self.entity
        circle_fps = 12.0
        total_area_frame = int(player._anim_timer * circle_fps)

        num_circles = len(entity_defs.MAGE_AREA_CIRCLES)
        frames_per_circle = len(entity_defs.MAGE_AREA_CIRCLES[0]) if num_circles > 0 else 6

        new_circle_idx = min(num_circles - 1, total_area_frame // frames_per_circle)
        player.area_subframe = total_area_frame % frames_per_circle

        first_frame_trigger = (
            new_circle_idx == 0 and total_area_frame == 0 and player._anim_timer <= dt
        )
        if new_circle_idx != player.area_circle_idx or first_frame_trigger:
            offsets_x = [45, 105, 175]
            base_offset = offsets_x[new_circle_idx]
            circle_offset_x = base_offset if player.facing == "right" else -base_offset
            spawn_x = player.hitbox.centerx + circle_offset_x
            spawn_y = player.hitbox.bottom

            player.flames.append({
                "x": spawn_x,
                "y": spawn_y,
                "idx": new_circle_idx,
                "timer": 0.0,
            })
        player.area_circle_idx = new_circle_idx

    def update(self, dt: float) -> None:
        
        player = self.entity
        player.vx = 0.0
        player.vy = 0.0

        if player.skin == "mage":
            self._update_mage_fire_area(dt)

        if player.is_animation_finished():
            if player.on_ground:
                self.change_state("idle")
            else:
                self.change_state("fall")

    def exit(self) -> None:
        player = self.entity

        if player.skin == "sword":
            dash_distance = 78.0
            dash_direction = 1.0 if player.facing == "right" else -1.0
            player.x += dash_distance * dash_direction
            player.hitbox.x = int(player.x)
            player.invulnerable_timer = max(player.invulnerable_timer, 0.25)

        elif player.skin == "mage":
            player.area_active = False