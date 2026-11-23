
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class SavingsGoalCreate(BaseModel):

    name: str = Field(
        min_length=1,
        max_length=150
    )

    description: str | None = None

    target_amount: int = Field(gt=0)

    monthly_contribution: int | None = Field(
        default=None,
        gt=0
    )

    target_date: date | None = None


class SavingsGoalUpdate(BaseModel):

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150
    )

    description: str | None = None

    target_amount: int | None = Field(
        default=None,
        gt=0
    )

    monthly_contribution: int | None = Field(
        default=None,
        gt=0
    )

    target_date: date | None = None


class SavingsGoalResponse(BaseModel):

    id: int

    name: str

    description: str | None

    target_amount: int

    monthly_contribution: int | None

    target_date: date | None

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SavingsContributionCreate(BaseModel):

    amount: int = Field(gt=0)

    contribution_date: date = Field(
        default_factory=date.today
    )

    note: str | None = Field(
        default=None,
        max_length=255
    )


class SavingsContributionResponse(BaseModel):

    id: int

    goal_id: int

    amount: int

    contribution_date: date

    note: str | None

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
