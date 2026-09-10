from fastapi import APIRouter
from pydantic import BaseModel

from app.services.project_runner import ProjectRunner

router = APIRouter(
    prefix="/api/v1",
    tags=["Project Runner"]
)

runner = ProjectRunner()


class RunRequest(BaseModel):
    project_name: str


@router.post("/run")
def run_project(data: RunRequest):

    return runner.run(data.project_name)