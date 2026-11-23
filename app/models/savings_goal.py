
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    DateTime,
    CheckConstraint
)
from sqlalchemy.sql import func

from app.core.database import Base


class SavingsGoal(Base):

    __tablename__ = "savings_goals"

    __table_args__ = (
        CheckConstraint(
            "target_amount > 0",
            name="check_savings_target_positive"
        ),
        CheckConstraint(
            "monthly_contribution IS NULL OR monthly_contribution > 0",
            name="check_monthly_contribution_positive"
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(150),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    target_amount = Column(
        Integer,
        nullable=False
    )

    monthly_contribution = Column(
        Integer,
        nullable=True
    )

    target_date = Column(
        Date,
        nullable=True
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
