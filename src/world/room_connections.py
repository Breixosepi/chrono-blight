"""
Chrono Blight - World Room Connections & Topology
"""

from typing import Dict, List, Any, Tuple

DEFAULT_START_ROOM = "middle"
DEFAULT_START_SPAWN = (64.0, 208.0)

ROOM_CONNECTIONS: Dict[str, List[Dict[str, Any]]] = {
    "middle": [
        # Arriba a la derecha -> Esquina 1 (abajo a la izquierda)
        {
            "direction": "right_top",
            "check": lambda player, room: (
                player.hitbox.right >= room.MAP_WIDTH - 6
                and player.vx >= 0
                and player.hitbox.centery < 260
            ),
            "target_room": "esquina_1",
            "target_spawn": (32.0, 224.0),
        },
        # Abajo a la derecha -> Subida (entrada inferior izquierda)
        {
            "direction": "right_bottom",
            "check": lambda player, room: (
                player.hitbox.right >= room.MAP_WIDTH - 6
                and player.vx >= 0
                and player.hitbox.centery >= 260
            ),
            "target_room": "subida",
            "target_spawn": (32.0, 576.0),
        },
        # Arriba a la izquierda -> Left Corner (abajo a la derecha)
        {
            "direction": "left_top",
            "check": lambda player, room: (
                player.hitbox.left <= 6
                and player.vx <= 0
                and player.hitbox.centery < 260
            ),
            "target_room": "left_corner",
            "target_spawn": (352.0, 248.0),
        },
        # Abajo a la izquierda -> Abismo
        {
            "direction": "left_bottom",
            "check": lambda player, room: (
                player.hitbox.left <= 6
                and player.vx <= 0
                and player.hitbox.centery >= 260
            ),
            "target_room": "abismo_fixed",
            "target_spawn": (760.0, 104.0),
        },
        # Arriba del todo -> Big Room (abajo)
        {
            "direction": "top",
            "check": lambda player, room: (
                player.hitbox.top <= 8
                and player.vy <= 0
                and (200 <= player.hitbox.centerx <= 280)
            ),
            "target_room": "big_room",
            "target_spawn": (800.0, 220.0),
        },
    ],

    "subida": [
        # Abajo a la izquierda -> Middle (abajo a la derecha)
        {
            "direction": "left",
            "check": lambda player, room: (
                player.hitbox.left <= 6
                and player.vx <= 0
                and player.hitbox.bottom >= 550
                and (room.rising_hazard is None or room.rising_hazard.gate_current_y < 560.0)
            ),
            "target_room": "middle",
            "target_spawn": (440.0, 368.0),
        },
        # Arriba -> Esquina 1 (abajo)
        {
            "direction": "top",
            "check": lambda player, room: (
                player.hitbox.top <= 10
                and player.vy <= 0
                and (100 <= player.hitbox.centerx <= 180)
            ),
            "target_room": "esquina_1",
            "target_spawn": (200.0, 256.0),
        },
    ],

    "esquina_1": [
        # Abajo -> Subida (arriba)
        {
            "direction": "bottom",
            "check": lambda player, room: (
                player.hitbox.bottom >= room.MAP_HEIGHT - 6
                and player.vy >= 0
                and (160 <= player.hitbox.centerx <= 240)
            ),
            "target_room": "subida",
            "target_spawn": (136.0, 32.0),
        },
        # Abajo a la izquierda -> Middle (arriba a la derecha)
        {
            "direction": "left_bottom",
            "check": lambda player, room: (
                player.hitbox.left <= 6
                and player.vx <= 0
                and player.hitbox.bottom >= 160
            ),
            "target_room": "middle",
            "target_spawn": (440.0, 160.0),
        },
    ],

    "abismo_fixed": [
        # Izquierda -> Sala Pasado
        {
            "direction": "left",
            "check": lambda player, room: player.hitbox.left <= 6 and player.vx <= 0,
            "target_room": "sala_past",
            "target_spawn": (600.0, 136.0),
        },
        # Derecha -> Middle (abajo a la izquierda)
        {
            "direction": "right",
            "check": lambda player, room: player.hitbox.right >= room.MAP_WIDTH - 6 and player.vx >= 0,
            "target_room": "middle",
            "target_spawn": (40.0, 384.0),
        },
    ],

    "sala_past": [
        # Derecha -> Abismo
        {
            "direction": "right",
            "check": lambda player, room: player.hitbox.right >= room.MAP_WIDTH - 6 and player.vx >= 0,
            "target_room": "abismo_fixed",
            "target_spawn": (32.0, 104.0),
        },
    ],

    "sala_future": [
        # Izquierda -> Left Corner (arriba a la derecha)
        {
            "direction": "left",
            "check": lambda player, room: player.hitbox.left <= 6 and player.vx <= 0,
            "target_room": "left_corner",
            "target_spawn": (352.0, 88.0),
        },
    ],

    "left_corner": [
        # Abajo a la derecha -> Middle (arriba a la izquierda)
        {
            "direction": "right_bottom",
            "check": lambda player, room: (
                player.hitbox.right >= room.MAP_WIDTH - 6
                and player.vx >= 0
                and player.hitbox.centery >= 150
            ),
            "target_room": "middle",
            "target_spawn": (40.0, 200.0),
        },
        # Arriba a la derecha -> Sala Futuro (izquierda)
        {
            "direction": "right_top",
            "check": lambda player, room: (
                player.hitbox.right >= room.MAP_WIDTH - 6
                and player.vx >= 0
                and player.hitbox.centery < 150
            ),
            "target_room": "sala_future",
            "target_spawn": (40.0, 152.0),
        },
    ],

    "big_room": [
        # Abajo (fosa central) -> Middle (arriba del todo)
        {
            "direction": "bottom",
            "check": lambda player, room: (
                player.hitbox.bottom >= room.MAP_HEIGHT - 6
                and player.vy >= 0
                and (760 <= player.hitbox.centerx <= 840)
            ),
            "target_room": "middle",
            "target_spawn": (240.0, 32.0),
        },
    ],
}
