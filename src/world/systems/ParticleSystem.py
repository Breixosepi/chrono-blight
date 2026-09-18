import random
import math
from typing import List, Dict, Any

class ParticleSystem:
    def __init__(self, map_width: float, map_height: float):
        self.map_width = map_width
        self.map_height = map_height
        
        self.ambient_particles: List[Dict[str, Any]] = [{
            "x": random.uniform(0, map_width), "y": random.uniform(0, map_height),
            "speed_y": random.uniform(-14.0, -5.0), "speed_x": random.uniform(-4.0, 4.0),
            "drift_timer": random.uniform(0.0, 6.28), "radius": random.choice([1, 1, 2]), "alpha": random.randint(85, 175)
        } for _ in range(40)]
        
        self.dust_particles: List[Dict[str, Any]] = []

    def update(self, dt: float) -> None:
        for p in self.ambient_particles:
            p["drift_timer"] += dt * 1.5
            p["y"] += p["speed_y"] * dt
            p["x"] += (p["speed_x"] + math.sin(p["drift_timer"]) * 6.0) * dt
            if p["y"] < 0: 
                p["y"] = self.map_height
                p["x"] = random.uniform(0, self.map_width)
            elif p["x"] < 0: 
                p["x"] = self.map_width
            elif p["x"] > self.map_width: 
                p["x"] = 0.0

        for d in self.dust_particles[:]:
            d["life"] -= dt
            d["x"] += d["vx"] * dt
            d["y"] += d["vy"] * dt
            if d["life"] <= 0.0: 
                self.dust_particles.remove(d)

    def spawn_dust(self, x: float, y: float, count: int = 4, color: tuple = None) -> None:
        for _ in range(count):
            self.dust_particles.append({
                "x": x + random.uniform(-5.0, 5.0), "y": y + random.uniform(-1.0, 1.0),
                "vx": random.uniform(-30.0, 30.0), "vy": random.uniform(-14.0, -4.0),
                "life": 0.22, "max_life": 0.22, "radius": random.choice([1, 2]),
                "color": color
            })

