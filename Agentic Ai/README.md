Agentic AI Collaboration Platform — CrewAI + LangChain
======================================================

Overview
--------
This repository implements a minimal agentic AI platform to initiate and manage cross-department, interdisciplinary academic programs. It uses:
- Backend: FastAPI, SQLAlchemy, PostgreSQL
- Orchestration: CrewAI (client + webhook stubs)
- Agent logic: LangChain-style agent (deterministic fallback) with strict JSON output and repair loop
- Background tasks: Redis + RQ
- Auth: JWT skeleton and RBAC placeholders
- Frontend: Minimal React + Tailwind scaffold

Architecture
------------
ASCII diagram:

```
[React UI] --HTTP--> [FastAPI Backend]
                      | \
                      |  \--(LangChain Agent)--> JSON spec -> Pydantic validate/repair
                      |
                      \--(CrewAI Client)--> create_job/get/update
                      |
                    [Postgres] <-- SQLAlchemy models
                      |
                    [Redis/RQ] <-- background tasks (future)
```

Quick Start
-----------
1) Prereqs: Docker, Docker Compose.

2) Copy env:
- Create a `.env` at the repo root using the following keys:
  - DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/agentic
  - REDIS_URL=redis://redis:6379/0
  - OPENAI_API_KEY=
  - CREW_API_BASE=
  - CREW_API_KEY=
  - CREW_WEBHOOK_SECRET=changeme-webhook-secret
  - JWT_SECRET=changeme-jwt-secret
  - JWT_ALG=HS256
  - JWT_EXPIRE_MINUTES=480

3) Launch:
```
docker compose up --build
```
Backend at http://localhost:8000. Swagger docs at `/docs`.

Database initialization
-----------------------
For demo, this project relies on SQLAlchemy metadata creation via Alembic placeholders (not included). Use your own migrations or a quick metadata create script if needed.

Example cURL Flows
------------------
- Create project from natural language:
```
curl -X POST http://localhost:8000/projects/create \
  -H "Content-Type: application/json" \
  -d '{ "instruction": "Create a Bioinformatics minor joining CS and Biology with Spring launch." }'
```
Response includes persisted project and a simulated CrewAI job id.

- List projects:
```
curl http://localhost:8000/projects/
```

How the agent reasons
---------------------
- System prompt (see `prompts/agent_prompts.md`) instructs the model to output strict JSON with keys: `title, summary, departments, stakeholders, milestones, tasks, resources` and nothing else.
- The service validates outputs with `AgentProjectSchema`. If validation fails, a repair step generates a minimal valid JSON matching the schema.
- Low temperature fosters deterministic outputs. In this demo, a deterministic fallback agent returns structured JSON without calling a vendor LLM when API keys are absent.

Running tests
-------------
```
pip install -r requirements.txt
pytest -q
```

Frontend
--------
See `frontend/` for a minimal React + Tailwind scaffold that can call backend endpoints and render a simple dashboard with a create-project form.

Notes
-----
- Replace CrewAI client stubs in `backend/app/services/crew_client.py` with real endpoints and authentication.
- Add proper JWT issuance/verification and RBAC enforcement in production.
- Implement Alembic migrations for production use.


