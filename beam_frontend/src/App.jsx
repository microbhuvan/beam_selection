import React, { useState } from "react";
import {
  Chart as ChartJS,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
} from "chart.js";
//chart.js is a js library used for making charts
//usually react compares the virtual dom to dom and then renders
//but the chart.js is made using html <canvas> element
//<canvas> element is like a digital paintboard unlike <div> which will have the children inside it
//so the react-chartjs-2 is a react wrapper around chart.js
import { Scatter } from "react-chartjs-2";
import "./App.css";

// Register the components required for a scatter plot
// this is used to draw traingular(cones) between tx and rx which represents beam
const beamConePlugin = {
  id: "beamConePlugin",
  beforeDatasetsDraw(chart, args, pluginOptions) {
    const { ctx } = chart;
    const { beamData } = pluginOptions; //gets data through chartOptions.plugins.beamConePlugin

    if (!beamData || beamData.length === 0) {
      return;
    }

    const { x, y } = chart.scales;

    //[{},{}]
    beamData.forEach((beam) => {
      const { txPos, rxPos, angle, color, beamwidth } = beam;

      //convert degree to radian
      const angleRad = (angle * Math.PI) / 180;
      const beamwidthRad = (beamwidth * Math.PI) / 180;
      //calculate the length of cone
      // by subtracting dist between tx and rx and multiplying them by 1.2
      const beamLength = Math.hypot(rxPos.x - txPos.x, rxPos.y - txPos.y) * 1.2;

      // Get pixel coordinates from data values
      const p0 = {
        x: x.getPixelForValue(txPos.x), //translates chart data to pixels for eg
        y: y.getPixelForValue(txPos.y), //{x: 0, y: 25} might be 800 pixels wide × 600 pixels tall in canvas
      };
      const p1 = {
        //left edge of cone
        x: x.getPixelForValue(
          txPos.x + beamLength * Math.cos(angleRad - beamwidthRad / 2)
        ),
        y: y.getPixelForValue(
          txPos.y + beamLength * Math.sin(angleRad - beamwidthRad / 2)
        ),
      };
      //right edge of cone
      const p2 = {
        x: x.getPixelForValue(
          txPos.x + beamLength * Math.cos(angleRad + beamwidthRad / 2)
        ),
        y: y.getPixelForValue(
          txPos.y + beamLength * Math.sin(angleRad + beamwidthRad / 2)
        ),
      };

      ctx.save();
      ctx.beginPath();
      ctx.moveTo(p0.x, p0.y);
      ctx.lineTo(p1.x, p1.y);
      ctx.lineTo(p2.x, p2.y);
      ctx.closePath();

      ctx.fillStyle = color;
      ctx.fill();
      ctx.restore();
    });
  },
};
ChartJS.register(
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
  beamConePlugin
);

function App() {
  // State for user inputs (transmitter and receiver positions)
  const [tx1Pos, setTx1Pos] = useState({ x: 0, y: 25 });
  const [rx1Pos, setRx1Pos] = useState({ x: 100, y: 25 });
  const [tx2Pos, setTx2Pos] = useState({ x: 0, y: 75 });
  const [rx2Pos, setRx2Pos] = useState({ x: 100, y: 75 });

  // State for managing the API call and its results
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // A generic handler to update position state from input fields
  // whenever the input values are changed this function is called
  // the setState is passed to this function (setter)
  // it is used as setter because all the setState can be passed here
  //e is a event React object
  //
  //so here the setter return (e)=>{} function back then we get onChange={(e)=>{}} which gets executed again
  const handlePosChange = (setter) => (e) => {
    //same as return (e)=>{}

    //curried function or function factory.
    setter((prev) => ({
      //takes in existing state as prev
      ...prev, //keeps all properties in state as it is (spread operator)
      [e.target.name]: parseFloat(e.target.value) || 0, //only change the input value typed and here the .name is x and y
    }));
  };

  // The main function to call the backend API
  const handleOptimize = async () => {
    console.log("Button clicked! Starting optimization process...");
    setIsLoading(true); //shows loading
    setResult(null); //clears last result
    setError(null); //clears error

    try {
      //sending positions to backend
      const response = await fetch("http://localhost:8000/optimize", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        //we can only send text or binary data so we stringify it
        body: JSON.stringify({
          // This is a new, API structure for multiple links
          links: [
            { tx_position: tx1Pos, rx_position: rx1Pos },
            { tx_position: tx2Pos, rx_position: rx2Pos },
          ],
        }),
      });

      //network succeeded but HTTP might be an error (400/500...)
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      //parse JSON and store it
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
        label: "Transmitter 1 (TX1)",
        data: [{ x: tx1Pos.x, y: tx1Pos.y }],
        backgroundColor: "rgba(54, 162, 235, 1)", // Blue
        pointRadius: 8,
        pointHoverRadius: 10,
        order: 2, // Draw points on top of lines
      },
      {
        label: "Receiver 1 (RX1)",
        data: [{ x: rx1Pos.x, y: rx1Pos.y }],
        backgroundColor: "rgba(255, 99, 132, 1)", // Red
        pointRadius: 8,
        pointHoverRadius: 10,
        order: 2, // Draw points on top of lines
      },
      {
        label: "Transmitter 2 (TX2)",
        data: [{ x: tx2Pos.x, y: tx2Pos.y }],
        backgroundColor: "rgba(153, 102, 255, 1)", // Purple
        pointRadius: 8,
        pointHoverRadius: 10,
        order: 2,
      },
      {
        label: "Receiver 2 (RX2)",
        data: [{ x: rx2Pos.x, y: rx2Pos.y }],
        backgroundColor: "rgba(255, 159, 64, 1)", // Orange
        pointRadius: 8,
        pointHoverRadius: 10,
        order: 2,
      },
    ],
  };

  // Configure the appearance and behavior of the chart
  const chartOptions = {
    scales: {
      x: {
        type: "linear",
        position: "bottom",
        title: { display: true, text: "X Coordinate", color: "white" },
        grid: { color: "rgba(255, 255, 255, 0.1)" },
        ticks: { color: "white" },
        min: 0,
        max: 110, // Set a fixed max, slightly larger than 100 for padding
      },
      y: {
        title: { display: true, text: "Y Coordinate", color: "white" },
        grid: { color: "rgba(255, 255, 255, 0.1)" },
        ticks: { color: "white" },
        min: 0,
        max: 110, // Set a fixed max, slightly larger than 100 for padding
      },
    },
    plugins: {
      legend: {
        labels: {
          color: "white",
        },
      },
      beamConePlugin: {
        // Options for our custom plugin
        beamData: [], // This will be populated below
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

  // If we have a successful result, prepare the data for our custom plugin
  if (result && result.success) {
    const beamwidth = 20; // The width of the beam cone in degrees

    // Data for Link 1's beam cone
    chartOptions.plugins.beamConePlugin.beamData.push({
      txPos: tx1Pos,
      rxPos: rx1Pos,
      angle: result.results[0].tx_action.azimuth,
      color: "rgba(75, 192, 192, 0.25)", // Translucent Teal
      beamwidth: beamwidth,
    });

    // Data for Link 2's beam cone
    chartOptions.plugins.beamConePlugin.beamData.push({
      txPos: tx2Pos,
      rxPos: rx2Pos,
      angle: result.results[1].tx_action.azimuth,
      color: "rgba(75, 192, 192, 0.25)", // Translucent Teal
      beamwidth: beamwidth,
    });

    // We can also add the interference paths back in as standard datasets
    chartData.datasets.push({
      type: "line",
      label: "Interference Path (TX1 -> RX2)",
      data: [
        { x: tx1Pos.x, y: tx1Pos.y },
        { x: rx2Pos.x, y: rx2Pos.y },
      ],
      borderColor: "rgba(255, 99, 132, 0.3)", // Faded Red
      borderWidth: 2,
      borderDash: [5, 5], // Make it a dashed line
      pointRadius: 0,
      order: 0, // Draw behind everything else
    });
    chartData.datasets.push({
      type: "line",
      label: "Interference Path (TX2 -> RX1)",
      data: [
        { x: tx2Pos.x, y: tx2Pos.y },
        { x: rx1Pos.x, y: rx1Pos.y },
      ],
      borderColor: "rgba(54, 162, 235, 0.3)", // Faded Blue
      borderWidth: 2,
      borderDash: [5, 5], // Make it a dashed line
      pointRadius: 0,
      order: 0, // Draw behind everything else
    });
  }

  return (
    <div className="App">
      <header className="App-header">
        <h1>Beam Selection Optimizer (Practice)</h1>

        <div className="main-content">
          <div className="controls">
            <div className="input-group">
              <h3>Transmitter 1 (TX1)</h3>
              <label>
                X:{" "}
                <input
                  type="number"
                  name="x"
                  value={tx1Pos.x}
                  onChange={handlePosChange(setTx1Pos)} //whenever input value is changed this func is called
                  //first receives (e)=>{} as return func which is executed again
                />
              </label>
              <label>
                Y:{" "}
                <input
                  type="number"
                  name="y"
                  value={tx1Pos.y}
                  onChange={handlePosChange(setTx1Pos)}
                />
              </label>
            </div>
            <div className="input-group">
              <h3>Receiver 1 (RX1)</h3>
              <label>
                X:{" "}
                <input
                  type="number"
                  name="x"
                  value={rx1Pos.x}
                  onChange={handlePosChange(setRx1Pos)}
                />
              </label>
              <label>
                Y:{" "}
                <input
                  type="number"
                  name="y"
                  value={rx1Pos.y}
                  onChange={handlePosChange(setRx1Pos)}
                />
              </label>
            </div>
            <div className="input-group">
              <h3>Transmitter 2 (TX2)</h3>
              <label>
                X:{" "}
                <input
                  type="number"
                  name="x"
                  value={tx2Pos.x}
                  onChange={handlePosChange(setTx2Pos)}
                />
              </label>
              <label>
                Y:{" "}
                <input
                  type="number"
                  name="y"
                  value={tx2Pos.y}
                  onChange={handlePosChange(setTx2Pos)}
                />
              </label>
            </div>
            <div className="input-group">
              <h3>Receiver 2 (RX2)</h3>
              <label>
                X:{" "}
                <input
                  type="number"
                  name="x"
                  value={rx2Pos.x}
                  onChange={handlePosChange(setRx2Pos)}
                />
              </label>
              <label>
                Y:{" "}
                <input
                  type="number"
                  name="y"
                  value={rx2Pos.y}
                  onChange={handlePosChange(setRx2Pos)}
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
              <strong>Total Capacity:</strong>{" "}
              {result.total_capacity.toFixed(4)} Gbps
            </p>
            <hr />
            <h4>Link 1</h4>
            <p>
              <strong>Capacity:</strong> {result.results[0].capacity.toFixed(4)}{" "}
              Gbps
            </p>
            <p>
              <strong>TX1 Azimuth:</strong>{" "}
              {result.results[0].tx_action.azimuth.toFixed(2)}°
            </p>
            <hr />
            <h4>Link 2</h4>
            <p>
              <strong>Capacity:</strong> {result.results[1].capacity.toFixed(4)}{" "}
              Gbps
            </p>
            <p>
              <strong>TX2 Azimuth:</strong>{" "}
              {result.results[1].tx_action.azimuth.toFixed(2)}°
            </p>
            <hr />
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

//HIGHER ORDER FUNCTIONS takes function as input and return a function after operating on it
/* // A function that takes another function as an argument
function applyOperation(x, y, operation) {
  return operation(x, y);
}

function add(a, b) {
  return a + b;
}

console.log(applyOperation(5, 3, add)); // 8 
// 

eg 2 

function multiplier(factor) {
  return function (x) {
    return x * factor; // return x*2
  };
}

const double = multiplier(2); gets function as return in double
console.log(double(5)); // 10 execute the double function

CURRIED FUNCTIONS
function addCurried(a) {
  return function(b) {
    return a + b;
  };
}
console.log(addCurried(2)(3)); // 5

addCurried(2)

Executes addCurried with a = 2.

Returns a function (b) => a + b.

At this moment, nothing is executed automatically — you just got a function back.

(3)

Immediately calls the function that was returned from step 1, passing b = 3.

Now it calculates 2 + 3 = 5.



json 
{
  "success": true,
  "message": "Optimized successfully",
  "total_capacity": 3.4567,
  "training_time": 1.23,
  "results": [
    { "capacity": 1.789, "tx_action": { "azimuth": 32.5 } },
    { "capacity": 1.667, "tx_action": { "azimuth": -15.0 } }
  ]
}


BEAM DATA 
{
  txPos: { x, y },
  rxPos: { x, y },
  angle: <degrees>,
  color: "rgba(...)",
  beamwidth: <degrees>
}

*/
