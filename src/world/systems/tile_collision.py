"""
Chrono Blight - Multi-Layer Tilemap Collision System
"""
from typing import Optional, Sequence, Tuple
from gale.tilemap import TileMap
from gale.tilemap.collision import (
    CollisionType,
    DEFAULT_COLLISION_PROPERTY,
    _overlapping_cells,
)

TILE_GID_MASK = 0x1FFFFFFF


def collision_type_in_layers(
    tilemap: TileMap,
    layers: Sequence[str],
    row: int,
    col: int,
    collision_property: str = DEFAULT_COLLISION_PROPERTY,
) -> str:
    if not tilemap.in_bounds(row, col):
        return CollisionType.NONE

    found_platform = False
    for layer_name in layers:
        gid = tilemap.get_gid(layer_name, row, col)
        if gid == 0:
            continue

        clean_gid = gid & TILE_GID_MASK
        val = tilemap.properties_of_gid(clean_gid).get(collision_property, CollisionType.NONE)

        if val == CollisionType.SOLID:
            return CollisionType.SOLID
        elif val == CollisionType.PLATFORM:
            found_platform = True

    return CollisionType.PLATFORM if found_platform else CollisionType.NONE


def _find_blocking_column_layers(
    tilemap: TileMap,
    layers: Sequence[str],
    left: float,
    top: float,
    right: float,
    bottom: float,
    collision_property: str,
    moving_right: bool,
) -> Optional[int]:
    blocking: Optional[int] = None
    for row, col in _overlapping_cells(tilemap, left, top, right, bottom):
        ctype = collision_type_in_layers(tilemap, layers, row, col, collision_property)
        if ctype != CollisionType.SOLID:
            continue

        if blocking is None or (col < blocking if moving_right else col > blocking):
            blocking = col
    return blocking


def _find_blocking_row_layers(
    tilemap: TileMap,
    layers: Sequence[str],
    original_bottom: float,
    left: float,
    top: float,
    right: float,
    bottom: float,
    collision_property: str,
    moving_down: bool,
) -> Optional[int]:
    blocking: Optional[int] = None
    for row, col in _overlapping_cells(tilemap, left, top, right, bottom):
        ctype = collision_type_in_layers(tilemap, layers, row, col, collision_property)

        if ctype == CollisionType.SOLID:
            blocks = True
        elif ctype == CollisionType.PLATFORM and moving_down:
            tile_top = row * tilemap.tile_height
            blocks = original_bottom <= (tile_top + 2.0)
        else:
            blocks = False

        if not blocks:
            continue

        if blocking is None or (row < blocking if moving_down else row > blocking):
            blocking = row
    return blocking


def move_and_collide_layers(
    tilemap: TileMap,
    layers: Sequence[str],
    x: float,
    y: float,
    width: float,
    height: float,
    dx: float,
    dy: float,
    collision_property: str = DEFAULT_COLLISION_PROPERTY,
) -> Tuple[float, float, bool, bool]:
    collided_x = False
    collided_y = False

    if dx != 0.0:
        moving_right = dx > 0.0
        new_x = x + dx
        left = min(x, new_x)
        right = max(x + width, new_x + width)

        blocking_col = _find_blocking_column_layers(
            tilemap,
            layers,
            left,
            y,
            right,
            y + height,
            collision_property,
            moving_right,
        )

        if blocking_col is not None:
            new_x = (
                blocking_col * tilemap.tile_width - width
                if moving_right
                else (blocking_col + 1) * tilemap.tile_width
            )
            collided_x = True
        x = new_x

    if dy != 0.0:
        moving_down = dy > 0.0
        new_y = y + dy
        top = min(y, new_y)
        bottom = max(y + height, new_y + height)

        blocking_row = _find_blocking_row_layers(
            tilemap,
            layers,
            y + height,
            x,
            top,
            x + width,
            bottom,
            collision_property,
            moving_down,
        )

        if blocking_row is not None:
            new_y = (
                blocking_row * tilemap.tile_height - height
                if moving_down
                else (blocking_row + 1) * tilemap.tile_height
            )
            collided_y = True
        y = new_y

    return x, y, collided_x, collided_y


def check_on_ground(
    tilemap: TileMap,
    layers: Sequence[str],
    x: float,
    y: float,
    width: float,
    height: float,
    collision_property: str = DEFAULT_COLLISION_PROPERTY,
) -> bool:
    _, _, _, collided_y = move_and_collide_layers(
        tilemap,
        layers,
        x,
        y,
        width,
        height,
        0.0,
        1.0,
        collision_property,
    )
    return collided_y