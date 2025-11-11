from __future__ import annotations

import json
from typing import Any, Dict, Optional, Tuple, Callable

from pydantic import ValidationError

from ..schemas import AgentProjectSchema


class DeterministicAgent:
    """
    Minimal, deterministic stand-in using LangChain-style interfaces.
    In production, replace with a LangChain Runnable pipeline (PromptTemplate → ChatModel → parser).
    """

    def __init__(self, temperature: float = 0.0) -> None:
        self.temperature = temperature

    def _build_json(self, instruction: str) -> Dict[str, Any]:
        # Rule-based extraction for demo; replace with actual LLM call via LangChain
        title = instruction.strip().split(".")[0][:80]
        if len(title) < 10:
            title = f"Academic Program: {title}"
        summary = f"Program derived from instruction: {instruction[:200]}"
        return {
            "title": title,
            "summary": summary,
            "departments": ["Computer Science", "Biology"],
            "stakeholders": ["Department Chairs", "Program Coordinator"],
            "milestones": ["Proposal Draft", "Committee Review", "Pilot Launch"],
            "tasks": [
                {
                    "title": "Draft proposal",
                    "description": "Create initial program proposal document",
                    "assignee": "Program Coordinator",
                    "due_date": None,
                },
                {
                    "title": "Identify faculty",
                    "description": "Compile list of potential instructors",
                    "assignee": "Department Chairs",
                    "due_date": None,
                },
            ],
            "resources": [
                {"name": "University Catalog Template", "type": "document", "url": None},
                {"name": "Budget Worksheet", "type": "spreadsheet", "url": None},
            ],
        }

    def generate(self, instruction: str) -> str:
        data = self._build_json(instruction)
        return json.dumps(data, ensure_ascii=False)


def validate_or_repair_json(
    raw_json_str: str,
    repair_fn: Callable[[str, str], str],
) -> Tuple[AgentProjectSchema, Optional[str]]:
    """
    Validate agent JSON and attempt one repair using the provided repair function.
    Returns tuple of (validated schema, repair_error_message_if_any).
    """
    try:
        parsed = json.loads(raw_json_str)
        return AgentProjectSchema.model_validate(parsed), None
    except (json.JSONDecodeError, ValidationError) as e1:
        # Attempt repair once with error details
        repaired = repair_fn(raw_json_str, str(e1))
        try:
            parsed2 = json.loads(repaired)
            return AgentProjectSchema.model_validate(parsed2), None
        except (json.JSONDecodeError, ValidationError) as e2:
            return AgentProjectSchema(
                title="Invalid Output",
                summary=f"Validation failed: {e2}",
                departments=[],
                stakeholders=[],
                milestones=[],
                tasks=[],
                resources=[],
            ), f"Repair failed: {e2}"


class AgentService:
    """
    AgentService coordinates the prompt, tools, and validation/repair loop.
    The actual LLM call is abstracted to allow deterministic behavior in tests/dev.
    """

    def __init__(self, temperature: float = 0.0) -> None:
        # In a full implementation, inject LangChain components here.
        self.model = DeterministicAgent(temperature=temperature)

    def _repair(self, raw_json_str: str, error_message: str) -> str:
        # Simple repair: if not valid JSON, return an empty, valid template
        # In production, call LLM with system prompt describing the error and expected JSON schema
        try:
            json.loads(raw_json_str)
            # If JSON but schema invalid, produce a minimal valid payload
            repaired = {
                "title": "Repaired Project",
                "summary": f"Automatically repaired due to: {error_message}",
                "departments": [],
                "stakeholders": [],
                "milestones": [],
                "tasks": [],
                "resources": [],
            }
            return json.dumps(repaired)
        except json.JSONDecodeError:
            repaired = {
                "title": "Repaired Project",
                "summary": f"Automatically repaired due to: {error_message}",
                "departments": [],
                "stakeholders": [],
                "milestones": [],
                "tasks": [],
                "resources": [],
            }
            return json.dumps(repaired)

    def create_project_spec(self, instruction: str) -> AgentProjectSchema:
        raw = self.model.generate(instruction)
        validated, _ = validate_or_repair_json(raw, self._repair)
        return validated


