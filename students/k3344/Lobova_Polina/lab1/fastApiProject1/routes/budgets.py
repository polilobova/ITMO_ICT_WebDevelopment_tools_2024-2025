from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List
from db import get_session
import crud, schemas
from routes.auth import get_current_user
from models import User

router = APIRouter(prefix="/budgets", tags=["budgets"])

@router.get("/", response_model=List[schemas.BudgetRead])
def read_budgets(db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    return crud.get_budgets_for_user(db, current_user.id)

@router.post("/", response_model=schemas.BudgetRead)
def create_budget(budget: schemas.BudgetCreate, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    return crud.create_budget(db, current_user.id, budget.month, budget.limit, budget.category_id)

@router.put("/{budget_id}", response_model=schemas.BudgetRead)
def update_budget(budget_id: int, budget: schemas.BudgetCreate, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    updated = crud.update_budget(db, budget_id, budget.limit)
    if not updated:
        raise HTTPException(status_code=404, detail="Budget not found")
    return updated

@router.delete("/{budget_id}", status_code=204)
def delete_budget(budget_id: int, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    crud.delete_budget(db, budget_id)
    return