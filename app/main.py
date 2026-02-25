from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.database import create_tables
from app.routers import tasks, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(
    title="Task Manager API",
    description="A personal task manager REST API. Manage tasks with priorities, statuses, and due dates.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(tasks.router)
app.include_router(users.router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/status")
def status():
    return {"status": "ok", "version": app.version, "title": app.title}
