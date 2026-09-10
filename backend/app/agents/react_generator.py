import json

from langchain_core.messages import HumanMessage, SystemMessage

from app.prompts.react_file_prompt import REACT_FILE_PROMPT
from app.tools.llm_tool import LLMTool


llm = LLMTool()


class ReactGenerator:

    MAX_CONTEXT_CHARS = 12000
    MAX_FILE_CHARS = 2600

    def generate_batch(
        self,
        plan,
        files,
        existing_files=None,
        repair_errors=None
    ):

        existing_files = existing_files or {}

        relevant_files = self._select_context_files(files, existing_files)
        existing_context = "\n\n".join(
            f"=====EXISTING_FILE:{path}=====\n"
            f"{content[:self.MAX_FILE_CHARS]}"
            for path, content in relevant_files.items()
        )
        existing_context = existing_context[:self.MAX_CONTEXT_CHARS]

        if not existing_context:
            existing_context = "(No files have been generated yet.)"

        repair_context = repair_errors or "No repair errors were reported."

        plan_context = {
            "website_name": plan.get("website_name", ""),
            "website_type": plan.get("website_type", ""),
            "description": plan.get("description", ""),
            "target_audience": plan.get("target_audience", ""),
            "primary_goal": plan.get("primary_goal", ""),
            "content_strategy": plan.get("content_strategy", []),
            "image_assets": plan.get("image_assets", []),
            "generation_level": plan.get("generation_level", "intermediate"),
            "content_depth": plan.get("content_depth", "detailed"),
            "theme": plan.get("theme", ""),
            "pages": plan.get("pages", []),
            "components": plan.get("components", []),
            "design_system": plan.get("design_system", {})
        }

        prompt = f"""
    PROJECT CONTEXT
    ===============

    {json.dumps(plan_context, separators=(",", ":"))}


    FILES TO GENERATE
    =================

    {json.dumps(files, separators=(",", ":"))}


ALREADY GENERATED SOURCE FILES
==============================

{existing_context}


VALIDATION ERRORS TO REPAIR
===========================

{repair_context}


IMPORTANT
=========

Only the files listed above exist.

Do not create any other files.

Use the exact paths provided above.

Generate every requested file.

Do not skip any file.

Reuse existing exports, imports, class names, route paths, and component APIs.
Do not replace or contradict the existing design system.
When validation errors are provided, fix them while preserving the intended design.
"""

        messages = [
            SystemMessage(content=REACT_FILE_PROMPT),
            HumanMessage(content=prompt)
        ]

        try:
            response = llm.invoke(messages, max_tokens=2800)
        except Exception as error:
            if not self._is_token_limit_error(error):
                raise

            compact_prompt = self._compact_prompt(
                plan_context,
                files,
                repair_errors
            )
            response = llm.invoke(
                [
                    SystemMessage(content=REACT_FILE_PROMPT),
                    HumanMessage(content=compact_prompt)
                ],
                max_tokens=1800
            )

        return response.content

    @staticmethod
    def _is_token_limit_error(error):
        message = str(error).lower()
        return "tokens per minute" in message or "request too large" in message

    @staticmethod
    def _compact_prompt(plan, files, repair_errors):
        return (
            "Generate only these files using the existing project conventions.\n"
            f"Plan: {json.dumps(plan, separators=(',', ':'))}\n"
            f"Files: {json.dumps(files, separators=(',', ':'))}\n"
            f"Repair errors: {str(repair_errors or '')[-3000:]}\n"
            "Return only =====FILE:path===== blocks and no explanations."
        )

    @staticmethod
    def _select_context_files(files, existing_files):
        if not existing_files:
            return {}

        requested_paths = set(files)
        selected = {}

        for path, content in existing_files.items():
            if path in {"src/App.jsx", "src/App.css", "src/index.css"}:
                selected[path] = content

        for path in existing_files:
            if path.startswith("src/components/") and path.endswith(".jsx"):
                selected[path] = existing_files[path]

        for path in requested_paths:
            selected.pop(path, None)

        return selected