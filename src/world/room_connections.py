"""
Chrono Blight - World Room Connections & Topology
"""
from typing import Dict, List, Any, Tuple, Optional, Callable

DEFAULT_START_ROOM = "middle"
DEFAULT_START_SPAWN = (64.0, 208.0)
MARGIN = 6.0

def _check_exit_right(
    player: Any,
    room: Any,
    y_min: float = 0.0,
    y_max: Optional[float] = None,
) -> bool:
    if player.hitbox.right < room.MAP_WIDTH - MARGIN or player.vx < 0:
        return False
    cy = player.hitbox.centery
    if y_max is not None:
        return y_min <= cy < y_max
    return cy >= y_min

def _check_exit_left(
    player: Any,
    y_min: float = 0.0,
    y_max: Optional[float] = None,
) -> bool:
    if player.hitbox.left > MARGIN or player.vx > 0:
        return False
    cy = player.hitbox.centery
    if y_max is not None:
        return y_min <= cy < y_max
    return cy >= y_min


def _check_exit_top(
    player: Any,
    x_min: float,
    x_max: float,
    margin_top: float = 10.0,
) -> bool:
    return (
        player.hitbox.top <= margin_top
        and player.vy <= 0
        and (x_min <= player.hitbox.centerx <= x_max)
    )

def _check_exit_bottom(
    player: Any,
    room: Any,
    x_min: float,
    x_max: float,
) -> bool:
    return (
        player.hitbox.bottom >= room.MAP_HEIGHT - MARGIN
        and player.vy >= 0
        and (x_min <= player.hitbox.centerx <= x_max)
    )


ROOM_CONNECTIONS: Dict[str, List[Dict[str, Any]]] = {
    "middle": [
        {
            "direction": "right_top",
            "check": lambda p, r: _check_exit_right(p, r, y_max=260.0),
            "target_room": "esquina_1",
            "target_spawn": (48.0, 104.0),
        },
        {
            "direction": "right_bottom",
            "check": lambda p, r: _check_exit_right(p, r, y_min=260.0),
            "target_room": "subida",
            "target_spawn": (64.0, 576.0),
        },
        {
            "direction": "left_top",
            "check": lambda p, r: _check_exit_left(p, y_max=260.0),
            "target_room": "left_corner",
            "target_spawn": (352.0, 248.0),
        },
        {
            "direction": "left_bottom",
            "check": lambda p, r: _check_exit_left(p, y_min=260.0),
            "target_room": "abismo_fixed",
            "target_spawn": (760.0, 104.0),
        },
    ],
    "subida": [
        {
            "direction": "left",
            "check": lambda p, r: (
                p.hitbox.left <= MARGIN
                and p.vx <= 0
                and p.hitbox.bottom >= 550
            ),
            "target_room": "middle",
            "target_spawn": (440.0, 368.0),
        },
        {
            "direction": "top",
            "check": lambda p, r: _check_exit_top(p, 100.0, 180.0),
            "target_room": "esquina_1",
            "target_spawn": (200.0, 120.0),
        },
    ],
    "esquina_1": [
        {
            "direction": "left_bottom",
            "check": lambda p, r: _check_exit_left(p),
            "target_room": "middle",
            "target_spawn": (440.0, 180.0),
        },
    ],
    "abismo_fixed": [
        {
            "direction": "left",
            "check": lambda p, r: _check_exit_left(p),
            "target_room": "sala_past",
            "target_spawn": (576.0, 152.0),
        },
        {
            "direction": "right",
            "check": lambda p, r: _check_exit_right(p, r),
            "target_room": "middle",
            "target_spawn": (40.0, 384.0),
        },
    ],
    "sala_past": [
        {
            "direction": "right",
            "check": lambda p, r: _check_exit_right(p, r),
            "target_room": "abismo_fixed",
            "target_spawn": (48.0, 104.0),
        },
    ],
    "sala_future": [
        {
            "direction": "left",
            "check": lambda p, r: _check_exit_left(p),
            "target_room": "left_corner",
            "target_spawn": (352.0, 88.0),
        },
    ],
    "left_corner": [
        {
            "direction": "right_bottom",
            "check": lambda p, r: _check_exit_right(p, r, y_min=150.0),
            "target_room": "middle",
            "target_spawn": (60.0, 200.0),
        },
        {
            "direction": "right_top",
            "check": lambda p, r: _check_exit_right(p, r, y_max=150.0),
            "target_room": "sala_future",
            "target_spawn": (64.0, 120.0),
        },
    ],
    "big_room": [
        {
            "direction": "bottom",
            "check": lambda p, r: _check_exit_bottom(p, r, 760.0, 840.0),
            "target_room": "middle",
            "target_spawn": (240.0, 32.0),
        },
    ],
}