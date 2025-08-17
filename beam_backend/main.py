import time
from typing import List, Union
from fastapi import FastAPI
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware

# --- Import our new Multi-Link Environment and Agent ---
from beam_environment import MultiBeamEnvironment2D
from q_learning_agent import MultiLinkQLearningAgent

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

# --- Pydantic Models for API Data Structure ---

class Position(BaseModel):
    x: float
    y: float

class Link(BaseModel):
    tx_position: Position
    rx_position: Position

class OptimizationRequest(BaseModel):
    links: List[Link]

class BeamAction(BaseModel):
    azimuth: Union[float, str]
    elevation: Union[float, str]

class LinkResult(BaseModel):
    capacity: float
    tx_action: BeamAction

class OptimizationResult(BaseModel):
    success: bool
    message: str
    total_capacity: float
    results: List[LinkResult]
    training_time: float

# --- API Endpoint ---
@app.post("/optimize", response_model=OptimizationResult)
async def optimize_beams(request: OptimizationRequest):
    try:
        print(f"Received request for {len(request.links)} links.")
        start_time = time.time()

        # Extract link data from the request
        links_data = [
            {'tx_pos': (link.tx_position.x, link.tx_position.y), 'rx_pos': (link.rx_position.x, link.rx_position.y)}
            for link in request.links
        ]

        # Initialize the new environment and agent
        env = MultiBeamEnvironment2D(links=links_data, num_steps=36)
        agent = MultiLinkQLearningAgent(env, alpha=0.1, gamma=0.9, epsilon=0.1)

        print("Training agent...")
        # The agent now returns a list of results and the total capacity
        results, total_capacity = agent.train(episodes=2000)
        end_time = time.time()
        training_time = end_time - start_time
        print(f"Training finished in {training_time:.2f} seconds.")

        return OptimizationResult(
            success=True,
            message=f"{len(request.links)}-Link Optimization completed successfully!",
            total_capacity=total_capacity,
            results=results,
            training_time=training_time,
        )
    except Exception as e:
        print(f"An error occurred during optimization: {e}")
        return OptimizationResult(success=False, message=str(e), total_capacity=0, results=[], training_time=0)

@app.get("/")
def read_root():
    return {"message": "2D Beam Selection Backend is running!"}
