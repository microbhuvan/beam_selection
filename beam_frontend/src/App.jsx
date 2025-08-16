import React, { useState } from "react";
import {
  Chart as ChartJS,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
} from "chart.js";
import { Scatter } from "react-chartjs-2";
import "./App.css";

// Register the components required for a scatter plot
ChartJS.register(LinearScale, PointElement, LineElement, Tooltip, Legend);

function App() {
  // State for user inputs (transmitter and receiver positions)
  const [txPos, setTxPos] = useState({ x: 0, y: 0 });
  const [rxPos, setRxPos] = useState({ x: 100, y: 50 });

  // State for managing the API call and its results
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // A generic handler to update position state from input fields
  const handlePosChange = (setter) => (e) => {
    setter((prev) => ({
      ...prev,
      [e.target.name]: parseFloat(e.target.value) || 0,
    }));
  };

  // The main function to call the backend API
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

  // Prepare the data object for the chart
  const chartData = {
    datasets: [
      {
        label: "Transmitter (TX)",
        data: [{ x: txPos.x, y: txPos.y }],
        backgroundColor: "rgba(54, 162, 235, 1)", // Blue
        pointRadius: 8,
        pointHoverRadius: 10,
        order: 2, // Draw points on top of lines
      },
      {
        label: "Receiver (RX)",
        data: [{ x: rxPos.x, y: rxPos.y }],
        backgroundColor: "rgba(255, 99, 132, 1)", // Red
        pointRadius: 8,
        pointHoverRadius: 10,
        order: 2, // Draw points on top of lines
      },
    ],
  };

  // If we have a successful result, add the "Optimal Beam" line to the chart
  if (result && result.success) {
    const angleRad = (result.tx_actions[0].azimuth * Math.PI) / 180;
    const beamLength = Math.hypot(rxPos.x - txPos.x, rxPos.y - txPos.y) * 1.2;
    const endX = txPos.x + beamLength * Math.cos(angleRad);
    const endY = txPos.y + beamLength * Math.sin(angleRad);

    chartData.datasets.push({
      type: "line",
      label: "Optimal Beam",
      data: [
        { x: txPos.x, y: txPos.y },
        { x: endX, y: endY },
      ],
      borderColor: "rgba(75, 192, 192, 1)", // Teal
      borderWidth: 3,
      pointRadius: 0, // No points on the line itself
      order: 1, // Draw line behind the TX/RX points
    });
  }

  // Configure the appearance and behavior of the chart
  const chartOptions = {
    scales: {
      x: {
        type: "linear",
        position: "bottom",
        title: { display: true, text: "X Coordinate", color: "white" },
        grid: { color: "rgba(255, 255, 255, 0.1)" },
        ticks: { color: "white" },
      },
      y: {
        title: { display: true, text: "Y Coordinate", color: "white" },
        grid: { color: "rgba(255, 255, 255, 0.1)" },
        ticks: { color: "white" },
      },
    },
    plugins: {
      legend: {
        labels: {
          color: "white",
        },
      },
      tooltip: {
        callbacks: {
          label: function (context) {
            return ` (${context.parsed.x}, ${context.parsed.y})`;
          },
        },
      },
    },
    maintainAspectRatio: false,
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Beam Selection Optimizer (Practice)</h1>

        <div className="main-content">
          <div className="controls">
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
          <div className="chart-container">
            <Scatter options={chartOptions} data={chartData} />
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
