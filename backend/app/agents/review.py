import json

from langchain_core.messages import HumanMessage, SystemMessage

from app.tools.llm_tool import LLMTool
from app.utils.json_parser import parse_json


REVIEW_PROMPT = """
You are a senior frontend code reviewer.

Review the generated React project against its website plan and design system.
Focus on concrete quality issues, not personal preferences.

Check:
- build and import consistency
- route and component consistency
- design-system usage through CSS variables
- responsive layout and accessibility
- domain-specific content and visual hierarchy
- repeated generic sections or placeholder content
- missing loading, empty, or error states where relevant

Return only valid JSON in this format:
{
  "score": 0,
  "strengths": [],
  "issues": [
	{
	  "severity": "high|medium|low",
	  "file": "",
	  "issue": "",
	  "recommendation": ""
	}
  ],
  "summary": ""
}
"""


class ReviewAgent:

	def __init__(self):
		self.llm = LLMTool()

	def review(self, plan, generated_files):
		source = {}
		source_size = 0

		for path, content in generated_files.items():
			remaining = 10000 - source_size
			if remaining <= 0:
				break

			excerpt = content[:min(2200, remaining)]
			source[path] = excerpt
			source_size += len(excerpt)

		response = self.llm.invoke(
			[
				SystemMessage(content=REVIEW_PROMPT),
				HumanMessage(
					content=(
						"WEBSITE PLAN\n"
						+ json.dumps(plan, separators=(",", ":"))
						+ "\n\nGENERATED SOURCE\n"
						+ json.dumps(source, separators=(",", ":"))
					)
				)
			],
			max_tokens=1400
		)

		return parse_json(response.content)
