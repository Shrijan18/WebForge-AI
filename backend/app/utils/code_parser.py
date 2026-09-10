import re


def clean_code(code):

    if not code:
        return ""

    code = code.strip()

    # Remove markdown emphasis markers accidentally placed around the file.
    code = re.sub(
        r"^(?:\*\*\s*\r?\n)+",
        "",
        code
    )

    code = re.sub(
        r"(?:\r?\n\s*\*\*)+$",
        "",
        code
    ).strip()

    # Remove markdown code fences and standalone language labels.
    code = re.sub(
        r"^```(?:[a-z0-9_+-]+)?\s*",
        "",
        code,
        flags=re.IGNORECASE
    )

    code = re.sub(
        r"^(?:css|jsx|javascript|js|react)\s*\r?\n",
        "",
        code,
        flags=re.IGNORECASE
    )

    code = re.sub(
        r"\s*```$",
        "",
        code
    )

    code = re.sub(
        r"(?:\r?\n\s*\*\*)+$",
        "",
        code
    ).strip()

    # Remove accidental file terminator
    code = code.replace(
        "=====END_FILE=====",
        ""
    )

    return code.strip()