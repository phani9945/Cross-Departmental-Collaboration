from __future__ import annotations

from backend.app.services.agents import AgentService
from backend.app.schemas import AgentProjectSchema


def test_agent_produces_valid_schema():
    agent = AgentService(temperature=0.0)
    spec = agent.create_project_spec("Create an interdisciplinary AI Ethics certificate across CS and Philosophy.")
    assert isinstance(spec, AgentProjectSchema)
    assert spec.title and isinstance(spec.title, str)
    assert spec.summary and isinstance(spec.summary, str)
    assert isinstance(spec.tasks, list)
    assert isinstance(spec.resources, list)


