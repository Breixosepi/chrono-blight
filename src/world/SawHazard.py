import pygame
from typing import Any, List, Optional
import settings


class SawHazard:
    _FRAMES_CACHE: dict[str, List[pygame.Surface]] = {}

    @classmethod
    def _get_frames(cls, hazard_type: str) -> List[pygame.Surface]:
        if hazard_type not in cls._FRAMES_CACHE:
            path = settings.BASE_DIR / "assets" / "graphics" / "player" / "sword" / "SawBladeSuriken.png"
            surf = pygame.image.load(str(path)).convert_alpha()
            if hazard_type == "shuriken":
                cls._FRAMES_CACHE["shuriken"] = [
                    surf.subsurface((i * 25 + 4, 36, 24, 24)) for i in range(2)
                ]
            else:
                cls._FRAMES_CACHE["saw"] = [
                    surf.subsurface((i * 24 + 4, 4, 24, 24)) for i in range(4)
                ]
        return cls._FRAMES_CACHE[hazard_type]

    def __init__(
        self,
        room: Any,
        x: float,
        y: float,
        hazard_type: str = "saw",
        phase: str = "neutral",
        patrol_dist: float = 0.0,
        axis: str = "y",
        speed: float = 50.0,
        damage: int = 15,
    ):
        self.room = room
        self.start_x = x
        self.start_y = y
        self.x = x
        self.y = y
        self.width = 24
        self.height = 24
        self.hitbox = pygame.Rect(int(x), int(y), self.width, self.height)
        self.hazard_type = hazard_type
        self.phase = phase
        self.patrol_dist = patrol_dist
        self.axis = axis.lower()
        self.speed = speed
        self.damage = damage
        self.direction = 1

        self.frames = self._get_frames(hazard_type)
        self.frame_index = 0
        self.anim_timer = 0.0
        self.frame_time = 0.08

    def update(self, dt: float) -> None:
        if self.phase != "neutral" and self.room.player.phase_color != self.phase:
            return

        # Animación de giro
        self.anim_timer += dt
        if self.anim_timer >= self.frame_time:
            self.anim_timer = 0.0
            self.frame_index = (self.frame_index + 1) % len(self.frames)

        # Movimiento patrulla
        if self.patrol_dist > 0:
            if self.axis == "y":
                self.y += self.direction * self.speed * dt
                if self.direction > 0 and self.y >= self.start_y + self.patrol_dist:
                    self.y = self.start_y + self.patrol_dist
                    self.direction = -1
                elif self.direction < 0 and self.y <= self.start_y:
                    self.y = self.start_y
                    self.direction = 1
            else:
                self.x += self.direction * self.speed * dt
                if self.direction > 0 and self.x >= self.start_x + self.patrol_dist:
                    self.x = self.start_x + self.patrol_dist
                    self.direction = -1
                elif self.direction < 0 and self.x <= self.start_x:
                    self.x = self.start_x
                    self.direction = 1

        self.hitbox.topleft = (int(self.x), int(self.y))

        # Colisión con el jugador
        player = self.room.player
        if not player.is_dead() and self.hitbox.colliderect(player.hitbox):
            if player.invulnerable_timer <= 0:
                player.take_damage(self.damage)
                self.room.camera.shake(3.0, 0.2)
                self.room._spawn_popup(
                    f"-{self.damage}",
                    player.hitbox.centerx,
                    player.hitbox.top - 10,
                    0.7,
                    (255, 60, 60),
                )

    def render(self, surface: pygame.Surface, camera_x: float, camera_y: float) -> None:
        if self.phase != "neutral" and self.room.player.phase_color != self.phase:
            return

        frame = self.frames[self.frame_index]
        draw_x = int(self.x - camera_x)
        draw_y = int(self.y - camera_y)
        surface.blit(frame, (draw_x, draw_y))

