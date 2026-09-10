from typing import TypedDict

class WebsiteState(TypedDict):
    user_prompt: str
    generation_level: str
    plan: dict
    frontend: dict
    backend: dict
    database: dict
    review: dict