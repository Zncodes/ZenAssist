
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from sqlalchemy import func

from app.core.database import get_db
from app.models.finance import FinanceTransaction
from app.schemas.finance import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse
)


router = APIRouter(
    prefix="/api/finance",
    tags=["Finance"]
)


# CREATE TRANSACTION
@router.post(
    "/transactions",
    response_model=TransactionResponse,
    status_code=201
)
def create_transaction(
    transaction_data: TransactionCreate,
    db: Session = Depends(get_db)
):

    new_transaction = FinanceTransaction(
        **transaction_data.model_dump()
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction


# GET ALL TRANSACTIONS
@router.get(
    "/transactions",
    response_model=list[TransactionResponse]
)
def get_transactions(
    transaction_type: str | None = None,
    category: str | None = None,
    db: Session = Depends(get_db)
):

    query = db.query(FinanceTransaction)

    if transaction_type:
        if transaction_type not in ["income", "expense"]:
            raise HTTPException(
                status_code=422,
                detail="Invalid transaction type"
            )

        query = query.filter(
            FinanceTransaction.transaction_type == transaction_type
        )

    if category:
        query = query.filter(
            FinanceTransaction.category == category
        )

    return query.order_by(
        FinanceTransaction.transaction_date.desc(),
        FinanceTransaction.id.desc()
    ).all()


# GET TRANSACTION BY ID
@router.get(
    "/transactions/{transaction_id}",
    response_model=TransactionResponse
)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db)
):

    transaction = db.query(FinanceTransaction).filter(
        FinanceTransaction.id == transaction_id
    ).first()

    if not transaction:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    return transaction


# UPDATE TRANSACTION
@router.patch(
    "/transactions/{transaction_id}",
    response_model=TransactionResponse
)
def update_transaction(
    transaction_id: int,
    transaction_data: TransactionUpdate,
    db: Session = Depends(get_db)
):

    transaction = db.query(FinanceTransaction).filter(
        FinanceTransaction.id == transaction_id
    ).first()

    if not transaction:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    update_data = transaction_data.model_dump(
        exclude_unset=True
    )

    for required_field in [
        "transaction_type",
        "amount",
        "category",
        "transaction_date"
    ]:

        if (
            required_field in update_data
            and update_data[required_field] is None
        ):
            raise HTTPException(
                status_code=422,
                detail=f"{required_field} cannot be null"
            )

    for key, value in update_data.items():
        setattr(transaction, key, value)

    db.commit()
    db.refresh(transaction)

    return transaction


# DELETE TRANSACTION
@router.delete("/transactions/{transaction_id}")
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db)
):

    transaction = db.query(FinanceTransaction).filter(
        FinanceTransaction.id == transaction_id
    ).first()

    if not transaction:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    db.delete(transaction)
    db.commit()

    return {
        "message": "Transaction deleted successfully",
        "transaction_id": transaction_id
    }

# FINANCIAL SUMMARY
@router.get("/summary")
def get_financial_summary(
    month: int,
    year: int,
    db: Session = Depends(get_db)
):

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

    # Calculate monthly income
    total_income = db.query(
        func.coalesce(func.sum(FinanceTransaction.amount), 0)
    ).filter(
        FinanceTransaction.transaction_type == "income",
        func.extract(
            "month",
            FinanceTransaction.transaction_date
        ) == month,
        func.extract(
            "year",
            FinanceTransaction.transaction_date
        ) == year
    ).scalar()

    # Calculate monthly expense
    total_expense = db.query(
        func.coalesce(func.sum(FinanceTransaction.amount), 0)
    ).filter(
        FinanceTransaction.transaction_type == "expense",
        func.extract(
            "month",
            FinanceTransaction.transaction_date
        ) == month,
        func.extract(
            "year",
            FinanceTransaction.transaction_date
        ) == year
    ).scalar()

    # Calculate transaction count
    transaction_count = db.query(
        func.count(FinanceTransaction.id)
    ).filter(
        func.extract(
            "month",
            FinanceTransaction.transaction_date
        ) == month,
        func.extract(
            "year",
            FinanceTransaction.transaction_date
        ) == year
    ).scalar()

    # Calculate expenses by category
    category_results = db.query(
        FinanceTransaction.category,
        func.sum(FinanceTransaction.amount).label("total")
    ).filter(
        FinanceTransaction.transaction_type == "expense",
        func.extract(
            "month",
            FinanceTransaction.transaction_date
        ) == month,
        func.extract(
            "year",
            FinanceTransaction.transaction_date
        ) == year
    ).group_by(
        FinanceTransaction.category
    ).all()

    total_income = int(total_income or 0)
    total_expense = int(total_expense or 0)

    net_balance = total_income - total_expense

    expenses_by_category = [
        {
            "category": item.category,
            "total": int(item.total)
        }
        for item in category_results
    ]

    return {
        "period": {
            "month": month,
            "year": year
        },
        "total_income": total_income,
        "total_expense": total_expense,
        "net_balance": net_balance,
        "transaction_count": transaction_count,
        "expenses_by_category": expenses_by_category
    }
