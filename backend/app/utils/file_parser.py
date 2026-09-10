import re

from app.utils.code_parser import clean_code


def parse_files(response):

    files = {}

    if not response:
        return files

    pattern = re.compile(
        r"=====FILE:\s*(.*?)\s*=====\s*"
        r"(.*?)"
        r"(?:=====END_FILE=====|(?=====FILE:)|\Z)",
        re.DOTALL
    )

    matches = pattern.findall(response)

    for file_path, content in matches:

        file_path = file_path.strip()

        if not file_path:
            continue

        content = content.strip()

        # Remove markdown fences if the model still adds them
        content = clean_code(content)

        # Remove accidental END_FILE marker
        content = content.replace(
            "=====END_FILE=====",
            ""
        ).strip()

        files[file_path] = content

    return files