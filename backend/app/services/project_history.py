import os
import json


class ProjectHistoryService:

    def __init__(self):
        self.projects_dir = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "../../../generated_projects"
            )
        )

    def get_projects(self):

        projects = []

        if not os.path.exists(self.projects_dir):
            return projects

        for project_name in os.listdir(self.projects_dir):

            project_path = os.path.join(
                self.projects_dir,
                project_name
            )

            if not os.path.isdir(project_path):
                continue

            plan_path = os.path.join(
                project_path,
                "plan.json"
            )

            plan = {}

            if os.path.exists(plan_path):

                try:
                    with open(
                        plan_path,
                        "r",
                        encoding="utf-8"
                    ) as file:

                        plan = json.load(file)

                except Exception:
                    plan = {}

            projects.append({
                "project_name": project_name,
                "website_name": plan.get(
                    "website_name",
                    project_name
                ),
                "website_type": plan.get(
                    "website_type",
                    "Website"
                ),
                "theme": plan.get(
                    "theme",
                    ""
                ),
                "pages": plan.get(
                    "pages",
                    []
                ),
                "features": plan.get(
                    "features",
                    []
                )
            })

        return projects