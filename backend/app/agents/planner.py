import json

from langchain_core.messages import HumanMessage, SystemMessage

from app.prompts.planner_prompt import PLANNER_PROMPT
from app.tools.llm_tool import LLMTool
from app.utils.json_parser import parse_json
from app.config.generation_levels import (
    DEFAULT_GENERATION_LEVEL,
    GENERATION_LEVELS,
)


llm = LLMTool()


class PlannerAgent:

    def execute(self, user_prompt, generation_level=DEFAULT_GENERATION_LEVEL):

        if generation_level not in GENERATION_LEVELS:
            generation_level = DEFAULT_GENERATION_LEVEL

        level = GENERATION_LEVELS[generation_level]

        prompt = f"""
    User Website Request:

    {user_prompt}

    Generation Level: {generation_level}
    Page count: {level['pages'][0]} to {level['pages'][1]}
    Component count: {level['components'][0]} to {level['components'][1]}
    Content depth: {level['content_depth']}

    You must return generation_level as "{generation_level}".
    """

        response = llm.invoke(
            [
                SystemMessage(content=PLANNER_PROMPT),
                HumanMessage(content=prompt)
            ]
        )

        print("\n========== PLANNER RAW RESPONSE ==========")
        print(repr(response.content))
        print("==========================================\n")

        plan = parse_json(response.content)
        plan["generation_level"] = generation_level
        plan["content_depth"] = level["content_depth"]
        plan["pages"] = self._fit_items(
            plan.get("pages", []),
            level["pages"],
            ["Home", "About", "Services", "Contact", "FAQ", "Testimonials", "Gallery"]
        )
        plan["components"] = self._fit_items(
            plan.get("components", []),
            level["components"],
            ["Navbar", "Footer", "Hero", "CTA", "FeatureCard", "Newsletter", "Stats"]
        )
        return plan

    @staticmethod
    def _fit_items(items, bounds, fallback_items):
        minimum, maximum = bounds
        result = []

        for item in items or []:
            if item not in result:
                result.append(item)

        for item in fallback_items:
            if len(result) >= minimum:
                break
            if item not in result:
                result.append(item)

        return result[:maximum]