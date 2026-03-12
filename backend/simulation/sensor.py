import numpy as np 
from utils.math_utils import batch_line_intersection

class Sensor:
    def __init__(
        self,
        ray_count: int = 5,
        spread_angle: float = np.pi / 2, # 90 degrees
        ray_length: float = 200.0
    ):
        self.ray_count = ray_count
        self.spread_angle = spread_angle
        self.ray_length = ray_length
        
        # Precompute angle offsets
        if self.ray_count > 1:
            fractions = np.linspace(0, 1, self.ray_count)
            self.angle_offsets = -self.spread_angle / 2 + fractions * self.spread_angle
        else:
            self.angle_offsets = np.array([0.0])

    def cast(
        self,
        car_pos: np.ndarray,
        car_angle: float,
        wall_starts: np.ndarray,
        wall_ends: np.ndarray
    ) -> tuple[np.ndarray, list[dict]]:
        
        # N = self.ray_count, M = number of walls
        ray_angles = car_angle + self.angle_offsets
        
        p1 = car_pos.reshape(1, 1, 2) # (1, 1, 2)
        
        # ray direction vectors
        d1 = np.stack([np.cos(ray_angles), np.sin(ray_angles)], axis=1) * self.ray_length
        d1 = d1.reshape(self.ray_count, 1, 2) # (N, 1, 2)
        
        p2 = p1 + d1 # (N, 1, 2)
        
        p3 = wall_starts.reshape(1, -1, 2) # (1, M, 2)
        p4 = wall_ends.reshape(1, -1, 2)   # (1, M, 2)
        
        t, valid = batch_line_intersection(p1, p2, p3, p4) # t: (N, M), valid: (N, M)
        
        # Assign t=1.0 where intersection is invalid
        t = np.where(valid, t, 1.0)
        
        # Get closest valid intersection for each ray
        closest_t = np.min(t, axis=1) # (N,)
        
        # Endpoints are car_pos + direction * closest_t
        d1_squeezed = d1.reshape(self.ray_count, 2)
        endpoints = car_pos + d1_squeezed * closest_t.reshape(-1, 1)
        
        # Format endpoints for the frontend
        formatted_endpoints = [{"x": float(p[0]), "y": float(p[1])} for p in endpoints]
        
        return closest_t, formatted_endpoints