import { useState } from "react";
import reactLogo from "./assets/react.svg";
import viteLogo from "/vite.svg";
import "./App.css";
import axios from "axios";

function App() {
  const [count, setCount] = useState([]);

  async function getAlgos() {
    await axios
      .get("http://localhost:8000/algos")
      .then((res) => {
        setCount(res.data);
        console.log("successfull");
      })
      .catch((err) => console.log(err));
  }

  return (
    <div>
      <h1>beam selection</h1>

      {count.map((algo, index) => {
        return (
          <div
            key={index}
            className="text-lg text-blue-600 p-2 border rounded w-fit flex flex-col gap-0.5"
          >
            {algo}
          </div>
        );
      })}

      <button onClick={getAlgos}>call algos</button>
    </div>
  );
}

export default App;
