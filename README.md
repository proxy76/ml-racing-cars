# 🏎️ ML Car Racing Simulation

**Neural network cars learn to race through evolution.**

This is a machine learning simulation where AI agents learn to navigate a randomly generated or complex 2D race track. The project is split into a **Python FastAPI backend** responsible for physics and evolution algorithms (Neural Networks / Genetic Algorithms) and a **React & Vite frontend** that provides an interactive visualization of the learning progress. 
The project is curently based on only an oval track.

---

## Features

- **End-to-end Machine Learning Pipeline**: Cars learn how to drive autonomously using a primitive brain structured as a multi-layer **Neural Network** mapped to sensor inputs.
- **Genetic Algorithms**: The core learning mechanism is evolution. The system simulates generations of cars, evaluates their fitness based on distance and checkpoints reached, and breeds the next generation using crossover and mutation.
- **Real-time WebSockets Simulation**: A high-performance, asynchronous WebSocket connection (`fastapi`) stream physics and positional frames.
- **Custom 2D Physics Engine**: Math-based raycasting sensors, continuous collision detection against track walls, and acceleration/friction modeling.
- **Interactive UI**: Visualize the entire generation live in the browser, complete with real-time statistics, pausing, speeding up the time scaling, and charts tracking the AI's evolutionary progress.

---

## Tech Stack

### Backend
- **Python 3.10+**
- **FastAPI & Uvicorn**: Ultra-fast async WebSocket handling and REST endpoints. Used for the simulation and for the connection between frontend and backend.
- **PyTorch**: Deep learning backend for constructing and running the neural networks for decision-making. Used for the neural networks and for the genetic algorithms and to improve performance of previous code for the neural network.
- **NumPy**: Highly efficient vectorized math and matrix calculation for 2D geometry and raycasting sensors. 

### Frontend
- **React 19 & TypeScript**: Component-based UI rendered directly to a canvas/SVG layout.
- **Vite**: Ultra-fast build tool and development server.
- **Recharts**: For dynamically rendering progress/fitness graphs.

---

## Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/proxy76/ml-racing-cars.git
cd ml-racing-cars
```

### 2. Setup the Backend

Ensure you have Python and optionally a virtual environment set up. 

```bash
cd backend

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the simulation backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
The API and WS server will run on `http://127.0.0.1:8000`

### 3. Setup the Frontend

Open a new terminal session.

```bash
cd frontend

# Install Node modules
npm install

# Start the Vite development server
npm run dev
```

The web app will run on `http://localhost:5173`

---

## How it Works

### The Neural Network

Every car has a "brain" represented by a traditional Feedforward Neural Network implemented with **PyTorch**.

1. **Sensors (Input Layer):** Each car calculates the distance to track boundaries using ray-casting sensors pointing outwards (front, sides, diagonals).
2. **Hidden Layer:** The sensor inputs are passed to a hidden layer of neurons. The network is initialized using 'He/Kaiming' style normal distribution (`torch.randn()`) to provide a stable starting point.
3. **Actions (Output Layer):** The signals propagate through a hyperbolic tangent (`tanh`) activation function, squashing the outputs between `-1.0` and `1.0`. The 4 output neurons dictate the car's actions: Accelerate, Brake, Turn Left, and Turn Right.
4. **Genome Mapping:** The DNA of a car is a flattened 1D array of all its neural network weights and biases. To simulate the network, the 1D DNA is converted back into 2D PyTorch matrices.

### The Genetic Algorithm

The simulation learns through "survival of the fittest". Each generation spawns a population of cars (e.g., 100). The cars that travel the furthest without crashing gain the highest **Fitness**.

Once all cars crash or the time limit is reached, the next generation is bred in 4 phases:

1. **Elitism (`count = 5`):** The best 5 cars are cloned exactly as they are and injected into the next generation. This ensures the AI never forgets a successful path it just learned.
2. **Tournament Selection (`size = 5`):** To pick parents for the remaining 95 cars, the algorithm randomly grabs 5 cars. The car with the highest fitness out of those 5 is chosen as Parent A. It repeats this process to find Parent B.
3. **Crossover:** A new "Child" genome is created by combining DNA from Parent A and Parent B using a 50/50 binomial mask.
4. **Mutation:** 
   - **Rate (`0.1`):** Every single gene (weight/bias) has a 10% chance of mutating.
   - **Strength (`0.3`):** Mutated genes are tweaked by adding random Gaussian noise scaled by 0.3. This slightly alters the behavior to encourage new discoveries without entirely destroying the learned driving skills.
   - Genes are clipped between `-2.0` and `2.0` to keep weights from exploding over 1000 generations.

---

## License

This project is open-source and available under standard open source licensing. Check the `LICENSE` file for more details. 
