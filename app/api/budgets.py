
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

from app.core.database import get_db
from app.models.budget import MonthlyBudget
from app.models.finance import FinanceTransaction
from app.schemas.budget import (
    BudgetCreate,
    BudgetUpdate,
    BudgetResponse
)


router = APIRouter(
    prefix="/api/finance",
    tags=["Finance Budget"]
)


# CREATE BUDGET
@router.post(
    "/budgets",
    response_model=BudgetResponse,
    status_code=201
)
def create_budget(
    budget_data: BudgetCreate,
    db: Session = Depends(get_db)
):

    new_budget = MonthlyBudget(
        **budget_data.model_dump()
    )

    db.add(new_budget)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Budget for this category and month already exists"
        )

    db.refresh(new_budget)

    return new_budget


# GET ALL BUDGETS
@router.get("/budgets")
def get_budgets(
    month: int,
    year: int,
    db: Session = Depends(get_db)
):

    if month < 1 or month > 12:
        raise HTTPException(
            status_code=422,
            detail="Month must be between 1 and 12"
        )

    budgets = db.query(MonthlyBudget).filter(
        MonthlyBudget.month == month,
        MonthlyBudget.year == year
    ).all()

    results = []

    for budget in budgets:

        spent = db.query(
            func.coalesce(func.sum(FinanceTransaction.amount), 0)
        ).filter(
            FinanceTransaction.transaction_type == "expense",
            FinanceTransaction.category == budget.category,
            func.extract(
                "month",
                FinanceTransaction.transaction_date
            ) == month,
            func.extract(
                "year",
                FinanceTransaction.transaction_date
            ) == year
        ).scalar()

        spent = int(spent or 0)

        remaining = budget.amount - spent

        usage_percentage = round(
            (spent / budget.amount) * 100,
            2
        )

        results.append({
            "id": budget.id,
            "category": budget.category,
            "amount": budget.amount,
            "spent": spent,
            "remaining": remaining,
            "usage_percentage": usage_percentage,
            "month": budget.month,
            "year": budget.year
        })

    return results


# UPDATE BUDGET
@router.patch(
    "/budgets/{budget_id}",
    response_model=BudgetResponse
)
def update_budget(
    budget_id: int,
    budget_data: BudgetUpdate,
    db: Session = Depends(get_db)
):

    budget = db.query(MonthlyBudget).filter(
        MonthlyBudget.id == budget_id
    ).first()

    if not budget:
        raise HTTPException(
            status_code=404,
            detail="Budget not found"
        )

    update_data = budget_data.model_dump(
        exclude_unset=True
    )

    for field in ["category", "amount"]:
        if field in update_data and update_data[field] is None:
            raise HTTPException(
                status_code=422,
                detail=f"{field} cannot be null"
            )

    for key, value in update_data.items():
        setattr(budget, key, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Budget for this category and month already exists"
        )

    db.refresh(budget)

    return budget


# DELETE BUDGET
@router.delete("/budgets/{budget_id}")
def delete_budget(
    budget_id: int,
    db: Session = Depends(get_db)
):

    budget = db.query(MonthlyBudget).filter(
        MonthlyBudget.id == budget_id
    ).first()

    if not budget:
        raise HTTPException(
            status_code=404,
            detail="Budget not found"
        )

    db.delete(budget)
    db.commit()

    return {
        "message": "Budget deleted successfully",
        "budget_id": budget_id
    }
