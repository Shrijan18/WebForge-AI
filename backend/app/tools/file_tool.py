import os
import json


class FileTool:

    def write_file(self, path, content):

        folder = os.path.dirname(path)

        os.makedirs(folder, exist_ok=True)

        with open(path, "w", encoding="utf-8") as file:
            file.write(content)

    def write_json(self, path, data):

        folder = os.path.dirname(path)

        os.makedirs(folder, exist_ok=True)

        with open(path, "w", encoding="utf-8") as file:

            json.dump(data, file, indent=4)


def write_project(self, project_name, files):

    import os

    base = f"../generated_projects/{project_name}/frontend"

    for file in files:

        path = os.path.join(base, file["path"])

        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:

            f.write(file["content"])