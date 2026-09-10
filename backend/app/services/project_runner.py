import os
import subprocess
import threading
import re


class ProjectRunner:

    def run(self, project_name):

        project_name = project_name.replace(" ", "_")

        project_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "../../../generated_projects",
                project_name,
                "frontend"
            )
        )

        print("Project Path:", project_path)

        if not os.path.exists(project_path):

            return {
                "success": False,
                "message": "Project folder not found."
            }

        if not os.path.exists(
            os.path.join(project_path, "node_modules")
        ):

            print("Installing npm packages...")

            subprocess.run(
                ["npm", "install"],
                cwd=project_path,
                shell=True
            )

        print("Starting Vite server...")

        process = subprocess.Popen(
            ["npm.cmd", "run", "dev"],
            cwd=project_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        threading.Thread(
            target=self.monitor_server,
            args=(process,),
            daemon=True
        ).start()

        return {
            "success": True,
            "message": "Website is starting..."
        }


    def monitor_server(self, process):

        for line in process.stdout:

            print(line, end="")

            # Remove ANSI terminal formatting
            clean_line = re.sub(
                r"\x1b\[[0-9;]*m",
                "",
                line
            )

            # Find localhost URL
            match = re.search(
                r"https?://localhost:\d+/?",
                clean_line
            )

            if match:

                url = match.group(0)

                print(
                    f"\nGenerated website is running at: {url}\n"
                )

                print(
                    "OPENING BROWSER:",
                    url
                )

                # Open in new browser tab
                subprocess.Popen(
                    [
                        "cmd",
                        "/c",
                        "start",
                        "",
                        url
                    ],
                    shell=False
                )

                break