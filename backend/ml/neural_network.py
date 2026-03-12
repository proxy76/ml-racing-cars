import torch
import numpy as np

class NeuralNetwork:
    def __init__(self, layer_sizes: list[int]):
        self.layer_sizes = layer_sizes
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        self.weights = []
        self.biases = []

        for i in range(len(layer_sizes) - 1):
            input_size = layer_sizes[i]
            output_size = layer_sizes[i+1]

            w = torch.randn(output_size, input_size, device=self.device) * np.sqrt(2.0 / input_size)
            b = torch.zeros(output_size, device=self.device)
            
            self.weights.append(w)
            self.biases.append(b)
        
    def predict(self, inputs: np.ndarray | torch.Tensor) -> np.ndarray:
        if isinstance(inputs, np.ndarray):
            current = torch.from_numpy(inputs).float().to(self.device)
        else:
            current = inputs.to(self.device)

        is_single = current.ndim == 1
        if is_single:
            current = current.unsqueeze(0)

        with torch.no_grad():
            for i in range(len(self.weights)):
                current = torch.mm(current, self.weights[i].t()) + self.biases[i]
                current = torch.tanh(current)
        
        # Convert back to numpy
        res = current.cpu().numpy()
        return res[0] if is_single else res

    def to_genome(self) -> np.ndarray:
        parts = []
        for w, b in zip(self.weights, self.biases):
            parts.append(w.detach().cpu().numpy().flatten())
            parts.append(b.detach().cpu().numpy().flatten())

        return np.concatenate(parts)

    @classmethod
    def from_genome(cls, genome: np.ndarray, layer_sizes: list[int]) -> 'NeuralNetwork':
        nn = cls.__new__(cls)
        nn.layer_sizes = layer_sizes
        nn.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        nn.weights = []
        nn.biases = []

        offset = 0
        genome_torch = torch.from_numpy(genome).float().to(nn.device)

        for i in range(len(layer_sizes) - 1):
            input_size = layer_sizes[i]
            output_size = layer_sizes[i+1]

            w_count = output_size * input_size
            w_flat = genome_torch[offset : offset + w_count]
            nn.weights.append(w_flat.reshape(output_size, input_size))
            
            offset += w_count

            b = genome_torch[offset : offset + output_size]
            nn.biases.append(b.clone())
            
            offset += output_size

        return nn

    @staticmethod
    def genome_size(layer_sizes: list[int]) -> int:
        total = 0
        for i in range(len(layer_sizes) - 1):
            total += layer_sizes[i+1] * layer_sizes[i]
            total += layer_sizes[i+1]
        
        return total