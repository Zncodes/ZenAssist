
from sqlalchemy import (
    Column,
    Integer,
    String,
    UniqueConstraint,
    CheckConstraint
)

from app.core.database import Base


class MonthlyBudget(Base):

    __tablename__ = "monthly_budgets"

    __table_args__ = (
        UniqueConstraint(
            "category",
            "month",
            "year",
            name="unique_monthly_category_budget"
        ),
        CheckConstraint(
            "amount > 0",
            name="check_budget_amount_positive"
        ),
        CheckConstraint(
            "month >= 1 AND month <= 12",
            name="check_budget_month"
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    category = Column(
        String(100),
        nullable=False
    )

    amount = Column(
        Integer,
        nullable=False
    )

    month = Column(
        Integer,
        nullable=False
    )

    year = Column(
        Integer,
        nullable=False
    )
