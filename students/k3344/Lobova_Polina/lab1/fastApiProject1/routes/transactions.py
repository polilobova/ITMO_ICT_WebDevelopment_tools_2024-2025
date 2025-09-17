from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from sqlalchemy.orm import selectinload

from db import get_session
import crud
from routes.auth import get_current_user
from models import Transaction, User, TransactionCategoryLink
from schemas import TransactionCreate, TransactionRead

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.get("/", response_model=List[TransactionRead])
def read_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    statement = (
        select(Transaction)
        .where(Transaction.user_id == current_user.id)
        .options(selectinload(Transaction.categories))  # Вот это важно!
    )
    transactions = db.exec(statement).all()
    return transactions

@router.post("/", response_model=TransactionRead)
def create_transaction(
    transaction: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    db_transaction = Transaction(
        amount=transaction.amount,
        is_income=transaction.is_income,
        description=transaction.description,
        user_id=current_user.id
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)

    for category_id in transaction.category_ids:
        link = TransactionCategoryLink(transaction_id=db_transaction.id, category_id=category_id)
        db.add(link)

    db.commit()
    db.refresh(db_transaction)

    return db_transaction

@router.get("/{transaction_id}", response_model=TransactionRead)
def read_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    statement = (
        select(Transaction)
        .where(Transaction.id == transaction_id, Transaction.user_id == current_user.id)
        .options(selectinload(Transaction.categories))
    )
    transaction = db.exec(statement).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@router.delete("/{transaction_id}", status_code=204)
def delete_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    transaction = crud.get_transaction_by_id(db, transaction_id)
    if not transaction or transaction.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Transaction not found")
    crud.delete_transaction(db, transaction_id)
    return

@router.put("/{transaction_id}", response_model=TransactionRead)
def update_transaction(
    transaction_id: int,
    transaction: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    db_transaction = crud.get_transaction_by_id(db, transaction_id)
    if not db_transaction or db_transaction.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Transaction not found")
    updated = crud.update_transaction(
        db,
        transaction_id,
        amount=transaction.amount,
        is_income=transaction.is_income,
        description=transaction.description,
        category_ids=transaction.category_ids,
    )
    return updated