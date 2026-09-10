class ManifestService:

    def get_batches(self, plan):

        batches = {}

        # App
        batches["layout"] = [
            "src/App.jsx",
            "src/App.css",
            "src/index.css"
        ]

        batch_number = 1

        # Components
        for component in plan.get("components", []):

            batches[f"component_{batch_number}"] = [
                f"src/components/{component}.jsx",
                f"src/components/{component}.css"
            ]

            batch_number += 1

        # Pages
        page_number = 1

        for page in plan.get("pages", []):

            page_name = page.replace(" ", "")

            batches[f"page_{page_number}"] = [
                f"src/pages/{page_name}.jsx",
                f"src/pages/{page_name}.css"
            ]

            page_number += 1

        return batches