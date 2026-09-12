
class Camera:

    def __init__(self, viewport_width: int, viewport_height: int) -> None:

        self.viewport_w: int = viewport_width
        self.viewport_h: int = viewport_height
        self.x: float = 0.0
        self.y: float = 0.0
        self.map_w: int = viewport_width
        self.map_h: int = viewport_height

    def set_map_bounds(self, map_width: int, map_height: int) -> None:

        self.map_w = map_width
        self.map_h = map_height

    def update(self, target_x: float, target_y: float) -> None:
        self.x = target_x - self.viewport_w / 2.0
        self.y = target_y - self.viewport_h / 2.0

        self.x = max(0.0, min(self.x, float(self.map_w  - self.viewport_w)))
        self.y = max(0.0, min(self.y, float(self.map_h - self.viewport_h)))

    def get_offset(self) -> tuple[float, float]:
        return (self.x, self.y)
