from fastapi import APIRouter

from app.services.project_history import ProjectHistoryService
from app.services.project_runner import ProjectRunner


router = APIRouter(
    prefix="/api/v1",
    tags=["Projects"]
)


history_service = ProjectHistoryService()
project_runner = ProjectRunner()


@router.get("/projects")
def get_projects():

    projects = history_service.get_projects()

    return {
        "status": "success",
        "projects": projects
    }


@router.post("/projects/{project_name}/run")
def run_project(project_name: str):

    result = project_runner.run(project_name)

    return result