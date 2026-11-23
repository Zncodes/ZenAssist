
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


class FinanceTransaction(Base):

    __tablename__ = "finance_transactions"

    __table_args__ = (
        CheckConstraint(
            "amount > 0",
            name="check_transaction_amount_positive"
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    transaction_type = Column(
        String(20),
        nullable=False
    )

    amount = Column(
        Integer,
        nullable=False
    )

    category = Column(
        String(100),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    transaction_date = Column(
        Date,
        nullable=False,
        index=True
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
