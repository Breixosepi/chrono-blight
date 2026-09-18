import pygame
from typing import Any
import settings

class CombatResolver:
    def __init__(self, room: Any):
        self.room = room
        self._hit_this_swing = set()
        self._flame_hits = set()
        self._prev_attack_state = False

    def update(self) -> None:
        currently_attacking = self.room.player.state_name in ("attack", "attack_special")
        if currently_attacking and not self._prev_attack_state:
            self._hit_this_swing.clear()
            self._flame_hits.clear()
        self._prev_attack_state = currently_attacking

    def handle_melee_combat(self, enemy: Any) -> None:
        attack_hitbox = self.room.player.get_attack_hitbox()
        if not attack_hitbox or not attack_hitbox.colliderect(enemy.hitbox): 
            return

        hit_id = (id(enemy), getattr(self.room.player, "swing_id", 0))
        if hit_id in self._hit_this_swing: 
            return
        self._hit_this_swing.add(hit_id)

        if getattr(enemy, "shield_active", False) or getattr(enemy, "invulnerable", False):
            settings.SOUNDS["shield-active"].play()
            self.room.camera.shake(1.8, 0.1)
            self.room._spawn_popup("ESCUDO", enemy.hitbox.centerx, enemy.hitbox.top - 8, 0.45, (220, 110, 255))
            return

        action_def = self.room.player.get_action("special" if self.room.player.state_name == "attack_special" else "attack")
        is_combo_2 = getattr(self.room.player.state_machine.current, "in_combo_followup", False)
        
        damage = int(action_def.get("combo", {}).get("hit2_damage", action_def.get("damage", 10))) if is_combo_2 else int(action_def.get("damage", 10))
        shake = 3.0 if is_combo_2 else 1.5

        settings.SOUNDS["slash-hit"].play()
        enemy.take_damage(float(damage))
        self.room.camera.shake(shake, 0.15)
        self.room._spawn_popup(f"-{damage}", enemy.hitbox.centerx, enemy.hitbox.top - 6, 0.5, (255, 230, 80))

    def handle_magic_combat(self, enemy: Any) -> None:
        if self.room.player.skin != "mage" or not self.room.player.area_active: 
            return

        is_boss = (
            getattr(enemy, "is_boss", False)
            or "boss" in getattr(enemy, "enemy_type", "")
            or getattr(enemy, "enemy_type", "") in ("cultist_priest", "the_harvester", "monster2_boss")
        )

        for flame in self.room.player.flames:
            flame_hitbox = pygame.Rect(int(flame["x"]) - 32, int(flame["y"]) - 56, 64, 56)
            hit_id = (id(enemy), "boss" if is_boss else flame["idx"])
            
            if flame_hitbox.colliderect(enemy.hitbox) and hit_id not in self._flame_hits:
                self._flame_hits.add(hit_id)
                if getattr(enemy, "shield_active", False) or getattr(enemy, "invulnerable", False):
                    settings.SOUNDS["shield-active"].play()
                    self.room._spawn_popup("ESCUDO", enemy.hitbox.centerx, enemy.hitbox.top - 8, 0.45, (220, 110, 255))
                else:
                    action_def = self.room.player.get_action("special")
                    damage = int(action_def.get("boss_damage", 20) if is_boss else action_def.get("damage", 60))
                    enemy.take_damage(float(damage))
                    self.room.camera.shake(2.0, 0.12)
                    self.room._spawn_popup(f"-{damage}", enemy.hitbox.centerx, enemy.hitbox.top - 8, 0.5, (255, 130, 40))

    def handle_contact_damage(self, enemy: Any) -> None:
        can_hit = (
            enemy.state_name not in ("hit", "death")
            and self.room.player.state_name not in ("hit", "death", "dash")
            and not getattr(self.room, "_is_sword_special", False)
            and self.room.player.invulnerable_timer <= 0.0
            and enemy.hitbox.colliderect(self.room.player.hitbox)
        )
        if can_hit:
            dmg = int(enemy.contact_damage)
            self.room.player.take_damage(dmg, source_x=enemy.hitbox.centerx)
            self.room.camera.shake(3.5, 0.2)
            self.room._spawn_popup(f"-{dmg}", self.room.player.hitbox.centerx, self.room.player.hitbox.top - 8, 0.6, (255, 75, 75))

