import time
from typing import List, Union
from fastapi import FastAPI
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware

# --- Import our new Multi-Link Environment and Agent ---
from beam_environment import MultiBeamEnvironment2D
from q_learning_agent import MultiLinkQLearningAgent
from sarsa_agent import MultiLinkSarsaAgent
from double_q_agent import MultiLinkDoubleQLearningAgent
from expected_sarsa_agent import MultiLinkExpectedSarsaAgent

app = FastAPI()

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

#  Pydantic Models for API Data Structure 

class Position(BaseModel):
    x: float
    y: float

class Link(BaseModel):
    tx_position: Position
    rx_position: Position

class OptimizationRequest(BaseModel):
    links: List[Link]
    algorithm_type: str = Field(default="q_learning", description="Type of RL algorithm to use")

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
    algorithm_type: str

#  API Endpoint 
@app.post("/optimize", response_model=OptimizationResult)
async def optimize_beams(request: OptimizationRequest):
    try:
        print(f"Received request for {len(request.links)} links using {request.algorithm_type}.")
        start_time = time.time()

        # Extract link data from the request
        links_data = [
            {'tx_pos': (link.tx_position.x, link.tx_position.y), 'rx_pos': (link.rx_position.x, link.rx_position.y)}
            for link in request.links
        ]

        # Initialize the environment
        env = MultiBeamEnvironment2D(links=links_data, num_steps=36)
        
        # Initialize the appropriate agent based on algorithm_type
        if request.algorithm_type == "q_learning":
            agent = MultiLinkQLearningAgent(env, alpha=0.1, gamma=0.9, epsilon=0.1)
        elif request.algorithm_type == "sarsa":
            agent = MultiLinkSarsaAgent(env, alpha=0.1, gamma=0.9, epsilon=0.1)
        elif request.algorithm_type == "double_q":
            agent = MultiLinkDoubleQLearningAgent(env, alpha=0.1, gamma=0.9, epsilon=0.1)
        elif request.algorithm_type == "expected_sarsa":
            agent = MultiLinkExpectedSarsaAgent(env, alpha=0.1, gamma=0.9, epsilon=0.1)
        else:
            raise ValueError(f"Unknown algorithm type: {request.algorithm_type}")

        print(f"Training {request.algorithm_type} agent...")
        # The agent now returns a list of results and the total capacity
        results, total_capacity = agent.train(episodes=2000)
        end_time = time.time()
        training_time = end_time - start_time
        print(f"Training finished in {training_time:.2f} seconds.")

        return OptimizationResult(
            success=True,
            message=f"{len(request.links)}-Link Optimization completed successfully using {request.algorithm_type}!",
            total_capacity=total_capacity,
            results=results,
            training_time=training_time,
            algorithm_type=request.algorithm_type,
        )
    except Exception as e:
        print(f"An error occurred during optimization: {e}")
        return OptimizationResult(
            success=False, 
            message=str(e), 
            total_capacity=0, 
            results=[], 
            training_time=0,
            algorithm_type=request.algorithm_type if 'request' in locals() else "unknown"
        )

@app.get("/")
def read_root():
    return {"message": "2D Beam Selection Backend is running!"}
