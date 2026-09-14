"""
Chrono Blight - World Room Connections & Topology
"""

from typing import Dict, List, Any, Tuple

DEFAULT_START_ROOM = "sala_past"
DEFAULT_START_SPAWN = (48.0, 144.0)

ROOM_CONNECTIONS: Dict[str, List[Dict[str, Any]]] = {
    "sala_past": [
        {
            "direction": "right",
            "check": lambda player, room: player.hitbox.right >= room.MAP_WIDTH - 6 and player.vx >= 0,
            "target_room": "abismo_fixed",
            "target_spawn": (24.0, 112.0),
        },
    ],
    "abismo_fixed": [
        {
            "direction": "left",
            "check": lambda player, room: player.hitbox.left <= 6 and player.vx <= 0,
            "target_room": "sala_past",
            "target_spawn": (600.0, 144.0),
        },
        {
            "direction": "right",
            "check": lambda player, room: player.hitbox.right >= room.MAP_WIDTH - 6 and player.vx >= 0,
            "target_room": "subida",
            "target_spawn": (40.0, 584.0),
        },
    ],
    "subida": [
        {
            "direction": "left",
            "check": lambda player, room: (
                player.hitbox.left <= 6
                and player.vx <= 0
                and player.hitbox.bottom >= 550
                and (room.rising_hazard is None or room.rising_hazard.gate_current_y < 560.0)
            ),
            "target_room": "abismo_fixed",
            "target_spawn": (760.0, 104.0),
        },
        {
            "direction": "top",
            "check": lambda player, room: (
                player.hitbox.top <= 10
                and player.vy <= 0
                and (100 <= player.hitbox.centerx <= 180)
            ),
            "target_room": "esquina_1",
            "target_spawn": (224.0, 264.0),
        },
    ],
    "esquina_1": [
        {
            "direction": "bottom",
            "check": lambda player, room: (
                player.hitbox.bottom >= room.MAP_HEIGHT - 6
                and player.vy >= 0
                and (160 <= player.hitbox.centerx <= 240)
            ),
            "target_room": "subida",
            "target_spawn": (140.0, 32.0),
        },
        {
            "direction": "left_top",
            "check": lambda player, room: (
                player.hitbox.left <= 6
                and player.vx <= 0
                and player.hitbox.top <= 120
            ),
            "target_room": "sala_future",
            "target_spawn": (32.0, 152.0),
        },
        {
            "direction": "left_bottom",
            "check": lambda player, room: (
                player.hitbox.left <= 6
                and player.vx <= 0
                and player.hitbox.bottom >= 200
            ),
            "target_room": "sala_future",
            "target_spawn": (32.0, 152.0),
        },
    ],
    "sala_future": [
        {
            "direction": "left",
            "check": lambda player, room: player.hitbox.left <= 6 and player.vx <= 0,
            "target_room": "esquina_1",
            "target_spawn": (24.0, 88.0),
        },
    ],
}

