import os


class ProjectTool:

    def create_frontend(self, project_name):

        folders = [

            f"../generated_projects/{project_name}/frontend/src",

            f"../generated_projects/{project_name}/frontend/src/components",

            f"../generated_projects/{project_name}/frontend/src/pages",

            f"../generated_projects/{project_name}/frontend/src/assets",

            f"../generated_projects/{project_name}/frontend/public"
        ]

        for folder in folders:
            os.makedirs(folder, exist_ok=True)