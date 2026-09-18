"""
Chrono Blight - HarvesterAttackState
Executes scythe slash combo and releases wind blades / dimensional slashes.
"""
import random
from typing import TYPE_CHECKING
import pygame

from src.states.entity.boss.BossBaseState import BossBaseState
import settings

if TYPE_CHECKING:
    from src.entities.Boss import Boss


class HarvesterAttackState(BossBaseState):
    def __init__(self, entity: "Boss", sm):
        super().__init__(entity, sm)
        self.entity = entity
        self.attack_done: bool = False
        self.ability_fired: bool = False

    def enter(self) -> None:
        self.entity.change_animation("attack")
        self.entity.can_hit_player = True
        self.entity.vx = 0.0
        self.attack_done = False
        self.ability_fired = False

        player = self.entity.room.player if self.entity.room else None
        if player:
            if player.hitbox.centerx < self.entity.hitbox.centerx:
                self.entity.facing = "left"
            else:
                self.entity.facing = "right"

    def update(self, dt: float) -> None:
        if self.entity.health <= 0:
            self.entity.change_state("death")
            return

        anim = self.entity.current_animation
        cur_frame = anim.current_frame_index if anim else 0

        if not self.attack_done and cur_frame >= 6:
            self._do_melee_hit()
            self.attack_done = True

        if not self.ability_fired and cur_frame >= 6:
            self._fire_ability()
            self.ability_fired = True

        if self.attack_done and anim and anim.times_played > 0:
            self.entity.change_state("idle", cooldown=0.8 if getattr(self.entity, "boss_phase", 1) == 3 else 1.2)

    def _do_melee_hit(self) -> None:
        if self.entity.room is None or self.entity.room.player is None:
            return

        dist = abs(self.entity.hitbox.centerx - self.entity.room.player.hitbox.centerx)
        if dist > 45:
            return

        reach = 38
        if self.entity.facing == "left":
            hitbox = pygame.Rect(self.entity.hitbox.left - reach, self.entity.hitbox.top, reach, self.entity.hitbox.height)
        else:
            hitbox = pygame.Rect(self.entity.hitbox.right, self.entity.hitbox.top, reach, self.entity.hitbox.height)

        player = self.entity.room.player
        if not player.is_dead() and hitbox.colliderect(player.hitbox):
            is_sword_special = (player.state_name == "attack_special" and player.skin == "sword")
            if player.state_name not in ("hit", "death", "dash") and not is_sword_special and player.invulnerable_timer <= 0.0:
                player.take_damage(14, source_x=self.entity.hitbox.centerx)
                if self.entity.room:
                    self.entity.room.camera.shake(3.5, 0.2)
                    self.entity.room._spawn_popup("-14", player.hitbox.centerx, player.hitbox.top - 10, 0.7, (255, 75, 75))
                    self.entity.room.spawn_dust(player.hitbox.centerx, player.hitbox.bottom, count=8)

    def _fire_ability(self) -> None:
        boss = self.entity
        player = boss.room.player if boss.room else None
        if not player:
            return

        phase = getattr(boss, "boss_phase", 1)
        dir_x = -1.0 if boss.facing == "left" else 1.0

        if phase == 1:
            color = boss.phase if boss.phase in ("green", "red") else ("green" if random.random() < 0.5 else "red")
            if random.random() < 0.50:
                spawn_x = boss.hitbox.left - 12 if dir_x < 0 else boss.hitbox.right + 12
                spawn_y = boss.hitbox.bottom - 10
                if hasattr(boss, "spawn_wind_blade"):
                    boss.spawn_wind_blade(spawn_x, spawn_y, dir_x, phase_color=color, is_vertical=False)
                if "boss-wind-spell" in settings.SOUNDS:
                    settings.SOUNDS["boss-wind-spell"].play()
                if boss.room:
                    boss.room.spawn_dust(spawn_x, boss.hitbox.bottom, count=6)
            else:
                target_x = player.hitbox.centerx
                if hasattr(boss, "spawn_falling_blade"):
                    boss.spawn_falling_blade(target_x, phase_color=color, delay=0.45)
                if "boss-wind-spell" in settings.SOUNDS:
                    settings.SOUNDS["boss-wind-spell"].play()
                if boss.room:
                    boss.room.spawn_dust(boss.hitbox.centerx, boss.hitbox.bottom, count=8)

        elif phase == 2:
            color = "green" if random.random() < 0.5 else "red"
            target_x = player.hitbox.centerx
            if hasattr(boss, "spawn_falling_blade"):
                boss.spawn_falling_blade(target_x, phase_color=color, delay=0.35)
                lead = 50.0 if (player.vx >= 0 and player.facing == "right") else -50.0
                boss.spawn_falling_blade(target_x + lead, phase_color="red" if color == "green" else "green", delay=0.60)

            spawn_x = boss.hitbox.left - 12 if dir_x < 0 else boss.hitbox.right + 12
            spawn_y = boss.hitbox.bottom - 10
            if hasattr(boss, "spawn_wind_blade"):
                boss.spawn_wind_blade(spawn_x, spawn_y, dir_x, phase_color=color, is_vertical=False, speed=220.0)

            if "boss-wind-spell" in settings.SOUNDS:
                settings.SOUNDS["boss-wind-spell"].play()
            if boss.room:
                boss.room.spawn_dust(boss.hitbox.centerx, boss.hitbox.bottom, count=8)

        elif phase == 3:
            color = "red" if random.random() < 0.5 else "green"
            if hasattr(boss, "spawn_falling_blade"):
                boss.spawn_falling_blade(player.hitbox.centerx, phase_color=color, delay=0.40)

            if hasattr(boss, "spawn_dimensional_slash"):
                lead_x = player.hitbox.centerx + (random.choice([-45.0, 45.0]))
                boss.spawn_dimensional_slash(lead_x, player.hitbox.bottom - 16, phase_color="red" if color == "green" else "green", delay=1.0)

            dir_to_player = -1.0 if player.hitbox.centerx < boss.hitbox.centerx else 1.0
            spawn_x = boss.hitbox.left - 10 if dir_to_player < 0 else boss.hitbox.right + 10
            spawn_y = boss.hitbox.bottom - 10
            if hasattr(boss, "spawn_wind_blade"):
                boss.spawn_wind_blade(spawn_x, spawn_y, dir_to_player, phase_color=color, is_vertical=False, speed=250.0)
            if "sword" in settings.SOUNDS:
                settings.SOUNDS["sword"].play()
