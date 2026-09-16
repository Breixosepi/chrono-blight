"""
Chrono Blight - Camera Wrapper
"""
from typing import Tuple, Optional
import pygame
from gale.camera import Camera as GaleCamera


class Camera(GaleCamera):
    def __init__(
        self,
        viewport_width: int,
        viewport_height: int,
        bounds: Optional[pygame.Rect] = None,
    ) -> None:
        super().__init__(float(viewport_width), float(viewport_height))
        self.map_w: int = viewport_width
        self.map_h: int = viewport_height
        self.smooth_follow: bool = True
        self.follow_speed: float = 18.0

        if bounds is not None:
            self.bounds = bounds
            self.map_w = bounds.width
            self.map_h = bounds.height

    def set_map_bounds(self, map_width: int, map_height: int) -> None:
        self.map_w = map_width
        self.map_h = map_height
        self.bounds = pygame.Rect(0, 0, map_width, map_height)

    def update(self, target_x: float, target_y: float, dt: float = 0.0) -> None:
        if self.smooth_follow and dt > 0.0:
            lerp_factor = min(1.0, self.follow_speed * dt)
            self.x += (target_x - self.x) * lerp_factor
            self.y += (target_y - self.y) * lerp_factor
        else:
            self.x = target_x
            self.y = target_y

        super().update(dt)

    def snap_to(self, target_x: float, target_y: float) -> None:
        self.x = target_x
        self.y = target_y
        super().update(0.0)

    def get_offset(self) -> Tuple[float, float]:
        ox, oy = self.offset
        return (round(ox), round(oy))