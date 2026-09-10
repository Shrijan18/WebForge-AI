import json
import re


def parse_json(text: str):
    # Remove ```json
    text = re.sub(r"^```json\s*", "", text)

    # Remove ```
    text = re.sub(r"\s*```$", "", text)

    text = text.strip()

    return json.loads(text)