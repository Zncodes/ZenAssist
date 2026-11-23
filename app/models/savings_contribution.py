
from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    ForeignKey,
    CheckConstraint
)
from sqlalchemy.sql import func

from app.core.database import Base


class SavingsContribution(Base):

    __tablename__ = "savings_contributions"

    __table_args__ = (
        CheckConstraint(
            "amount > 0",
            name="check_contribution_amount_positive"
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    goal_id = Column(
        Integer,
        ForeignKey("savings_goals.id"),
        nullable=False,
        index=True
    )

    amount = Column(
        Integer,
        nullable=False
    )

    contribution_date = Column(
        Date,
        nullable=False
    )

    note = Column(
        String(255),
        nullable=True
    )

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )
