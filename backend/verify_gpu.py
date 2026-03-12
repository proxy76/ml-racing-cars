import torch
import numpy as np
import time
from ml.neural_network import NeuralNetwork

def verify_gpu():
    print("--- GPU Verification ---")
    cuda_available = torch.cuda.is_available()
    print(f"CUDA Available: {cuda_available}")
    if cuda_available:
        print(f"Current Device: {torch.cuda.get_device_name(0)}")
    else:
        print("Running on CPU.")

    # Test NeuralNetwork
    layer_sizes = [5, 6, 2]
    nn = NeuralNetwork(layer_sizes)
    print(f"NN Device: {nn.device}")

    # Single predict
    dummy_input = np.random.randn(5).astype(np.float32)
    start = time.perf_counter()
    output = nn.predict(dummy_input)
    end = time.perf_counter()
    print(f"Single prediction time: {(end - start) * 1000:.4f}ms")
    print(f"Output: {output}")

    # Batch predict (100 cars)
    batch_input = np.random.randn(100, 5).astype(np.float32)
    start = time.perf_counter()
    output_batch = nn.predict(batch_input)
    end = time.perf_counter()
    print(f"Batch prediction (100) time: {(end - start) * 1000:.4f}ms")
    print(f"Batch Output Shape: {output_batch.shape}")

if __name__ == "__main__":
    verify_gpu()
