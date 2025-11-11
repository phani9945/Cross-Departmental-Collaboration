from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.main import create_app
from backend.app.db import get_db
from backend.app.models import Base


def get_test_app_and_db():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
    Base.metadata.create_all(bind=engine)

    def _get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app = create_app()
    app.dependency_overrides[get_db] = _get_db
    return app


def test_create_project_endpoint():
    app = get_test_app_and_db()
    client = TestClient(app)
    resp = client.post("/projects/create", json={"instruction": "Create Neuroscience and Data Science joint program."})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "project" in data
    assert "crew_job_id" in data
    assert data["project"]["title"]


