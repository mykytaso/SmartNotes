from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import init_db, close_db
from routes import note_router, version_router, analytics_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()


app = FastAPI(
    title="Notes Manager System",
    description="System to manage notes with AI features",
    lifespan=lifespan,
)

api_version_prefix = "/api/v1"

app.include_router(note_router, prefix=f"{api_version_prefix}/notes")
app.include_router(version_router, prefix=f"{api_version_prefix}/versions")
app.include_router(analytics_router, prefix=f"{api_version_prefix}/analytics")
