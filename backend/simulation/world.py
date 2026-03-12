import numpy as np
from simulation.car import Car
from simulation.track import Track
from simulation.sensor import Sensor
from simulation.physics import check_wall_collision, check_checkpoint
from ml.neural_network import NeuralNetwork
from ml.genetic_algorithm import GeneticAlgorithm
from ml.fitness import calculate_fitness

class World:
    LAYER_SIZES = [5, 6, 2]
    MAX_STEPS = 2000

    def __init__(self, pop_size: int = 100):
        self.pop_size = pop_size
        self.track = Track.generate_oval(
            center_x=500, center_y=400,
            radius_x=300, radius_y=200,
            road_width=80,
            num_segments=60,
            num_checkpoints=20
        )

        self.sensor = Sensor(ray_count=5, spread_angle=np.pi / 2, ray_length=200)

        self.ga = GeneticAlgorithm(
            population_size=pop_size,
            mutation_rate=0.1,
            mutation_strength=0.3,
            elitism_count=5,
            tournament_size=5
        )

        self.brains = [NeuralNetwork(self.LAYER_SIZES) for _ in range(pop_size)]

        self.cars = [
            Car(self.track.start_pos, self.track.start_angle)
            for _ in range(pop_size)
        ]

        self.generation = 0       # Current generation number
        self.current_step = 0     # Current step within this generation
        self.best_fitness = 0.0   # Best fitness ever seen
        self.generation_best = 0.0  # Best fitness this generation

        self._sensor_readings = [np.ones(5) for _ in range(pop_size)]
        self._sensor_endpoints = [[] for _ in range(pop_size)]

    def reset_generation(self):
        for car in self.cars:
            car.reset()
        self.current_step = 0
        self._sensor_readings = [np.ones(5) for _ in range(self.pop_size)]
        self._sensor_endpoints = [[] for _ in range(self.pop_size)]

    def step(self) -> bool:
        if self.current_step >= self.MAX_STEPS:
            return False
        
        any_alive = False
        alive_indices = []
        batch_readings = []

        # 1. Collect sensor data for all alive cars
        for i in range(self.pop_size):
            car = self.cars[i]
            if not car.alive:
                continue
            any_alive = True
            
            readings, endpoints = self.sensor.cast(
                car.pos, car.angle, self.track.wall_starts_np, self.track.wall_ends_np
            )

            self._sensor_readings[i] = readings
            self._sensor_endpoints[i] = endpoints
            
            alive_indices.append(i)
            batch_readings.append(readings)

        if not any_alive:
            return False

        
        for i, car_idx in enumerate(alive_indices):
            readings = batch_readings[i]
            output = self.brains[car_idx].predict(readings)
            
            steering = float(output[0])
            throttle = float(output[1])

            car = self.cars[car_idx]
            car.update(steering, throttle)

            if check_wall_collision(car, self.track.wall_starts_np, self.track.wall_ends_np):
                car.alive = False

            if car.alive:
                check_checkpoint(car, self.track.checkpoints)
        
        self.current_step += 1
        
        return any_alive

    def all_dead(self) -> bool:
        return not any(car.alive for car in self.cars)

    def evolve_generation(self) -> dict:
        fitnesses = []

        for car in self.cars:
            f = calculate_fitness(
                checkpoints_passed=car.checkpoints_passed,
                total_distance=car.total_distance,
                avg_speed=car.avg_speed,
                steps_alive=car.steps_alive,
                total_checkpoints=len(self.track.checkpoints),
                max_steps=self.MAX_STEPS
            )
            fitnesses.append(f)

        best_fit = max(fitnesses)
        avg_fit = sum(fitnesses) / len(fitnesses)
        worst_fit = min(fitnesses)
        best_idx = fitnesses.index(best_fit)
        best_car = self.cars[best_idx]

        if best_fit > self.best_fitness:
            self.best_fitness = best_fit
        self.generation_best = best_fit

        genomes = [brain.to_genome() for brain in self.brains]
        new_genomes = self.ga.evolve(genomes, fitnesses)
        
        self.brains = [
            NeuralNetwork.from_genome(g, self.LAYER_SIZES) for g in new_genomes
        ]

        stats = {
            "type": "generation_end",
            "generation": self.generation,
            "bestFitness": round(best_fit, 1),
            "avgFitness": round(avg_fit, 1),
            "worstFitness": round(worst_fit, 1),
            "bestCheckpoints": best_car.checkpoints_passed,
            "bestDistance": round(best_car.total_distance, 1),
            "bestStepsAlive": best_car.steps_alive,
            "allTimeBest": round(self.best_fitness, 1),
        }

        self.generation += 1
        self.reset_generation()

        return stats

    def get_frame_data(self) -> dict:
        best_idx = 0
        best_fitness_alive = -1
        
        # 1. Find the best alive car
        for i, car in enumerate(self.cars):
            if car.alive:
                f = car.checkpoints_passed * 1000 + car.total_distance * 0.1
                if f > best_fitness_alive:
                    best_fitness_alive = f
                    best_idx = i
                    
        # 2. Build the payload, only attaching sensor data to the best car
        car_data = []
        for i, car in enumerate(self.cars):
            if i == best_idx and car.alive:
                # Give the champion its lasers
                car_data.append(car.to_dict(sensor_endpoints=self._sensor_endpoints[i]))
            else:
                # Everyone else just gets basic position data
                car_data.append(car.to_dict())
                
        return {
            "type": "frame",
            "generation": self.generation,
            "step": self.current_step,
            "cars": car_data,
            "bestCarIndex": best_idx,
        }

    def get_track_data(self) -> dict:
        return self.track.to_dict()

        