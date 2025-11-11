from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers.projects import router as projects_router
from .routers.crew import router as crew_router
from .models import Base
from .db import engine


def create_app() -> FastAPI:
    app = FastAPI(title="Agentic AI Collaboration Platform", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(projects_router, prefix="/projects", tags=["projects"])
    app.include_router(crew_router, prefix="/crew", tags=["crew"])

    @app.on_event("startup")
    def on_startup() -> None:
        # For demo purposes only: create tables if not exist.
        Base.metadata.create_all(bind=engine)

    return app


app = create_app()


