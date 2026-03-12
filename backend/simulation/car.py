"""
Each car in the simulation is controlled by two values from its neural network:
    - steering: [-1, 1] where -1 = full left, +1 = full right
    - throttle: [-1, 1] where -1 = full brake/reverse, +1 = full acceleration
"""

import numpy as np 
 
class Car:
    # Constants:
    MAX_SPEED = 8.0
    MAX_REVERSE_SPEED = 2.0
    ACCELERATION = 0.3
    TURN_RATE = 0.04
    FRICTION = 0.95
    LENGTH = 30
    WIDTH = 14

    def __init__(self, start_pos: np.ndarray, start_angle: float):
        self.pos = start_pos.astype(float).copy()
        self.angle = float(start_angle)
        self.speed = 0.0

        self.alive = True 

        self.steps_alive = 0 # how many physics steps the car survived
        self.total_distance = 0.0
        self.checkpoints_passed = 0
        self.next_checkpoint = 0
        self.speed_accumulator = 0.0

        self._start_pos = start_pos.astype(float).copy()
        self._start_angle = float(start_angle)

    def reset(self):
        self.pos = self._start_pos.copy()
        self.angle = self._start_angle
        self.speed = 0.0
        self.alive = True
        self.steps_alive = 0
        self.total_distance = 0.0
        self.checkpoints_passed = 0
        self.next_checkpoint = 0
        self.speed_accumulator = 0.0

    def update(self, steering: float, throttle: float):
        if not self.alive:
            return
        
        # Steering
        speed_factor = min(abs(self.speed) / 2.0, 1.0)
        self.angle += steering * self.TURN_RATE * speed_factor
        self.speed += throttle * self.ACCELERATION
        self.speed *= self.FRICTION
        self.speed = np.clip(self.speed, -self.MAX_REVERSE_SPEED, self.MAX_SPEED)

        if abs(self.speed) < 0.01:
            self.speed = 0.0
        
        # Movement
        dx = np.cos(self.angle) * self.speed
        dy = np.sin(self.angle) * self.speed
        self.pos[0] += dx
        self.pos[1] += dy

        distance_this_step = abs(self.speed)
        self.total_distance += distance_this_step

        self.steps_alive += 1
        self.speed_accumulator += abs(self.speed)
        
    @property
    def avg_speed(self) -> float:
        if self.steps_alive == 0:
            return 0.0
        return self.speed_accumulator / self.steps_alive


    def get_corners(self) -> list[np.ndarray]:
        forward = np.array([np.cos(self.angle), np.sin(self.angle)])
        right = np.array([np.cos(self.angle + np.pi/2), np.sin(self.angle + np.pi/2)])
        half_len = self.LENGTH / 2
        half_wid = self.WIDTH / 2
        fl = self.pos + forward * half_len - right * half_wid  # 
        fr = self.pos + forward * half_len + right * half_wid  # 
        br = self.pos - forward * half_len + right * half_wid  # 
        bl = self.pos - forward * half_len - right * half_wid  # 
        return [fl, fr, br, bl]

    def to_dict(self, sensor_endpoints: list = None) -> dict:
        data = {
            "x": float(self.pos[0]),
            "y": float(self.pos[1]),
            "angle": float(self.angle),
            "alive": self.alive,
            "fitness": float(self.checkpoints_passed * 1000 + self.total_distance * 0.1),
            "speed": float(self.speed),
        }
        
        # Only attach sensor endpoints if explicitly provided (e.g., for the best car)
        if sensor_endpoints is not None:
            data["sensorEndpoints"] = sensor_endpoints
            
        return data