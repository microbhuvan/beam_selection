

import time
from typing import List
from fastapi import FastAPI
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware

# --- Import our 2D Environment and the updated Agent ---
from beam_environment import BeamEnvironment2D
from q_learning_agent import QLearningAgent

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Data Models ---
# We keep elevation here so the frontend doesn't break, but it will be a placeholder.
class BeamAction(BaseModel):
    azimuth: float | str
    elevation: float | str

class OptimizationResult(BaseModel):
    success: bool
    message: str
    best_capacity: float
    tx_actions: List[BeamAction]
    rx_actions: List[BeamAction]
    training_time: float

# --- API Endpoint ---
@app.post("/optimize", response_model=OptimizationResult)
async def optimize_beams():
    try:
        print("Received request to /optimize... Starting 2D optimization.")
        start_time = time.time()

        # --- Use 2D positions and the 2D Environment ---
        tx_position = (0, 0)
        rx_position = (100, 50)

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
