from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List
from db import get_session
import crud, schemas
from routes.auth import get_current_user
from models import User

router = APIRouter(prefix="/goals", tags=["goals"])

@router.get("/", response_model=List[schemas.GoalRead])
def read_goals(db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    return crud.get_goals_for_user(db, current_user.id)

@router.post("/", response_model=schemas.GoalRead)
def create_goal(goal: schemas.GoalCreate, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    return crud.create_goal(db, current_user.id, goal.title, goal.target_amount, goal.deadline)

@router.put("/{goal_id}", response_model=schemas.GoalRead)
def update_goal(goal_id: int, current_amount: float, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    updated = crud.update_goal(db, goal_id, current_amount)
    if not updated:
        raise HTTPException(status_code=404, detail="Goal not found")
    return updated

@router.delete("/{goal_id}", status_code=204)
def delete_goal(goal_id: int, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    crud.delete_goal(db, goal_id)
    return