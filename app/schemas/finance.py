
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


TransactionType = Literal["income", "expense"]


class TransactionCreate(BaseModel):

    transaction_type: TransactionType

    amount: int = Field(gt=0)

    category: str = Field(
        min_length=1,
        max_length=100
    )

    description: str | None = None

    transaction_date: date = Field(
        default_factory=date.today
    )


class TransactionUpdate(BaseModel):

    transaction_type: TransactionType | None = None

    amount: int | None = Field(
        default=None,
        gt=0
    )

    category: str | None = Field(
        default=None,
        min_length=1,
        max_length=100
    )

    description: str | None = None

    transaction_date: date | None = None


class TransactionResponse(BaseModel):

    id: int

    transaction_type: TransactionType

    amount: int

    category: str

    description: str | None

    transaction_date: date

    created_at: datetime

    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
