import React, { useState } from "react";
import "./App.css";

function App() {
  // --- NEW: State for user inputs ---
  const [txPos, setTxPos] = useState({ x: 0, y: 0 });
  const [rxPos, setRxPos] = useState({ x: 100, y: 50 });

  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handlePosChange = (setter) => (e) => {
    setter((prev) => ({
      ...prev,
      [e.target.name]: parseFloat(e.target.value) || 0,
    }));
  };

  const handleOptimize = async () => {
    console.log("Button clicked! Starting optimization process...");
    setIsLoading(true);
    setResult(null);
    setError(null);

    try {
      const response = await fetch("http://localhost:8000/optimize", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        // --- NEW: Send the coordinates in the request body ---
        body: JSON.stringify({
          tx_position: txPos,
          rx_position: rxPos,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = await response.json();
      console.log("Received data from backend:", data);
      setResult(data);
    } catch (e) {
      console.error("An error occurred:", e.message);
      setError(e.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Beam Selection Optimizer (Practice)</h1>

        {/* --- NEW: Input fields for coordinates --- */}
        <div className="input-grid">
          <div className="input-group">
            <h3>Transmitter (TX)</h3>
            <label>
              X:{" "}
              <input
                type="number"
                name="x"
                value={txPos.x}
                onChange={handlePosChange(setTxPos)}
              />
            </label>
            <label>
              Y:{" "}
              <input
                type="number"
                name="y"
                value={txPos.y}
                onChange={handlePosChange(setTxPos)}
              />
            </label>
          </div>
          <div className="input-group">
            <h3>Receiver (RX)</h3>
            <label>
              X:{" "}
              <input
                type="number"
                name="x"
                value={rxPos.x}
                onChange={handlePosChange(setRxPos)}
              />
            </label>
            <label>
              Y:{" "}
              <input
                type="number"
                name="y"
                value={rxPos.y}
                onChange={handlePosChange(setRxPos)}
              />
            </label>
          </div>
        </div>

        <button onClick={handleOptimize} disabled={isLoading}>
          {isLoading ? "Optimizing..." : "Run 2D Optimization"}
        </button>

        {result && (
          <div className="results-card">
            <h2>Optimization Results</h2>
            <p>
              <strong>Status:</strong> {result.success ? "Success" : "Failed"}
            </p>
            <p>
              <strong>Message:</strong> {result.message}
            </p>
            <p>
              <strong>Best Capacity:</strong> {result.best_capacity.toFixed(4)}{" "}
              Gbps
            </p>
            <p>
              <strong>Best TX Azimuth:</strong>{" "}
              {result.tx_actions[0].azimuth.toFixed(2)}°
            </p>
            <p>
              <strong>Training Time:</strong> {result.training_time.toFixed(2)}{" "}
              seconds
            </p>
          </div>
        )}

        {error && (
          <div className="error-card">
            <h2>An Error Occurred</h2>
            <p>{error}</p>
          </div>
        )}
      </header>
    </div>
  );
}

export default App;
