
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

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
