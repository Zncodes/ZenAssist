
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.core.database import Base, engine

# Database models
from app.models.task import Task
from app.models.finance import FinanceTransaction
from app.models.budget import MonthlyBudget
from app.models.savings_goal import SavingsGoal
from app.models.savings_contribution import SavingsContribution

# API routers
from app.api.tasks import router as task_router
from app.api.finance import router as finance_router
from app.api.budgets import router as budget_router
from app.api.savings import router as savings_router

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
app.include_router(finance_router)
app.include_router(budget_router)
app.include_router(savings_router)

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
