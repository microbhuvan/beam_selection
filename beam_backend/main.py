import time
from typing import List, Union
from fastapi import FastAPI
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware

# --- Import our 2D Environment and the updated Agent ---
from beam_environment import BeamEnvironment2D
from q_learning_agent import QLearningAgent

app = FastAPI()

# In your previous file, you had 5173, which is common for Vite.
# I'll add both 3000 (React default) and 5173 to be safe.
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- NEW: Define a model for the incoming request data ---
# This describes the JSON structure we expect from the frontend.
class Position(BaseModel):
    x: float
    y: float

class OptimizationRequest(BaseModel):
    tx_position: Position
    rx_position: Position


# --- Data Models ---
# We keep elevation here so the frontend doesn't break, but it will be a placeholder.
class BeamAction(BaseModel):
    azimuth: Union[float, str]
    elevation: Union[float, str]

class OptimizationResult(BaseModel):
    success: bool
    message: str
    best_capacity: float
    tx_actions: List[BeamAction]
    rx_actions: List[BeamAction]
    training_time: float

# --- API Endpoint ---
@app.post("/optimize", response_model=OptimizationResult)
async def optimize_beams(request: OptimizationRequest): # <<< KEY CHANGE 1: Added request parameter
    try:
        # <<< KEY CHANGE 2: Log the received data for debugging
        print(f"Received request: TX at ({request.tx_position.x}, {request.tx_position.y}), RX at ({request.rx_position.x}, {request.rx_position.y})")
        start_time = time.time()

        # <<< KEY CHANGE 3: Use positions from the request instead of hardcoded values
        tx_position = (request.tx_position.x, request.tx_position.y)
        rx_position = (request.rx_position.x, request.rx_position.y)

        env = BeamEnvironment2D(tx_pos=tx_position, rx_pos=rx_position, num_steps=36)
        agent = QLearningAgent(env, alpha=0.1, gamma=0.9, epsilon=0.1)

        print("Training agent...")
        tx_actions, rx_actions, best_capacity = agent.train(episodes=1000)
        end_time = time.time()
        training_time = end_time - start_time
        print(f"Training finished in {training_time:.2f} seconds.")

        return OptimizationResult(
            success=True,
            message="2D Optimization completed successfully using Q-Learning!",
            best_capacity=best_capacity,
            tx_actions=[BeamAction(azimuth=az, elevation=el) for az, el in tx_actions],
            rx_actions=[BeamAction(azimuth=az, elevation=el) for az, el in rx_actions],
            training_time=training_time,
        )

    except Exception as e:
        print(f"An error occurred during optimization: {e}")
        return OptimizationResult(success=False, message=str(e), best_capacity=0, tx_actions=[], rx_actions=[], training_time=0)

@app.get("/")
def read_root():
    return {"message": "2D Beam Selection Backend is running!"}
