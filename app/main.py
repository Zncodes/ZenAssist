
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.core.database import Base, engine

# Import model agar SQLAlchemy mengenali tabel
from app.models.task import Task

from app.api.tasks import router as task_router


@asynccontextmanager
async def lifespan(app: FastAPI):

    # Create database tables
    Base.metadata.create_all(bind=engine)

    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Your Personal Life Management Assistant",
    lifespan=lifespan
)


# Register API routers
app.include_router(task_router)


@app.get("/")
async def root():

    return {
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "modules": [
            "productivity",
            "finance",
            "fitness",
            "notes",
            "ai",
            "automation"
        ]
    }


@app.get("/health")
async def health_check():

    return {
        "status": "healthy",
        "application": settings.APP_NAME
    }
