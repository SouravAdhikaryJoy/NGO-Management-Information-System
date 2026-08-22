import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.errors import install_error_handlers
from app.api.v1 import router as v1_router
from app.config.seed import seed_defaults
from app.database import Base, SessionLocal, engine
from app.web.routes import router as web_router

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Alembic migrations are the canonical schema source; create_all + seed
    # makes dev/test bootstrapping frictionless and is a no-op on migrated DBs.
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_defaults(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="University Timetabling System",
    version="1.0.0",
    lifespan=lifespan,
)
install_error_handlers(app)
app.include_router(v1_router)
app.include_router(web_router)
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent / "web" / "static"),
    name="static",
)


@app.get("/health")
def health():
    return {"status": "ok"}
