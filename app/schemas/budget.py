
from pydantic import BaseModel, ConfigDict, Field


class BudgetCreate(BaseModel):

    category: str = Field(
        min_length=1,
        max_length=100
    )

    amount: int = Field(gt=0)

    month: int = Field(ge=1, le=12)

    year: int = Field(ge=2000, le=2100)


class BudgetUpdate(BaseModel):

    category: str | None = Field(
        default=None,
        min_length=1,
        max_length=100
    )

    amount: int | None = Field(
        default=None,
        gt=0
    )


class BudgetResponse(BaseModel):

    id: int

    category: str

    amount: int

    month: int

    year: int

    model_config = ConfigDict(from_attributes=True)
