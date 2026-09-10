import { useEffect, useState } from "react";
import axios from "axios";
import "./History.css";

function History() {

  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(null);

  useEffect(() => {

    loadProjects();

  }, []);

  const loadProjects = async () => {

    try {

      const response = await axios.get(
        "http://127.0.0.1:8000/api/v1/projects"
      );

      setProjects(response.data.projects);

    } catch (error) {

      console.error(
        "Failed to load projects:",
        error
      );

    } finally {

      setLoading(false);

    }
  };

  const runProject = async (projectName) => {

    try {

      setRunning(projectName);

      await axios.post(
        `http://127.0.0.1:8000/api/v1/projects/${projectName}/run`
      );

    } catch (error) {

      console.error(
        "Failed to run project:",
        error
      );

    } finally {

      setRunning(null);

    }
  };

  if (loading) {

    return (
      <div className="history-container">
        <h1>Project History</h1>
        <p>Loading projects...</p>
      </div>
    );

  }

  return (

    <div className="history-container">

      <div className="history-header">

        <div>
          <h1>Project History</h1>

          <p>
            View and run your previously generated websites.
          </p>
        </div>

        <div className="project-count">
          {projects.length} Projects
        </div>

      </div>


      {projects.length === 0 ? (

        <div className="empty-history">

          <h2>No projects yet</h2>

          <p>
            Generate your first website to see it here.
          </p>

        </div>

      ) : (

        <div className="project-grid">

          {projects.map((project) => (

            <div
              className="project-card"
              key={project.project_name}
            >

              <div className="project-card-top">

                <span className="project-type">
                  {project.website_type}
                </span>

                <span className="project-theme">
                  {project.theme}
                </span>

              </div>


              <h2>
                {project.website_name}
              </h2>


              <p className="project-description">

                {project.pages.length} pages ·{" "}
                {project.features.length} features

              </p>


              <div className="project-pages">

                {project.pages
                  .slice(0, 4)
                  .map((page) => (

                    <span key={page}>
                      {page}
                    </span>

                  ))}

                {project.pages.length > 4 && (
                  <span>
                    +{project.pages.length - 4} more
                  </span>
                )}

              </div>


              <button
                className="run-button"
                onClick={() =>
                  runProject(project.project_name)
                }
                disabled={
                  running === project.project_name
                }
              >

                {running === project.project_name
                  ? "Starting..."
                  : "▶ Run Website"}

              </button>

            </div>

          ))}

        </div>

      )}

    </div>
  );
}

export default History;