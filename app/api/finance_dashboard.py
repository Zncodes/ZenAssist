
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db

from app.models.finance import FinanceTransaction
from app.models.budget import MonthlyBudget
from app.models.savings_goal import SavingsGoal
from app.models.savings_contribution import SavingsContribution


router = APIRouter(
    prefix="/api/finance/dashboard",
    tags=["Finance Dashboard"]
)


# HELPER: GET MONTH RANGE
def get_month_range(month: int, year: int):

    if month < 1 or month > 12:
        raise HTTPException(
            status_code=422,
            detail="Month must be between 1 and 12"
        )

    if year < 2000 or year > 2100:
        raise HTTPException(
            status_code=422,
            detail="Invalid year"
        )

    start_date = date(year, month, 1)

    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)

    return start_date, end_date


# HELPER: GET TRANSACTION TOTAL
def get_transaction_total(
    db: Session,
    transaction_type: str,
    start_date: date,
    end_date: date
):

    result = db.query(
        func.coalesce(
            func.sum(FinanceTransaction.amount),
            0
        )
    ).filter(
        FinanceTransaction.transaction_type == transaction_type,
        FinanceTransaction.transaction_date >= start_date,
        FinanceTransaction.transaction_date < end_date
    ).scalar()

    return int(result or 0)


# 1. FINANCIAL OVERVIEW
@router.get("/overview")
def get_dashboard_overview(
    month: int,
    year: int,
    db: Session = Depends(get_db)
):

    start_date, end_date = get_month_range(month, year)

    total_income = get_transaction_total(
        db, "income", start_date, end_date
    )

    total_expense = get_transaction_total(
        db, "expense", start_date, end_date
    )

    transaction_count = db.query(
        func.count(FinanceTransaction.id)
    ).filter(
        FinanceTransaction.transaction_date >= start_date,
        FinanceTransaction.transaction_date < end_date
    ).scalar()

    return {
        "period": {
            "month": month,
            "year": year
        },
        "currency": "IDR",
        "total_income": total_income,
        "total_expense": total_expense,
        "net_balance": total_income - total_expense,
        "transaction_count": int(transaction_count or 0)
    }


# 2. MONTHLY FINANCIAL TRENDS
@router.get("/trends")
def get_dashboard_trends(
    month: int,
    year: int,
    db: Session = Depends(get_db)
):

    get_month_range(month, year)

    # Generate six months, including selected month
    months = []

    current_year = year
    current_month = month

    for _ in range(5, -1, -1):

        months.append(
            (current_year, current_month)
        )

        current_month -= 1

        if current_month == 0:
            current_month = 12
            current_year -= 1

    results = []

    for item_year, item_month in months:

        start_date, end_date = get_month_range(
            item_month,
            item_year
        )

        income = get_transaction_total(
            db, "income", start_date, end_date
        )

        expense = get_transaction_total(
            db, "expense", start_date, end_date
        )

        results.append({
            "month": item_month,
            "year": item_year,
            "income": income,
            "expense": expense,
            "net_balance": income - expense
        })

    return {
        "currency": "IDR",
        "months": results
    }


# 3. EXPENSE BREAKDOWN
@router.get("/expenses")
def get_dashboard_expenses(
    month: int,
    year: int,
    db: Session = Depends(get_db)
):

    start_date, end_date = get_month_range(month, year)

    results = db.query(
        FinanceTransaction.category,
        func.sum(FinanceTransaction.amount).label("total")
    ).filter(
        FinanceTransaction.transaction_type == "expense",
        FinanceTransaction.transaction_date >= start_date,
        FinanceTransaction.transaction_date < end_date
    ).group_by(
        FinanceTransaction.category
    ).order_by(
        func.sum(FinanceTransaction.amount).desc()
    ).all()

    total_expense = sum(
        int(item.total or 0)
        for item in results
    )

    categories = []

    for item in results:

        amount = int(item.total or 0)

        percentage = (
            round(amount / total_expense * 100, 2)
            if total_expense > 0
            else 0
        )

        categories.append({
            "category": item.category,
            "amount": amount,
            "percentage": percentage
        })

    return {
        "period": {
            "month": month,
            "year": year
        },
        "total_expense": total_expense,
        "categories": categories
    }


# 4. BUDGET OVERVIEW
@router.get("/budgets")
def get_dashboard_budgets(
    month: int,
    year: int,
    db: Session = Depends(get_db)
):

    start_date, end_date = get_month_range(month, year)

    budgets = db.query(MonthlyBudget).filter(
        MonthlyBudget.month == month,
        MonthlyBudget.year == year
    ).all()

    results = []

    total_budget = 0
    total_spent = 0

    for budget in budgets:

        spent = db.query(
            func.coalesce(
                func.sum(FinanceTransaction.amount),
                0
            )
        ).filter(
            FinanceTransaction.transaction_type == "expense",
            FinanceTransaction.category == budget.category,
            FinanceTransaction.transaction_date >= start_date,
            FinanceTransaction.transaction_date < end_date
        ).scalar()

        spent = int(spent or 0)

        remaining = budget.amount - spent

        percentage = round(
            spent / budget.amount * 100,
            2
        )

        if percentage >= 100:
            status = "exceeded"
        elif percentage >= 80:
            status = "warning"
        else:
            status = "normal"

        results.append({
            "category": budget.category,
            "budget": budget.amount,
            "spent": spent,
            "remaining": remaining,
            "usage_percentage": percentage,
            "status": status
        })

        total_budget += budget.amount
        total_spent += spent

    return {
        "period": {
            "month": month,
            "year": year
        },
        "total_budget": total_budget,
        "total_spent": total_spent,
        "total_remaining": total_budget - total_spent,
        "budgets": results
    }


# 5. SAVINGS OVERVIEW
@router.get("/savings")
def get_dashboard_savings(
    db: Session = Depends(get_db)
):

    goals = db.query(SavingsGoal).order_by(
        SavingsGoal.created_at.desc()
    ).all()

    results = []

    total_target = 0
    total_saved = 0

    for goal in goals:

        saved = db.query(
            func.coalesce(
                func.sum(SavingsContribution.amount),
                0
            )
        ).filter(
            SavingsContribution.goal_id == goal.id
        ).scalar()

        saved = int(saved or 0)

        remaining = max(
            goal.target_amount - saved,
            0
        )

        progress = round(
            saved / goal.target_amount * 100,
            2
        )

        results.append({
            "id": goal.id,
            "name": goal.name,
            "target_amount": goal.target_amount,
            "total_saved": saved,
            "remaining_amount": remaining,
            "progress_percentage": progress,
            "status": (
                "achieved"
                if saved >= goal.target_amount
                else "in_progress"
            )
        })

        total_target += goal.target_amount
        total_saved += saved

    return {
        "currency": "IDR",
        "total_target": total_target,
        "total_saved": total_saved,
        "total_remaining": max(
            total_target - total_saved,
            0
        ),
        "goals_count": len(goals),
        "goals": results
    }