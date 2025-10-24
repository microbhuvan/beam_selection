# Beam Selection Optimizer - Practice Implementation

This practice implementation demonstrates a multi-link beam selection optimization system using various Reinforcement Learning algorithms. Users can select different RL algorithms and compare their performance on beam selection tasks.

## 🚀 Features

- **Multiple RL Algorithms**: Choose from 4 different reinforcement learning approaches:

  - **Q-Learning**: Off-policy learning with Q-value updates
  - **SARSA**: On-policy learning using actual actions taken
  - **Double Q-Learning**: Reduces overestimation bias using two Q-tables
  - **Expected SARSA**: Uses expected value instead of maximum value

- **Interactive Frontend**: React-based web interface with:

  - Algorithm selection dropdown
  - Real-time beam visualization
  - Performance metrics display
  - Interactive transmitter/receiver positioning

- **RESTful API**: FastAPI backend with:
  - Model selection endpoints
  - Real-time optimization results
  - Training time tracking
  - Error handling

## 📁 Project Structure

```
practice/
├── beam_backend/           # FastAPI backend
│   ├── main.py            # Main API server
│   ├── beam_environment.py # Multi-link environment
│   ├── q_learning_agent.py # Q-Learning implementation
│   ├── sarsa_agent.py     # SARSA implementation
│   ├── double_q_agent.py  # Double Q-Learning implementation
│   ├── expected_sarsa_agent.py # Expected SARSA implementation
│   └── requirements.txt   # Python dependencies
├── beam_frontend/         # React frontend
│   ├── src/
│   │   ├── App.jsx        # Main application component
│   │   └── App.css        # Styling
│   ├── package.json       # Node.js dependencies
│   └── vite.config.js     # Vite configuration
├── test_algorithms.py     # Test script for all algorithms
└── README.md              # This file
```

## 🛠️ Installation & Setup

### Backend Setup

1. Navigate to the backend directory:

   ```bash
   cd practice/beam_backend
   ```

2. Create and activate virtual environment:

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the backend server:
   ```bash
   python main.py
   ```
   The API will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:

   ```bash
   cd practice/beam_frontend
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```
   The frontend will be available at `http://localhost:5173`

## 🎯 Usage

1. **Open the Application**: Navigate to `http://localhost:5173` in your browser

2. **Select Algorithm**: Use the dropdown to choose your preferred RL algorithm:

   - Q-Learning (default)
   - SARSA
   - Double Q-Learning
   - Expected SARSA

3. **Configure Links**: Set transmitter and receiver positions for up to 2 links:

   - TX1/RX1: First communication link
   - TX2/RX2: Second communication link

4. **Run Optimization**: Click the "Run [ALGORITHM] Optimization" button

5. **View Results**: The system will display:
   - Total system capacity
   - Individual link capacities
   - Optimal beam angles
   - Training time
   - Visual beam representation

## 🧪 Testing

Run the comprehensive test suite to verify all algorithms work correctly:

```bash
cd practice
python test_algorithms.py
```

This will test all 4 RL algorithms and provide a summary of their performance.

## 🔬 Algorithm Details

### Q-Learning

- **Type**: Off-policy
- **Update**: Uses maximum Q-value of next state
- **Advantage**: Can learn optimal policy while following exploratory policy
- **Use Case**: General-purpose optimization

### SARSA

- **Type**: On-policy
- **Update**: Uses actual action taken in next state
- **Advantage**: More conservative, learns the policy it follows
- **Use Case**: When exploration is costly or dangerous

### Double Q-Learning

- **Type**: Off-policy with bias reduction
- **Update**: Uses two Q-tables to reduce overestimation
- **Advantage**: More stable learning, less prone to overestimation
- **Use Case**: When Q-values tend to be overestimated

### Expected SARSA

- **Type**: On-policy with expectation
- **Update**: Uses expected value over all possible actions
- **Advantage**: Reduces variance compared to SARSA
- **Use Case**: When you want on-policy learning with lower variance

## 📊 Performance Comparison

Different algorithms may perform better in different scenarios:

- **Q-Learning**: Often fastest convergence, good for exploration
- **SARSA**: More conservative, better for safety-critical applications
- **Double Q-Learning**: Most stable, best for complex environments
- **Expected SARSA**: Balanced approach with lower variance

## 🔧 API Reference

### POST /optimize

Optimize beam selection using the specified RL algorithm.

**Request Body:**

```json
{
  "links": [
    {
      "tx_position": { "x": 0, "y": 25 },
      "rx_position": { "x": 100, "y": 25 }
    },
    {
      "tx_position": { "x": 0, "y": 75 },
      "rx_position": { "x": 100, "y": 75 }
    }
  ],
  "algorithm_type": "q_learning"
}
```

**Response:**

```json
{
  "success": true,
  "message": "2-Link Optimization completed successfully using q_learning!",
  "total_capacity": 3.4567,
  "results": [
    {
      "capacity": 1.789,
      "tx_action": { "azimuth": 32.5, "elevation": "N/A" }
    },
    {
      "capacity": 1.667,
      "tx_action": { "azimuth": -15.0, "elevation": "N/A" }
    }
  ],
  "training_time": 1.23,
  "algorithm_type": "q_learning"
}
```

## 🐛 Troubleshooting

### Common Issues

1. **Backend won't start**: Check if port 8000 is available
2. **Frontend won't connect**: Ensure backend is running on localhost:8000
3. **Import errors**: Verify all dependencies are installed
4. **Slow performance**: Reduce episode count in agent training

### Debug Mode

Enable debug logging by setting environment variables:

```bash
export DEBUG=1
python main.py
```

## 🤝 Contributing

To add new RL algorithms:

1. Create a new agent class in `beam_backend/`
2. Implement the required methods: `__init__`, `choose_action`, `update_q_table`, `train`
3. Add the algorithm to the main.py endpoint
4. Update the frontend dropdown options
5. Add tests to `test_algorithms.py`

## 📝 License

This project is for educational and research purposes. See the main project README for licensing information.
