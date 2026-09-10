import shutil
from pathlib import Path


class TemplateService:

    def copy_react_template(self, project_name):

        root = Path(__file__).resolve().parents[3]

        template = root / "backend" / "app" / "templates" / "react"

        destination = (
            root /
            "generated_projects" /
            project_name /
            "frontend"
        )

        if destination.exists():
            shutil.rmtree(destination)

        shutil.copytree(
            template,
            destination
        )

        return destination