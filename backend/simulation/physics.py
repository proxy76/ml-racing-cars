import numpy as np
from utils.math_utils import batch_line_intersection, line_intersection

def check_wall_collision(car, wall_starts: np.ndarray, wall_ends: np.ndarray) -> bool:
    corners = car.get_corners()  # [FL, FR, BR, BL]
    
    car_starts = np.array([corners[0], corners[1], corners[2], corners[3]]) # (4, 2)
    car_ends = np.array([corners[1], corners[2], corners[3], corners[0]])   # (4, 2)
    
    p1 = car_starts.reshape(4, 1, 2)
    p2 = car_ends.reshape(4, 1, 2)
    
    p3 = wall_starts.reshape(1, -1, 2)
    p4 = wall_ends.reshape(1, -1, 2)
    
    _, valid = batch_line_intersection(p1, p2, p3, p4)
    
    return bool(np.any(valid))


def check_checkpoint(car, checkpoints: list[tuple[np.ndarray, np.ndarray]]) -> bool:
  
    if len(checkpoints) == 0:
        return False

    cp_index = car.next_checkpoint
    cp_start, cp_end = checkpoints[cp_index]

    forward = np.array([np.cos(car.angle), np.sin(car.angle)])
    movement_start = car.pos - forward * 15 
    movement_end = car.pos + forward * 15

    result = line_intersection(movement_start, movement_end, cp_start, cp_end)

    if result is not None:
        car.checkpoints_passed += 1
        car.next_checkpoint = (cp_index + 1) % len(checkpoints) 
        return True

    return False
