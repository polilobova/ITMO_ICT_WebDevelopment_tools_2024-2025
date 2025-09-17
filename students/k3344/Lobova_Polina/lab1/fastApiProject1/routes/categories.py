from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List
from db import get_session
import crud, schemas
from routes.auth import get_current_user
from models import User

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("/", response_model=List[schemas.CategoryRead])
def read_categories(db: Session = Depends(get_session)):
    return crud.get_categories(db)

@router.post("/", response_model=schemas.CategoryRead)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    return crud.create_category(db, category.name)

@router.put("/{category_id}", response_model=schemas.CategoryRead)
def update_category(category_id: int, category: schemas.CategoryCreate, db: Session = Depends(get_session)):
    updated = crud.update_category(db, category_id, category.name)
    if not updated:
        raise HTTPException(status_code=404, detail="Category not found")
    return updated

@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_session)):
    crud.delete_category(db, category_id)
    return {"message": "Category deleted"}