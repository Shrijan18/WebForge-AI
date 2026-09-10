import { useState } from "react";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import axios from "axios";

import "./App.css";
import History from "./pages/History";

function Generator() {
  const [prompt, setPrompt] = useState("");
  const [generationLevel, setGenerationLevel] = useState("intermediate");
  const [generation, setGeneration] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const generateWebsite = async () => {
    if (!prompt.trim()) {
      setError("Describe the website you want to generate first.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const res = await axios.post(
        "http://127.0.0.1:8000/api/v1/generate",
        {
          prompt: prompt,
          generation_level: generationLevel,
        }
      );

      setGeneration(res.data);

    } catch (error) {

      console.error(error);
      setError(
        error.response?.data?.detail ||
        "Something went wrong while generating the website."
      );
    } finally {
      setLoading(false);
    }
  };

  const runProject = async () => {

    if (!generation?.plan) {
      setError("Generate a website first.");
      return;
    }

    try {

      const res = await axios.post(
        "http://127.0.0.1:8000/api/v1/run",
        {
          project_name: generation.plan.website_name
        }
      );

      alert(res.data.message);

    } catch (error) {

      console.error(error);
      setError("Unable to run project.");
    }
  };

  const response = generation?.plan;

  return (
    <div className="container">

      <nav>
        <Link to="/">
          Generator
        </Link>

        <Link to="/history">
          History
        </Link>
      </nav>

      <h1>🚀 WebForge AI</h1>

      <textarea
        rows="6"
        placeholder="Describe your website..."
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
      />

      <label htmlFor="generation-level">Website depth</label>
      <select
        id="generation-level"
        value={generationLevel}
        onChange={(e) => setGenerationLevel(e.target.value)}
      >
        <option value="basic">Basic: 2-3 pages and components</option>
        <option value="intermediate">Intermediate: 4-5 pages and components</option>
        <option value="advanced">Advanced: 6-7 pages and components</option>
      </select>

      <button onClick={generateWebsite}>
        {loading ? "Generating..." : "Generate Website"}
      </button>

      {error && <p className="error-message">{error}</p>}

      {generation && (
        <div className={`status status-${generation.status}`}>
          Generation status: <strong>{generation.status}</strong>
          {generation.validation && (
            <span>
              {" "}| Build: <strong>{generation.validation.status}</strong>
            </span>
          )}
        </div>
      )}

      <h3>Response</h3>

      {response && (
        <div className="response">

          <h2>{response.website_name}</h2>

          <p>
            <strong>Type:</strong>{" "}
            {response.website_type}
          </p>

          <p>
            <strong>Theme:</strong>{" "}
            {response.theme}
          </p>

          <p>
            <strong>Generation level:</strong>{" "}
            {response.generation_level}
          </p>

          <p>
            <strong>Description:</strong>{" "}
            {response.description}
          </p>

          <p>
            <strong>Database:</strong>{" "}
            {response.database ? "Yes" : "No"}
          </p>

          <p>
            <strong>Authentication:</strong>{" "}
            {response.authentication ? "Yes" : "No"}
          </p>

          <h3>Pages</h3>

          <ul>
            {response.pages?.map((page, index) => (
              <li key={index}>
                {page}
              </li>
            ))}
          </ul>

          <h3>Features</h3>

          <ul>
            {response.features?.map((feature, index) => (
              <li key={index}>
                {feature}
              </li>
            ))}
          </ul>

          {generation.review?.score !== undefined && (
            <p>
              <strong>Quality score:</strong> {generation.review.score}/100
            </p>
          )}

          {generation.errors?.length > 0 && (
            <div className="diagnostics">
              <h3>Generation issues</h3>
              <ul>
                {generation.errors.map((issue) => (
                  <li key={issue}>{issue}</li>
                ))}
              </ul>
            </div>
          )}

          <button onClick={runProject}>
            ▶ Run Website
          </button>

        </div>
      )}

    </div>
  );
}


function App() {

  return (
    <BrowserRouter>

      <Routes>

        <Route
          path="/"
          element={<Generator />}
        />

        <Route
          path="/history"
          element={<History />}
        />

      </Routes>

    </BrowserRouter>
  );
}

export default App;