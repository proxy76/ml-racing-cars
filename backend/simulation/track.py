import numpy as np
from utils.math_utils import normalize

class Track:
    def __init__(
        self,
        inner_walls: list[tuple[np.ndarray, np.ndarray]],
        outer_walls: list[tuple[np.ndarray, np.ndarray]],
        checkpoints: list[tuple[np.ndarray, np.ndarray]],
        start_pos: np.ndarray,
        start_angle: float  
    ):
        self.inner_walls = inner_walls
        self.outer_walls = outer_walls
        self.checkpoints = checkpoints
        self.start_pos = start_pos
        self.start_angle = start_angle

        self.all_walls = inner_walls + outer_walls
        self.wall_starts_np = np.array([w[0] for w in self.all_walls], dtype=np.float32)
        self.wall_ends_np = np.array([w[1] for w in self.all_walls], dtype=np.float32)

    @staticmethod
    def generate_oval(
        center_x: float = 500,
        center_y: float = 400,
        radius_x: float = 300,
        radius_y: float = 200,
        road_width: float = 80,
        num_segments: int = 60,
        num_checkpoints: int = 20
    ):
        inner_walls = []
        outer_walls = []
        half_width = road_width / 2

        inner_points = []
        outer_points = []

        for i in range(num_segments):
            angle_1 = 2 * np.pi * i / num_segments
            angle_2 = 2 * np.pi * (i+1) / num_segments
            center_1 = np.array([
                center_x + radius_x * np.cos(angle_1),
                center_y + radius_y * np.sin(angle_1)
            ])
            center_2 = np.array([
                center_x + radius_x * np.cos(angle_2),
                center_y + radius_y * np.sin(angle_2)
            ])

            normal_1 = normalize(np.array([
                np.cos(angle_1) / radius_x,
                np.sin(angle_1) / radius_y
            ]))
            normal_2 = normalize(np.array([
                np.cos(angle_2) / radius_x,
                np.sin(angle_2) / radius_y
            ]))

            inner_1 = center_1 - normal_1 * half_width
            inner_2 = center_2 - normal_2 * half_width
            outer_1 = center_1 + normal_1 * half_width
            outer_2 = center_2 + normal_2 * half_width

            inner_walls.append((inner_1, inner_2))
            outer_walls.append((outer_1, outer_2))

            inner_points.append(inner_1)
            outer_points.append(outer_1)

        checkpoints = []
        for i in range(num_checkpoints):
            idx = int(i * num_segments / num_checkpoints)
            checkpoints.append((inner_points[idx], outer_points[idx]))
        
        start_center = np.array([
            center_x + radius_x,
            center_y
        ])
        
        start_angle = -np.pi / 2

        return Track(inner_walls, outer_walls, checkpoints, start_center, start_angle)


    def to_dict(self) -> dict:
        return {
            "type": "track",
            "innerWalls": [
                {"x1": float(s[0]), "y1": float(s[1]), "x2": float(e[0]), "y2": float(e[1])}
                for s, e in self.inner_walls
            ],
            "outerWalls": [
                {"x1": float(s[0]), "y1": float(s[1]), "x2": float(e[0]), "y2": float(e[1])}
                for s, e in self.outer_walls
            ],
            "checkpoints": [
                {"x1": float(s[0]), "y1": float(s[1]), "x2": float(e[0]), "y2": float(e[1])}
                for s, e in self.checkpoints
            ],
            "startPos": {"x": float(self.start_pos[0]), "y": float(self.start_pos[1])},
            "startAngle": float(self.start_angle),
        }
        