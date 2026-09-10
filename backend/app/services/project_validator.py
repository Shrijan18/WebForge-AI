import subprocess
from pathlib import Path


class ProjectValidator:

    def validate(self, project_path: Path):

        commands = [
            ("install", ["npm.cmd", "install"]),
            ("build", ["npm.cmd", "run", "build"])
        ]

        results = []

        for name, command in commands:
            try:
                result = subprocess.run(
                    command,
                    cwd=project_path,
                    capture_output=True,
                    text=True,
                    timeout=180
                )
            except subprocess.TimeoutExpired:
                return {
                    "status": "failed",
                    "step": name,
                    "output": f"{name} timed out after 180 seconds.",
                    "results": results
                }
            except OSError as error:
                return {
                    "status": "failed",
                    "step": name,
                    "output": str(error),
                    "results": results
                }

            output = "\n".join(
                value for value in (result.stdout, result.stderr) if value
            ).strip()

            results.append({
                "step": name,
                "status": "success" if result.returncode == 0 else "failed",
                "output": output
            })

            if result.returncode != 0:
                return {
                    "status": "failed",
                    "step": name,
                    "output": output,
                    "results": results
                }

        return {
            "status": "success",
            "step": "build",
            "output": results[-1]["output"],
            "results": results
        }
