"""
Chrono Blight - World Room Connections & Topology
Mapeo de interconexión y transiciones entre salas del juego.
"""

from typing import Dict, List, Any, Tuple

DEFAULT_START_ROOM = "sala_past"
DEFAULT_START_SPAWN = (48.0, 144.0)

ROOM_CONNECTIONS: Dict[str, List[Dict[str, Any]]] = {
    "sala_past": [
        {
            "direction": "right",
            "check": lambda player, room: player.hitbox.right >= room.MAP_WIDTH - 6,
            "target_room": "abismo_fixed",
            "target_spawn": (24.0, 112.0),
        },
    ],
    "abismo_fixed": [
        {
            "direction": "left",
            "check": lambda player, room: player.hitbox.left <= 6,
            "target_room": "sala_past",
            "target_spawn": (600.0, 144.0),
        },
        {
            "direction": "right",
            "check": lambda player, room: player.hitbox.right >= room.MAP_WIDTH - 6,
            "target_room": "subida",
            "target_spawn": (16.0, 592.0),
        },
    ],
    "subida": [
        {
            "direction": "left",
            "check": lambda player, room: (
                player.hitbox.left <= 6
                and player.hitbox.bottom >= 550
                and (room.rising_hazard is None or room.rising_hazard.gate_current_y < 560.0)
            ),
            "target_room": "abismo_fixed",
            "target_spawn": (700.0, 144.0),
        },
        {
            "direction": "top",
            "check": lambda player, room: player.hitbox.top <= 12 and (100 <= player.hitbox.centerx <= 180),
            "target_room": "sala_future",
            "target_spawn": (24.0, 144.0),
        },
    ],
    "sala_future": [
        {
            "direction": "left",
            "check": lambda player, room: player.hitbox.left <= 6,
            "target_room": "subida",
            "target_spawn": (140.0, 24.0),
        },
    ],
}

