# Agent Prompt Templates

System:

You are an assistant that extracts structured plans for interdisciplinary academic programs. Output only JSON with keys: title, summary, departments, stakeholders, milestones, tasks, resources. Never include prose outside JSON. Keep outputs deterministic and concise.

User (example):

Create a joint Bioinformatics minor between Computer Science and Biology focusing on data analysis, with guest lectures from the Medical School, launching in Spring. Include a draft proposal task and a resource list.

Expected JSON (example):

```json
{
  "title": "Bioinformatics Minor Program",
  "summary": "A program integrating CS and Biology for data analysis; launch Spring.",
  "departments": ["Computer Science", "Biology", "Medical School"],
  "stakeholders": ["Department Chairs", "Program Coordinator"],
  "milestones": ["Proposal Draft", "Committee Review", "Pilot Launch"],
  "tasks": [
    {"title": "Draft proposal", "description": "Create initial document", "assignee": "Program Coordinator", "due_date": null}
  ],
  "resources": [
    {"name": "University Catalog Template", "type": "document", "url": null}
  ]
}
```

How the agent reasons:
- System prompt enforces JSON-only outputs and required keys.
- Tools (stubs) exist for DB, CrewAI, notifier, resource retrieval.
- Repair loop validates with Pydantic. If invalid, a repair step asks the model (or a deterministic fallback) to return a minimal valid JSON matching the schema. Low temperature encourages deterministic outputs.


