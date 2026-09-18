from typing import Optional, Tuple
import pygame
import settings

class RoomEventLogic:
    def __init__(self, room):
        self.room = room
        self.solid_blockers = []

    def check_cleared_events(self) -> None:
        cleared = getattr(self.room.play_state, "cleared_events", None)
        if cleared is None:
            cleared = getattr(self.room, "cleared_events", set())
        
        if "boss_cultist_defeated" in cleared and self.room.map_name == "sala_future":
            if self.room.arena and self.room.arena.state not in ("cleared", "clearing", "unlocking"):
                self.room.arena = None
            self.room.enemies = []
            for elev in self.room.elevators:
                if elev.state not in ("descending", "ascending", "arriving", "arriving_open"):
                    elev.state = "open"
                    elev.image = elev.tex_open
                    elev.y = elev.start_y - elev.height
                    elev.hitbox.y = int(elev.y)

        if "survival_boss_defeated" in cleared and self.room.map_name == "sala_past":
            if "lava" in settings.SOUNDS:
                settings.SOUNDS["lava"].stop()
            if self.room.arena and self.room.arena.state not in ("cleared", "clearing", "unlocking"):
                self.room.arena = None
            self.room.enemies = []
            if getattr(self.room, "rising_hazard", None):
                self.room.rising_hazard.reset()
            self.room.rising_hazard = None
            self.room.lava_rising = False
            for saw in self.room.saw_hazards:
                saw.stop()
            for elev in self.room.elevators:
                if elev.state not in ("descending", "ascending", "arriving", "arriving_open"):
                    elev.state = "open"
                    elev.image = elev.tex_open
                    elev.y = elev.start_y - elev.height
                    elev.hitbox.y = int(elev.y)

        if "subida_cleared" in cleared and self.room.map_name in ("subida", "subida_past", "subida_future"):
            if "lava" in settings.SOUNDS:
                settings.SOUNDS["lava"].stop()
            if getattr(self.room, "rising_hazard", None):
                self.room.rising_hazard.reset()
            self.room.rising_hazard = None

        all_major_events = {"survival_boss_defeated", "boss_cultist_defeated", "subida_cleared"}
        all_cleared = all_major_events.issubset(cleared)
        if self.room.map_name == "middle":
            for elev in self.room.elevators:
                if "middle_elevator_unlocked" in cleared:
                    if elev.state not in ("ascending", "arriving", "arriving_open"):
                        elev.state = "open"
                        elev.image = elev.tex_open
                        elev.y = elev.start_y - elev.height
                        elev.hitbox.y = int(elev.y)
                elif all_cleared:
                    if elev.state in ("hidden", "hidden_permanently"):
                        elev.activate()
                        cleared.add("middle_elevator_unlocked")
                        if self.room.play_state:
                            self.room.play_state.cleared_events.add("middle_elevator_unlocked")
                    elif elev.state not in ("descending", "ascending", "arriving", "arriving_open"):
                        elev.state = "open"
                        elev.image = elev.tex_open
                        elev.y = elev.start_y - elev.height
                        elev.hitbox.y = int(elev.y)
                else:
                    elev.state = "hidden"

        self.solid_blockers = []
        for layer in self.room.map_data.get("layers", []):
            if layer.get("type") == "objectgroup":
                for obj in layer.get("objects", []):
                    props = self.room._parse_props(obj)
                    obj_name = str(obj.get("name", "")).lower()
                    obj_type = str(obj.get("type", "")).lower()
                    req_event = props.get("requires_event", props.get("event"))

                    if req_event or "block" in obj_name or "block" in obj_type or "door" in obj_name or "door" in obj_type:
                        if not req_event:
                            continue

                        if "col" in props or "column" in props:
                            c = int(props.get("col", props.get("column", 0)))
                            r = int(props.get("row", 0))
                            count = int(props.get("count", 1))
                            axis = str(props.get("axis", "vertical")).lower()
                            if axis == "vertical":
                                start_col, end_col = c, c
                                start_row, end_row = r, r + count - 1
                            else:
                                start_col, end_col = c, c + count - 1
                                start_row, end_row = r, r
                            ox = float(start_col * self.room.TILE_SIZE)
                            oy = float(start_row * self.room.TILE_SIZE)
                            ow = float((end_col - start_col + 1) * self.room.TILE_SIZE)
                            oh = float((end_row - start_row + 1) * self.room.TILE_SIZE)
                        else:
                            ox = float(obj.get("x", 0.0))
                            oy = float(obj.get("y", 0.0))
                            ow = max(1.0, float(obj.get("width", 16.0)))
                            oh = max(1.0, float(obj.get("height", 16.0)))
                            start_col = int(ox // self.room.TILE_SIZE)
                            end_col = int((ox + ow - 1) // self.room.TILE_SIZE)
                            start_row = int(oy // self.room.TILE_SIZE)
                            end_row = int((oy + oh - 1) // self.room.TILE_SIZE)

                        is_event_cleared = (
                            req_event in cleared
                            or (req_event in ("all_events", "all_bosses_defeated", "all_cleared") and all_cleared)
                        )
                        if is_event_cleared:
                            for row_idx in range(start_row, end_row + 1):
                                for col_idx in range(start_col, end_col + 1):
                                    if 0 <= row_idx < self.room.MAP_ROWS and 0 <= col_idx < self.room.MAP_COLS:
                                        self.room.tilemap.set_gid("ground", row_idx, col_idx, 0)
                                        self.room.tilemap.set_gid("red_ground", row_idx, col_idx, 0)
                                        self.room.tilemap.set_gid("green_ground", row_idx, col_idx, 0)
                        else:
                            blocker_rect = pygame.Rect(int(ox), int(oy), int(ow), int(oh))
                            if not any(s == blocker_rect for s in self.solid_blockers):
                                self.solid_blockers.append(blocker_rect)

    def check_room_exits(self) -> Optional[Tuple[str, float, float]]:
        if self.room.arena and self.room.arena.is_locked(): return None
        if self.room.player.state_name == "unlock": return None
        if not getattr(self.room.player, "active", True): return None
        if getattr(self.room.player, "hidden", False): return None
        
        from src.world.room_connections import ROOM_CONNECTIONS
        for exit_def in ROOM_CONNECTIONS.get(self.room.map_name, []):
            if exit_def["check"](self.room.player, self.room):
                return exit_def["target_room"], float(exit_def["target_spawn"][0]), float(exit_def["target_spawn"][1])
        return None

