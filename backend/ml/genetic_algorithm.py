import numpy as np 

class GeneticAlgorithm:
    def __init__(
        self,
        population_size: int = 100,
        mutation_rate: float = 0.1,
        mutation_strength: float = 0.3,
        elitism_count: int = 5,
        tournament_size: int = 5
    ):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.mutation_strength = mutation_strength
        self.elitism_count = elitism_count
        self.tournament_size = tournament_size

    def evolve(
        self,
        genomes: list[np.ndarray],
        fitnesses: list[float]
    ) -> list[np.ndarray]:
        paired = sorted(
            zip(genomes, fitnesses),
            key = lambda pair: pair[1],
            reverse = True
        )

        new_generation = []

        # Elitism - keep the best
        for i in range(self.elitism_count):
            new_generation.append(paired[i][0].copy())
        
        while len(new_generation) < self.population_size:
            parent_a = self._tournament_select(paired)
            parent_b = self._tournament_select(paired)

            child = self._crossover(parent_a, parent_b)

            self._mutate(child)

            new_generation.append(child)

        return new_generation

    def _tournament_select(
        self,
        paired: list[tuple[np.ndarray, float]]
    ) -> np.ndarray:
        indices = np.random.randint(0, len(paired), size=self.tournament_size)
        best_idx = max(indices, key=lambda i: paired[i][1])
        return paired[best_idx][0].copy()

    def _crossover(self, parent_a: np.ndarray, parent_b: np.ndarray) -> np.ndarray:
        mask = np.random.random(len(parent_a)) < 0.5
        return np.where(mask, parent_a, parent_b)

    def _mutate(self, genome: np.ndarray):
        mutation_mask = np.random.random(len(genome)) < self.mutation_rate

        num_mutations = mutation_mask.sum()

        if num_mutations > 0:
            noise = np.random.randn(num_mutations) * self.mutation_strength
            genome[mutation_mask] += noise
        
        np.clip(genome, -2.0, 2.0, out=genome)