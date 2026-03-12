import numpy as np 

def calculate_fitness(
    checkpoints_passed: int,
    total_distance: float,
    avg_speed: float,
    steps_alive: int,
    total_checkpoints: int,
    max_steps: int 
) -> float:
    fitness = 0.0

    fitness += checkpoints_passed * 1000

    fitness += total_distance * 0.1

    fitness += avg_speed * 50
    
    if checkpoints_passed >= total_checkpoints:
        fitness += 5000

        time_ratio = 1.0 - (steps_alive / max_steps)
        fitness += time_ratio * 3000
    
    if steps_alive < 30:
        fitness *= 0.5

    return fitness