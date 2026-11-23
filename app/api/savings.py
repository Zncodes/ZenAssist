
from math import ceil

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.database import get_db

from app.models.savings_goal import SavingsGoal
from app.models.savings_contribution import SavingsContribution

from app.schemas.savings_goal import (
    SavingsGoalCreate,
    SavingsGoalUpdate,
    SavingsContributionCreate,
    SavingsGoalResponse,
    SavingsContributionResponse
)


router = APIRouter(
    prefix="/api/finance/savings-goals",
    tags=["Savings Goals"]
)


# HELPER: CALCULATE GOAL PROGRESS
def calculate_goal_progress(
    goal: SavingsGoal,
    db: Session
):

    total_saved = db.query(
        func.coalesce(
            func.sum(SavingsContribution.amount),
            0
        )
    ).filter(
        SavingsContribution.goal_id == goal.id
    ).scalar()

    total_saved = int(total_saved or 0)

    remaining_amount = max(
        goal.target_amount - total_saved,
        0
    )

    excess_amount = max(
        total_saved - goal.target_amount,
        0
    )

    progress_percentage = round(
        (total_saved / goal.target_amount) * 100,
        2
    )

    estimated_months = None

    if (
        goal.monthly_contribution
        and remaining_amount > 0
    ):
        estimated_months = ceil(
            remaining_amount / goal.monthly_contribution
        )

    return {
        "id": goal.id,
        "name": goal.name,
        "description": goal.description,
        "target_amount": goal.target_amount,
        "total_saved": total_saved,
        "remaining_amount": remaining_amount,
        "excess_amount": excess_amount,
        "progress_percentage": progress_percentage,
        "monthly_contribution": goal.monthly_contribution,
        "estimated_months": estimated_months,
        "target_date": goal.target_date,
        "status": (
            "achieved"
            if total_saved >= goal.target_amount
            else "in_progress"
        )
    }


# CREATE SAVINGS GOAL
@router.post(
    "/",
    response_model=SavingsGoalResponse,
    status_code=201
)
def create_savings_goal(
    goal_data: SavingsGoalCreate,
    db: Session = Depends(get_db)
):

    new_goal = SavingsGoal(
        **goal_data.model_dump()
    )

    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)

    return new_goal


# GET ALL SAVINGS GOALS
@router.get("/")
def get_savings_goals(
    db: Session = Depends(get_db)
):

    goals = db.query(SavingsGoal).order_by(
        SavingsGoal.created_at.desc()
    ).all()

    return [
        calculate_goal_progress(goal, db)
        for goal in goals
    ]


# GET SAVINGS GOAL BY ID
@router.get("/{goal_id}")
def get_savings_goal(
    goal_id: int,
    db: Session = Depends(get_db)
):

    goal = db.query(SavingsGoal).filter(
        SavingsGoal.id == goal_id
    ).first()

    if not goal:
        raise HTTPException(
            status_code=404,
            detail="Savings goal not found"
        )

    return calculate_goal_progress(goal, db)


# UPDATE SAVINGS GOAL
@router.patch(
    "/{goal_id}",
    response_model=SavingsGoalResponse
)
def update_savings_goal(
    goal_id: int,
    goal_data: SavingsGoalUpdate,
    db: Session = Depends(get_db)
):

    goal = db.query(SavingsGoal).filter(
        SavingsGoal.id == goal_id
    ).first()

    if not goal:
        raise HTTPException(
            status_code=404,
            detail="Savings goal not found"
        )

    update_data = goal_data.model_dump(
        exclude_unset=True
    )

    for field in ["name", "target_amount"]:
        if field in update_data and update_data[field] is None:
            raise HTTPException(
                status_code=422,
                detail=f"{field} cannot be null"
            )

    for key, value in update_data.items():
        setattr(goal, key, value)

    db.commit()
    db.refresh(goal)

    return goal


# DELETE SAVINGS GOAL
@router.delete("/{goal_id}")
def delete_savings_goal(
    goal_id: int,
    db: Session = Depends(get_db)
):

    goal = db.query(SavingsGoal).filter(
        SavingsGoal.id == goal_id
    ).first()

    if not goal:
        raise HTTPException(
            status_code=404,
            detail="Savings goal not found"
        )

    # Delete contributions first
    db.query(SavingsContribution).filter(
        SavingsContribution.goal_id == goal_id
    ).delete(synchronize_session=False)

    db.delete(goal)
    db.commit()

    return {
        "message": "Savings goal deleted successfully",
        "goal_id": goal_id
    }


# ADD CONTRIBUTION
@router.post(
    "/{goal_id}/contributions",
    response_model=SavingsContributionResponse,
    status_code=201
)
def add_contribution(
    goal_id: int,
    contribution_data: SavingsContributionCreate,
    db: Session = Depends(get_db)
):

    goal = db.query(SavingsGoal).filter(
        SavingsGoal.id == goal_id
    ).first()

    if not goal:
        raise HTTPException(
            status_code=404,
            detail="Savings goal not found"
        )

    new_contribution = SavingsContribution(
        goal_id=goal_id,
        **contribution_data.model_dump()
    )

    db.add(new_contribution)
    db.commit()
    db.refresh(new_contribution)

    return new_contribution


# GET CONTRIBUTION HISTORY
@router.get(
    "/{goal_id}/contributions",
    response_model=list[SavingsContributionResponse]
)
def get_contributions(
    goal_id: int,
    db: Session = Depends(get_db)
):

    goal = db.query(SavingsGoal).filter(
        SavingsGoal.id == goal_id
    ).first()

    if not goal:
        raise HTTPException(
            status_code=404,
            detail="Savings goal not found"
        )

    return db.query(SavingsContribution).filter(
        SavingsContribution.goal_id == goal_id
    ).order_by(
        SavingsContribution.contribution_date.desc(),
        SavingsContribution.id.desc()
    ).all()


# DELETE CONTRIBUTION
@router.delete("/contributions/{contribution_id}")
def delete_contribution(
    contribution_id: int,
    db: Session = Depends(get_db)
):

    contribution = db.query(SavingsContribution).filter(
        SavingsContribution.id == contribution_id
    ).first()

    if not contribution:
        raise HTTPException(
            status_code=404,
            detail="Contribution not found"
        )

    db.delete(contribution)
    db.commit()

    return {
        "message": "Contribution deleted successfully",
        "contribution_id": contribution_id
    }
